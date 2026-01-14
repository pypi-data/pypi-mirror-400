"""
简化版文本纠错组件

继承自BaseLLMComponent，提供并行文本纠错功能
"""

import difflib
from typing import List, Dict, Any, Callable, Optional, Tuple, Literal

import jieba
from pydantic import BaseModel, Field

from duowen_agent.agents.component.base import BaseLLMComponent
from duowen_agent.llm.chat_model import BaseAIChat
from duowen_agent.utils.concurrency import concurrent_execute, ProgressBar
from duowen_agent.utils.core_utils import remove_think, stream_to_string
from duowen_agent.utils.string_template import StringTemplate


class Edits(BaseModel):
    start_pos: int = Field(..., description="原文字符起始字符位置")
    end_pos: int = Field(..., description="原文字符结束字符位置")
    src: str = Field(..., description="原字符")
    tgt: str = Field(..., description="修正字符")
    edit_type: Literal["replace", "insert", "delete"] = Field(
        ..., description="编辑操作类型"
    )

    @classmethod
    def create_from_diff(
        cls, start_pos: int, end_pos: int, src: str, tgt: str
    ) -> "Edits":
        """根据差异信息创建编辑对象，自动判断编辑类型"""
        if not src and tgt:
            edit_type = "insert"
        elif src and not tgt:
            edit_type = "delete"
        else:
            edit_type = "replace"

        return cls(
            start_pos=start_pos, end_pos=end_pos, src=src, tgt=tgt, edit_type=edit_type
        )

    def to_dict(self):
        """转换为字典格式，便于前端使用"""
        return {
            "start_pos": self.start_pos,
            "end_pos": self.end_pos,
            "src": self.src,
            "tgt": self.tgt,
            "edit_type": self.edit_type,
            "length": len(self.src),
            "new_length": len(self.tgt),
        }


class TextCorrectorResult(BaseModel):
    source: str = Field(default=None, description="原始文本内容")
    edits: Optional[List[Edits]] = Field(..., description="无修改记录保持空数组状态")
    target: str = Field(default=None, description="完整修正文本")

    def get_edit_summary(self) -> Dict[str, Any]:
        """获取编辑操作的统计摘要"""
        if not self.edits:
            return {
                "total_edits": 0,
                "replace_count": 0,
                "insert_count": 0,
                "delete_count": 0,
                "total_chars_changed": 0,
            }

        summary = {
            "total_edits": len(self.edits),
            "replace_count": sum(
                1 for edit in self.edits if edit.edit_type == "replace"
            ),
            "insert_count": sum(1 for edit in self.edits if edit.edit_type == "insert"),
            "delete_count": sum(1 for edit in self.edits if edit.edit_type == "delete"),
            "total_chars_changed": sum(len(edit.src) for edit in self.edits),
        }

        return summary

    def to_dict(self):
        """转换为字典格式，包含详细的编辑信息"""
        return {
            "source": self.source,
            "target": self.target,
            "edits": [edit.to_dict() for edit in (self.edits or [])],
            "edit_summary": self.get_edit_summary(),
        }


class TextCorrector(BaseLLMComponent):
    """简化版文本纠错组件"""

    def __init__(
        self,
        llm_instance: BaseAIChat,
        pre_len_size: int = 120,
        after_len_size: int = 120,
        max_chunk_length: int = 512,
        work_num: int = 4,
        call_back_func: Optional[Callable] = None,
        interrupt_func: Optional[Callable] = None,
        prompt_template: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(llm_instance, **kwargs)
        self.llm_instance.temperature = 0
        self.pre_len_size = pre_len_size
        self.after_len_size = after_len_size
        self.max_chunk_length = max_chunk_length
        self.work_num = work_num
        self.call_back_func = call_back_func or (lambda x: True)
        self.interrupt_func = interrupt_func or (lambda: False)

        self.pb = ProgressBar(total=0, message="文本纠错进度")

        self.prompt = StringTemplate(
            prompt_template
            or """
作为专业文本纠错助手，仅针对指定目标文本进行语法、用词、标点、大小写等错误修正，不新增 / 删减原文语义，不修改非目标内容。

输入包含三个部分：

1. <before>：待纠错文本的前部分，提供上下文参考
2. <target>：待纠错文本，这是需要进行纠错的目标文本  
3. <after>：待纠错文本的后部分，提供上下文参考  


### Few-shot 示例:

输入：  
<before>
以下是实习报告的部分内容：
</before>

<target>
    我在公司里主要负责数据分析,和报表的制作。
在这个过程钟，我学习了如何使用excel和python。
同时，我也参与了一个客护满意度调查项目，
负责收集并整理用户的反馈意见。
</target>

<after>
以上是第一周的工作总结。
</after>

输出：

<corrected>
    我在公司里主要负责数据分析和报表的制作。
在这个过程中，我学习了如何使用Excel和Python。
同时，我也参与了一个客户满意度调查项目，
负责收集并整理用户的反馈意见。
</corrected>


### Real Data

<before>
{{before}}
</before>

<target>
{{target}}
</target>

<after>
{{after}}
</after>


要求：  
- **严格限制**：只纠错 <target> 部分，绝对不能包含 <before> 或 <after> 的任何内容。
- **输出长度**：输出内容的长度应该与 <target> 部分相近，不能明显过长。
- **内容边界**：输出必须严格对应 <target> 的开始和结束，不能延伸到上下文。
- **保持原有的文本格式**（换行、缩进、标点、大小写等），不要输出多余解释。  
- **输出格式**：将纠错后的文本放在 <corrected>...</corrected> 标签内，不包含前后部分，也不包含额外说明。  
- 不修改未出现错误的部分。
""",
            template_format="jinja2",
        )

    @staticmethod
    def _needs_correction(text: str) -> bool:
        """判断文本是否需要纠错（包含中文或英文）"""
        if not text.strip():
            return False
        return any(
            "\u4e00" <= c <= "\u9fff" or (c.isalpha() and c.isascii()) for c in text
        )

    @staticmethod
    def _clean_model_output(text: str) -> tuple[str, bool]:
        """清理模型输出，提取XML标签内的内容

        Args:
            text: 模型原始输出

        Returns:
            tuple: (清理后的文本, 是否找到XML标签)
        """
        if not text:
            return text, False

        import re

        # 提取 <corrected>...</corrected> 标签内的内容
        match = re.search(r"<corrected>\s*(.*?)\s*</corrected>", text, flags=re.DOTALL)
        if not match:
            return text.strip(), False

        corrected = match.group(1).strip()
        return corrected, True

    @staticmethod
    def _validate_content_boundary(
        corrected: str, target: str, before: str = "", after: str = ""
    ) -> tuple[bool, str, str]:
        """使用difflib分析差异，验证是否为合理的文本纠错

        文本纠错应该是小幅修改，不应该有大段的插入、删除或替换

        Returns:
            tuple: (是否通过验证, 清理后的文本, 失败原因)
        """
        if not corrected or not target:
            return True, corrected, ""

        corrected = corrected.strip()
        target = target.strip()

        # 1. 基本长度检查：防止极端情况
        if len(corrected) < len(target) * 0.3:  # 不能缩短超过70%
            reason = f"输出过短: {len(corrected)}字符，原文{len(target)}字符，缩短了{(1-len(corrected)/len(target))*100:.1f}%"
            return False, corrected, reason
        elif len(corrected) > len(target) * 2.5:  # 不能增长超过150%
            reason = f"输出过长: {len(corrected)}字符，原文{len(target)}字符，增长了{(len(corrected)/len(target)-1)*100:.1f}%"
            return False, corrected, reason

        # 2. 使用difflib分析字符级差异
        s = difflib.SequenceMatcher(None, target, corrected)

        # 统计各种操作的字符数
        total_chars = len(target)
        insert_chars = 0
        delete_chars = 0
        replace_chars = 0

        large_operations = []  # 记录大段操作

        for tag, i1, i2, j1, j2 in s.get_opcodes():
            if tag == "insert":
                insert_chars += j2 - j1
                if j2 - j1 > 20:  # 大段插入（超过20字符）
                    inserted_text = corrected[j1:j2]
                    large_operations.append(
                        f"大段插入({j2-j1}字符): '{inserted_text[:30]}...'"
                    )

            elif tag == "delete":
                delete_chars += i2 - i1
                if i2 - i1 > 20:  # 大段删除（超过20字符）
                    deleted_text = target[i1:i2]
                    large_operations.append(
                        f"大段删除({i2-i1}字符): '{deleted_text[:30]}...'"
                    )

            elif tag == "replace":
                replace_chars += max(i2 - i1, j2 - j1)
                if max(i2 - i1, j2 - j1) > 20:  # 大段替换（超过20字符）
                    original_text = target[i1:i2]
                    new_text = corrected[j1:j2]
                    large_operations.append(
                        f"大段替换({max(i2-i1, j2-j1)}字符): '{original_text[:15]}...' → '{new_text[:15]}...'"
                    )

        # 3. 检查是否有大段操作（文本纠错不应该有大段修改）
        if large_operations:
            reason = f"检测到非纠错性质的大段修改: {'; '.join(large_operations[:2])}"  # 只显示前2个
            return False, corrected, reason

        # 4. 检查总体修改比例
        total_changes = insert_chars + delete_chars + replace_chars
        change_ratio = total_changes / max(total_chars, 1)

        if change_ratio > 0.6:  # 如果修改超过60%的内容，可能不是纠错
            reason = f"修改比例过高: {change_ratio*100:.1f}% (插入{insert_chars}字符, 删除{delete_chars}字符, 替换{replace_chars}字符)"
            return False, corrected, reason

        # 5. 检查是否包含上下文内容（简化版）
        # 只检查明显的长字符串泄露（30字符以上）
        if len(corrected) >= 30:
            for i in range(len(corrected) - 29):
                substr = corrected[i : i + 30]
                # 如果这个长字符串在目标中不存在，但在上下文中存在
                if substr not in target:
                    if (before and substr in before) or (after and substr in after):
                        reason = f"检测到上下文内容泄露: '{substr[:40]}...'"
                        return False, corrected, reason

        return True, corrected, ""

    @staticmethod
    def _validate_word_level_similarity(
        original: str, corrected: str, max_word_change_ratio: float = 0.5
    ) -> bool:
        """基于jieba分词验证词级别的相似度"""
        if not original.strip() or not corrected.strip():
            return True

        # 分词并计算词级别相似度
        original_words = list(jieba.cut(original.strip()))
        corrected_words = list(jieba.cut(corrected.strip()))

        # 对于很短的文本（词数<=2），使用更宽松的策略
        if len(original_words) <= 2 and len(corrected_words) <= 2:
            # 单词对单词的替换，如果长度相近则允许
            if abs(len(original_words) - len(corrected_words)) <= 1:
                return True
            max_word_change_ratio = 0.9  # 短文本允许更大的变化

        s = difflib.SequenceMatcher(None, original_words, corrected_words)
        word_similarity = s.ratio()

        return word_similarity >= (1 - max_word_change_ratio)

    def _get_chunk_context(
        self, lines: List[str], start_idx: int, end_idx: int
    ) -> Tuple[str, str]:
        """获取块的前后上下文（按字符数）"""
        # 获取前文内容（基于块的开始位置，按字符数截取）
        before_lines = lines[:start_idx]
        before_text = "\n".join(before_lines) if before_lines else ""
        before = (
            before_text[-self.pre_len_size :]
            if len(before_text) > self.pre_len_size
            else before_text
        )

        # 获取后文内容（基于块的结束位置，按字符数截取）
        after_lines = lines[end_idx + 1 :]
        after_text = "\n".join(after_lines) if after_lines else ""
        after = (
            after_text[: self.after_len_size]
            if len(after_text) > self.after_len_size
            else after_text
        )

        return before, after

    def _preserve_format(self, original: str, corrected: str) -> str:
        """保持原行格式"""
        if not original.strip():
            return original

        # 提取格式信息
        leading = len(original) - len(original.lstrip())
        trailing = len(original) - len(original.rstrip())

        if not corrected.strip():
            return original

        # 重建格式
        prefix = original[:leading]
        suffix = original[-trailing:] if trailing > 0 else ""

        return prefix + corrected.strip() + suffix

    def _correct_line(self, **chunk_data) -> Dict[str, Any]:
        """纠错文本块"""
        if self.interrupt_func():
            raise InterruptedError("用户中断")

        # 显示进度
        self.call_back_func(self.pb.log_msg())

        # 检查是否需要纠错
        if not self._needs_correction(chunk_data["text"]):
            self.pb.increment()
            self.pb.show()
            return {"corrected": chunk_data["text"], "success": True}

        try:
            # 格式化提示词
            prompt_input = self.prompt.format(
                before=chunk_data["before"],
                target=chunk_data["text"],
                after=chunk_data["after"],
            )

            # 重试机制：最多重试3次
            max_retries = 3
            for attempt in range(max_retries + 1):
                # LLM纠错
                raw_output = remove_think(
                    stream_to_string(self.llm_instance.chat_for_stream(prompt_input))
                ).strip()

                # 清理模型输出，检查是否找到XML标签
                corrected, found_xml = self._clean_model_output(raw_output)

                # 检查是否找到XML标签
                if not found_xml:
                    if attempt == max_retries:
                        chunk_info = f"块{chunk_data['chunk_num']}(行{chunk_data['start_line']}-{chunk_data['end_line']})"
                        self.call_back_func(
                            f"{chunk_info} 重试{max_retries}次后仍未找到XML格式，使用原文"
                        )
                        corrected = chunk_data["text"]
                        break
                    else:
                        chunk_info = f"块{chunk_data['chunk_num']}(行{chunk_data['start_line']}-{chunk_data['end_line']})"
                        self.call_back_func(
                            f"{chunk_info} 第{attempt + 1}次未找到XML格式，重试中..."
                        )
                        continue

                # 验证内容边界，防止包含上下文内容
                boundary_valid, cleaned_corrected, boundary_reason = (
                    self._validate_content_boundary(
                        corrected,
                        chunk_data["text"],
                        chunk_data["before"],
                        chunk_data["after"],
                    )
                )

                if not boundary_valid:
                    if attempt == max_retries:
                        chunk_info = f"块{chunk_data['chunk_num']}(行{chunk_data['start_line']}-{chunk_data['end_line']})"
                        self.call_back_func(
                            f"{chunk_info} 重试{max_retries}次后内容边界仍不合理，使用原文。原因: {boundary_reason}"
                        )
                        corrected = chunk_data["text"]
                        break
                    else:
                        chunk_info = f"块{chunk_data['chunk_num']}(行{chunk_data['start_line']}-{chunk_data['end_line']})"
                        self.call_back_func(
                            f"{chunk_info} 第{attempt + 1}次内容边界不合理，重试中... 原因: {boundary_reason}"
                        )
                        continue

                # 使用清理后的内容
                corrected = cleaned_corrected

                # 验证文本差异是否合理（所有文本都需要完整验证）
                if not self._validate_word_level_similarity(
                    chunk_data["text"], corrected
                ):
                    if attempt == max_retries:
                        chunk_info = f"块{chunk_data['chunk_num']}(行{chunk_data['start_line']}-{chunk_data['end_line']})"
                        self.call_back_func(
                            f"{chunk_info} 重试{max_retries}次后修改差异仍过大，使用原文"
                        )
                        corrected = chunk_data["text"]
                        break
                    else:
                        chunk_info = f"块{chunk_data['chunk_num']}(行{chunk_data['start_line']}-{chunk_data['end_line']})"
                        self.call_back_func(
                            f"{chunk_info} 第{attempt + 1}次修改差异过大，重试中..."
                        )
                        continue

                # XML格式正确且差异合理，跳出重试循环
                break

            # 如果清理后为空或无效，使用原文
            if not corrected or corrected == chunk_data["text"]:
                corrected = chunk_data["text"]

            # 保持格式
            result = self._preserve_format(chunk_data["text"], corrected)

            return {"corrected": result, "success": True}

        except Exception as e:
            chunk_info = f"块{chunk_data['chunk_num']}(行{chunk_data['start_line']}-{chunk_data['end_line']})"
            self.call_back_func(f"{chunk_info} 纠错失败: {e}")
            return {"corrected": chunk_data["text"], "success": False}

        finally:
            self.pb.increment()
            self.pb.show()

    def _split_text(self, text: str) -> List[Dict[str, Any]]:
        """智能分割文本为块，合并短行以提高处理效率"""
        lines = text.split("\n")
        chunks = []
        i = 0

        while i < len(lines):
            # 开始一个新的块
            chunk_lines = [lines[i]]
            chunk_start_idx = i
            current_length = len(lines[i])

            # 尝试添加更多行，直到达到长度限制
            j = i + 1
            while (
                j < len(lines)
                and current_length + len(lines[j]) + 1 <= self.max_chunk_length
            ):
                chunk_lines.append(lines[j])
                current_length += len(lines[j]) + 1  # +1 for newline
                j += 1

            # 确保至少包含一行（即使超过长度限制）
            if j == i + 1 and len(chunk_lines) == 1:
                j = i + 1

            chunk_end_idx = j - 1
            chunk_text = "\n".join(chunk_lines)

            # 计算这个块的前后上下文
            before, after = self._get_chunk_context(
                lines, chunk_start_idx, chunk_end_idx
            )

            chunks.append(
                {
                    "chunk_num": len(chunks) + 1,
                    "text": chunk_text,
                    "before": before,
                    "after": after,
                    "start_line": chunk_start_idx + 1,
                    "end_line": chunk_end_idx + 1,
                    "line_count": len(chunk_lines),
                }
            )

            i = j

        return chunks

    def _calculate_edits(
        self, original_lines: List[str], corrected_lines: List[str]
    ) -> List[Edits]:
        """计算编辑差异，返回Edits列表

        使用更精确的算法来计算字符级别的编辑操作，
        能够正确处理跨行变化、行插入/删除等复杂情况
        """
        edits = []

        # 重建完整文本以进行全局差异计算
        original_text = "\n".join(original_lines)
        corrected_text = "\n".join(corrected_lines)

        # 如果文本完全相同，直接返回空编辑列表
        if original_text == corrected_text:
            return edits

        # 使用difflib进行全局文本差异计算
        s = difflib.SequenceMatcher(None, original_text, corrected_text)

        for tag, i1, i2, j1, j2 in s.get_opcodes():
            if tag != "equal":
                # 提取原始文本和修正文本片段
                src_text = original_text[i1:i2]
                tgt_text = corrected_text[j1:j2]

                # 创建编辑操作，自动判断类型
                edit = Edits.create_from_diff(
                    start_pos=i1,
                    end_pos=i2,
                    src=src_text,
                    tgt=tgt_text,
                )
                edits.append(edit)

        return edits

    def run(self, text: str, **kwargs) -> TextCorrectorResult:
        """运行方法（继承自BaseLLMComponent）- 主要入口"""
        # 分割文本
        chunk_data = self._split_text(text)
        self.pb.total = len(chunk_data)

        verbose = kwargs.get("verbose", True)
        if verbose:
            self.call_back_func(
                f"分割为 {len(chunk_data)} 个块，使用 {self.work_num} 个线程处理"
            )

        # 并行处理
        try:
            results = concurrent_execute(
                self._correct_line, chunk_data, work_num=self.work_num
            )
        except Exception as e:
            self.call_back_func(f"处理失败: {e}")
            return TextCorrectorResult(
                source=text,
                edits=[],
                target=text,
            )

        # 处理结果
        corrected_chunks = []
        successful = 0

        for result in results:
            corrected_chunks.append(result["corrected"])
            if result["success"]:
                successful += 1

        corrected_text = "\n".join(corrected_chunks)

        # 计算编辑差异
        original_lines = text.split("\n")
        corrected_lines = corrected_text.split("\n")
        edits = self._calculate_edits(original_lines, corrected_lines)

        # 创建结果对象
        result = TextCorrectorResult(
            source=text,
            edits=edits,
            target=corrected_text,
        )

        if verbose:
            summary = result.get_edit_summary()
            self.call_back_func(
                f"完成: 成功处理 {successful} 个块, 发现 {summary['total_edits']} 个编辑操作 "
                f"(替换:{summary['replace_count']}, 插入:{summary['insert_count']}, 删除:{summary['delete_count']})"
            )

        return result
