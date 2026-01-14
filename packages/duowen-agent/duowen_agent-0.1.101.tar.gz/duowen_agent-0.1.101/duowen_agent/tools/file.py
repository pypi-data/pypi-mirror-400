import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from duowen_agent.agents.state import Resources
from duowen_agent.error import ToolError
from duowen_agent.llm import OpenAIChat, tokenizer, MessagesSet
from duowen_agent.tools.base import BaseTool, BaseToolResult
from duowen_agent.utils.core_utils import stream_to_string, remove_think
from duowen_agent.utils.string_template import StringTemplate


def file_path_repair(file_path):
    if file_path.startswith("/workspace/"):
        return file_path
    elif file_path.startswith("/") and not file_path.startswith("/workspace/"):
        raise ToolError("文件路径必须以 /workspace/ 开头")
    else:
        return "/workspace/" + file_path


class FileToolResult(BaseToolResult):
    status_msg: str
    file_content: Optional[str] = None

    def to_str(self) -> str:
        return self.status_msg

    def to_view(self) -> str:

        if self.status_msg and not self.file_content:
            return self.status_msg

        if self.file_content is not None:
            if self.file_content == self.status_msg:
                return self.status_msg
            else:
                return f"> {self.status_msg}\n\n{self.file_content}"

        return self.status_msg


class CreateFileParams(BaseModel):
    file_path: str = Field(
        description="Path to the file to be created, relative to /workspace (e.g., 'src/main.py')"
    )
    content: str = Field(description="The content to write to the file")
    permissions: Optional[str] = Field(
        description="File permissions in octal format (e.g., '644')", default="644"
    )


class CreateFile(BaseTool):
    name: str = "create-file"
    description: str = (
        "Create a new file with the provided contents at a given path in the workspace. The path must be relative to /workspace (e.g., 'src/main.py' for /workspace/src/main.py)"
    )
    parameters = CreateFileParams

    def __init__(self, resources: Resources, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resources = resources

    def _run(self, file_path, content, permissions="644") -> FileToolResult:
        _file_path = file_path_repair(file_path)
        self.resources.file_add(_file_path, content, permissions)
        return FileToolResult(
            status_msg=f"File '{_file_path}' created successfully.",
            file_content=self.resources.read_all_file(_file_path),
        )


class FileStrReplaceParams(BaseModel):
    file_path: str = Field(
        description="Path to the target file, relative to /workspace (e.g., 'src/main.py')"
    )
    old_str: str = Field(description="Text to be replaced (must appear exactly once)")
    new_str: str = Field(description="Replacement text")


class FileStrReplace(BaseTool):
    name: str = "file-str-replace"
    description: str = (
        "Replace specific text in a file. The file path must be relative to /workspace (e.g., 'src/main.py' for /workspace/src/main.py). Use this when you need to replace a unique string that appears exactly once in the file."
    )
    parameters = FileStrReplaceParams

    def __init__(self, resources: Resources, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resources = resources

    def _run(self, file_path, old_str, new_str) -> FileToolResult:
        _file_path = file_path_repair(file_path)
        if not self.resources.file_exists(_file_path):
            return FileToolResult(status_msg=f"文件 '{_file_path}' 不存在.")
        if self.resources.file_str_replace(_file_path, old_str, new_str):
            return FileToolResult(
                status_msg=f"替换文件 '{_file_path}' 内容成功",
                file_content=self.resources.read_all_file(_file_path),
            )
        else:
            return FileToolResult(
                status_msg=f"内容 '{old_str}' 未在文件内 '{_file_path}'发现."
            )


class FileFullRewriteParams(BaseModel):
    file_path: str = Field(
        description="Path to the file to be rewritten, relative to /workspace (e.g., 'src/main.py')"
    )
    content: str = Field(
        description="The new content to write to the file, replacing all existing content"
    )
    permissions: Optional[str] = Field(
        description="File permissions in octal format (e.g., '644')", default="644"
    )


class FileFullRewrite(BaseTool):
    name: str = "file-full-rewrite"
    description: str = (
        "Completely rewrite an existing file with new content. The file path must be relative to /workspace (e.g., 'src/main.py' for /workspace/src/main.py). Use this when you need to replace the entire file content or make extensive changes throughout the file."
    )
    parameters = FileFullRewriteParams

    def __init__(self, resources: Resources, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resources = resources

    def _run(self, file_path, content, permissions="664") -> FileToolResult:
        _file_path = file_path_repair(file_path)
        if not self.resources.file_exists(_file_path):
            return FileToolResult(status_msg=f"文件 '{_file_path}' 不存在.")
        self.resources.file_full_rewrite(_file_path, content, permissions)
        return FileToolResult(
            status_msg=f"文件 '{_file_path}' 完全重写成功.",
            file_content=self.resources.read_all_file(_file_path),
        )


class FileDeleteParams(BaseModel):
    file_path: str = Field(
        description="Path to the file to be deleted, relative to /workspace (e.g., 'src/main.py')"
    )


class FileDelete(BaseTool):
    name: str = "file-delete"
    description: str = (
        "Delete a file at the given path. The path must be relative to /workspace (e.g., 'src/main.py' for /workspace/src/main.py)"
    )
    parameters = FileDeleteParams

    def __init__(self, resources: Resources, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resources = resources

    def _run(self, file_path) -> FileToolResult:
        _file_path = file_path_repair(file_path)
        if not self.resources.file_exists(_file_path):
            return FileToolResult(status_msg=f"文件 '{_file_path}' 不存在.")
        self.resources.file_delete(_file_path)
        return FileToolResult(status_msg=f"文件 '{_file_path}' 删除成功.")


class GrepFileParams(BaseModel):
    file_path: str = Field(
        description="Path to the file to search in, relative to /workspace (e.g., 'src/main.py')"
    )
    pattern: str = Field(description="The pattern to search for (regular expression)")
    max_results: Optional[int] = Field(
        description="Maximum number of results to return (default: 20)", default=20
    )


class GrepFile(BaseTool):
    name: str = "grep-file"
    description: str = (
        "Search for a pattern in a file using regular expressions. The file path must be relative to /workspace (e.g., 'src/main.py' for /workspace/src/main.py). Returns matching lines with line numbers."
    )
    parameters = GrepFileParams

    def __init__(self, resources: Resources, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resources = resources

    def _run(self, file_path, pattern, max_results=20) -> FileToolResult:
        _file_path = file_path_repair(file_path)
        if not self.resources.file_exists(_file_path):
            return FileToolResult(status_msg=f"文件 '{_file_path}' 不存在.")

        # 读取文件内容
        file_content = self.resources.read_all_file(_file_path)
        lines = file_content.split("\n")

        # 搜索匹配行
        matches = []
        for line_num, line in enumerate(lines, 1):  # 使用 enumerate 获取行号，从1开始
            if re.search(pattern, line):
                matches.append(f"行 {line_num}: {line}")  # 这里包含了行号信息
                if len(matches) >= max_results:
                    break

        if not matches:
            return FileToolResult(
                status_msg=StringTemplate(
                    "在文件 '{{file_path}}' 中未找到模式 `{{pattern}}` 的匹配项。",
                    template_format="jinja2",
                ).format(file_path=_file_path, pattern=pattern)
            )

        result = StringTemplate(
            "在文件 '{{file_path}}' 中找到 {{len_matches}} 个匹配模式 `{{pattern}}` 的结果:\n\n",
            template_format="jinja2",
        ).format(file_path=_file_path, pattern=pattern, len_matches=len(matches))
        result += "\n".join(matches)  # 这里会显示所有匹配行及其行号

        if len(matches) == max_results:
            result += (
                f"\n\n(显示前 {max_results} 个结果，使用 max_results 参数查看更多)"
            )

        return FileToolResult(status_msg=result)


class FileReadParams(BaseModel):
    file_path: str = Field(
        description="Path to the file to be read, relative to /workspace (e.g.,'src/main.py')"
    )
    start_line: int = Field(description="Start line number to read from")
    end_line: int = Field(description="End line number to read to")


class FileRead(BaseTool):
    name: str = "file-read"
    description: str = (
        "Read a file at the given path. The path must be relative to /workspace (e.g.,'src/main.py' for /workspace/src/main.py)"
    )
    parameters = FileReadParams

    def __init__(
        self, resources: Resources, read_token_limit: int = 4000, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.resources = resources
        self.read_token_limit = read_token_limit

    def _run(self, file_path, start_line, end_line) -> FileToolResult:
        _file_path = file_path_repair(file_path)
        if not self.resources.file_exists(_file_path):
            return FileToolResult(status_msg=f"文件 '{_file_path}' 不存在.")
        data = self.resources.read_file(_file_path, start_line, end_line)

        if tokenizer.chat_len(data["content"]) <= self.read_token_limit:

            return FileToolResult(
                status_msg=f"""读取文件 {_file_path}
                
文件开始行号: {data["start_line"]}, 文件结束行号: {data["end_line"]}, 文件总行数: {data["total_lines"]}

文件内容: {data["content"]}
"""
            )
        else:
            return FileToolResult(
                status_msg=f"文件 '{_file_path}'的读取方式 start_line: {start_line}, end_line: {end_line} 导致读取内容超过工具最大 {self.read_token_limit} tokens 限制，请缩小范围."
            )


class AskFileParams(BaseModel):
    file_path: str = Field(
        description="Path to the file to be read, relative to /workspace (e.g.,'src/main.py')"
    )
    question: str = Field(description="The question to ask about the file")


class AskFile(BaseTool):
    name: str = "ask-file"
    description: str = (
        "Ask a question about a file at the given path. The path must be relative to /workspace (e.g.,'src/main.py' for /workspace/src/main.py)"
    )
    parameters = AskFileParams

    def __init__(self, resources: Resources, llm: OpenAIChat, **kwargs):
        super().__init__(**kwargs)
        self.resources = resources
        self.llm = llm

    def _run(self, file_path, question) -> FileToolResult:
        _file_path = file_path_repair(file_path)
        if not self.resources.file_exists(_file_path):
            return FileToolResult(status_msg=f"文件 '{_file_path}' 不存在.")

        data = self.resources.read_all_file(_file_path)
        if tokenizer.chat_len(data) <= (self.llm.token_limit - 20000):
            _prompt = MessagesSet()

            _prompt.add_user(
                StringTemplate(
                    """
你是一个专业的智能信息检索助手，犹如专业的高级秘书，依据检索到的信息回答用户问题。
当用户提出问题时，助手只能基于给定的信息进行解答，不能利用任何先验知识。

## 回答问题规则
- 仅根据检索到的信息中的事实进行回复，不得运用任何先验知识，保持回应的客观性和准确性。
- 复杂问题和答案的按Markdown分结构展示，总述部分不需要拆分
- 如果是比较简单的答案，不需要把最终答案拆分的过于细碎
- 结果中使用的url地址必须来自于检索到的信息，不得虚构
- 检查结果中的文字和图片是否来自于检索到的信息，如果扩展了不在检索到的信息中的内容，必须进行修改，直到得到最终答案


## 输出限制
- 以Markdown格式输出你的最终结果
- 输出内容要保证简短且全面，条理清晰，信息明确，不重复。

## 当前时间是：
{{CurrentTime}} {{CurrentWeek}}

## 检索到的信息如下：
------BEGIN------
{{data}}
------END------

## 用户当前的问题是：
{{question}}
""",
                    template_format="jinja2",
                ).format(
                    CurrentTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    CurrentWeek=datetime.now().strftime("%A"),
                    data=data,
                    question=question,
                )
            )
            _prompt.add_user(question)
            res = stream_to_string(self.llm.chat_for_stream(_prompt))
            return FileToolResult(status_msg=remove_think(res))
        else:
            return FileToolResult(status_msg=f"文件 '{_file_path}' 内容过长，无法读取.")
