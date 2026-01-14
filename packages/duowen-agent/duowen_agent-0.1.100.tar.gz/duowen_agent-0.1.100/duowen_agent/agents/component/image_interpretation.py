"""
图片解析模块 (Image Interpretation)

基于多模态模型的智能图片内容提取，支持：
1. 图片类型自动分类 (ImageClassifier)
2. 根据分类结果动态拼接提示词进行内容提取 (ImageExtractor)

典型用例:
    from duowen_agent.agents.component.image_interpretation import (
        ImageElementRegistry,
        ImageClassifier,
        ImageExtractor,
    )
    
    # 加载元素类型注册表
    registry = ImageElementRegistry.load()
    
    # 创建分类器和提取器
    classifier = ImageClassifier(llm_instance)
    extractor = ImageExtractor(llm_instance, registry)
    
    # 分类图片类型
    types = classifier.run(image_content)
    
    # 提取内容
    result = extractor.run(image_content, types)
"""

import os
from pathlib import Path
from typing import List, Dict, Optional, Union

import yaml
from pydantic import BaseModel, Field

from duowen_agent.agents.component.base import BaseLLMComponent
from duowen_agent.error import ObserverException
from duowen_agent.llm.chat_model import BaseAIChat
from duowen_agent.llm.entity import (
    MessagesSet,
    UserMessage,
    TextContent,
    ImageURLContent,
    ContentUnion,
)
from duowen_agent.utils.core_utils import json_observation, stream_to_string
from duowen_agent.utils.image_utils import file_to_base64, url_to_base64


# =============================================================================
# 数据模型定义
# =============================================================================


class ImageElementDef(BaseModel):
    """图片元素类型定义"""
    type: str = Field(description="类型唯一标识符")
    name: str = Field(description="类型中文名称")
    desc: str = Field(description="类型描述，用于分类识别")
    priority: int = Field(default=50, description="优先级，越小越靠前")
    prompt: str = Field(description="提取要点提示词片段")
    output_format: Optional[str] = Field(default=None, description="期望的输出格式")

class ImageClassificationResult(BaseModel):
    """图片分类结果"""
    types: List[str] = Field(
        description="识别到的图片元素类型列表，按重要性排序"
    )
    summary: str = Field(
        description="图片整体内容的一句话描述"
    )


# =============================================================================
# 元素类型注册表
# =============================================================================


class ImageElementRegistry:
    """图片元素类型注册表"""
    
    def __init__(self, elements: List[ImageElementDef]):
        self.elements = elements
        self._type_map: Dict[str, ImageElementDef] = {e.type: e for e in elements}
    
    @classmethod
    def load(cls, yaml_path: Optional[str] = None) -> "ImageElementRegistry":
        """
        从 YAML 文件加载元素类型定义
        
        Args:
            yaml_path: YAML 文件路径，默认从同目录下的 image_elements.yaml 加载
            
        Returns:
            ImageElementRegistry 实例
        """
        if yaml_path is None:
            # 默认从同目录加载
            yaml_path = Path(__file__).parent / "image_elements.yaml"
        
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        elements = [ImageElementDef(**item) for item in data.get("elements", [])]
        return cls(elements)
    
    def get(self, type_id: str) -> Optional[ImageElementDef]:
        """根据类型 ID 获取元素定义"""
        return self._type_map.get(type_id)
    
    def get_many(self, type_ids: List[str]) -> List[ImageElementDef]:
        """根据类型 ID 列表获取元素定义，并按优先级排序"""
        elements = [self._type_map[t] for t in type_ids if t in self._type_map]
        elements.sort(key=lambda x: x.priority)
        return elements
    
    def get_categories(self) -> Dict[str, str]:
        """获取分类器用的类型字典 {type: desc}"""
        return {e.type: e.desc for e in self.elements}
    
    def get_type_list(self) -> List[str]:
        """获取所有类型 ID 列表"""
        return list(self._type_map.keys())
    
    def __len__(self) -> int:
        return len(self.elements)
    
    def __iter__(self):
        return iter(self.elements)


# =============================================================================
# 图片分类器
# =============================================================================


class ImageClassifier(BaseLLMComponent):
    """
    图片类型分类器
    
    识别图片中包含的元素类型，支持多标签分类。
    
    Args:
        llm_instance: 多模态语言模型实例
        registry: 图片元素类型注册表，默认自动加载
        max_types: 最多返回的类型数量，默认 5
        
    Example:
        classifier = ImageClassifier(llm_instance)
        
        # 使用 http/https URL
        result = classifier.run("https://example.com/chart.png")
        
        # 使用本地文件路径 (file:// 协议)
        result = classifier.run("file:///path/to/image.png")
        
        # 转换为 base64 后再发送
        result = classifier.run("https://example.com/chart.png", convert_to_base64=True)
        
        # result.types = ["chart_bar", "table_simple"]
        # result.summary = "一张包含柱状图和表格的数据分析图"
    """
    
    CLASSIFIER_PROMPT_TEMPLATE = """你是一个专业的图片类型识别专家。请仔细分析这张图片，识别其中包含的所有内容类型。

## 可选类型列表
{types_with_desc}

## 输出要求
1. 返回图片中识别到的所有类型（可多选）
2. 按照内容占比/重要性排序
3. 最多返回 {max_types} 个类型
4. 如果都不匹配，返回 ["other"]

## 输出格式 (JSON)
```json
{{
  "types": ["type1", "type2", ...],
  "summary": "一句话描述图片整体内容"
}}
```

只输出 JSON，不要其他内容。"""

    def __init__(
        self,
        llm_instance: BaseAIChat,
        registry: Optional[ImageElementRegistry] = None,
        max_types: int = 5,
        **kwargs
    ):
        super().__init__(llm_instance, **kwargs)
        self.registry = registry or ImageElementRegistry.load()
        self.max_types = max_types
    
    def _build_prompt(self) -> str:
        """构建分类提示词"""
        types_desc = "\n".join([
            f"- **{e.type}** ({e.name}): {e.desc}"
            for e in self.registry
        ])
        return self.CLASSIFIER_PROMPT_TEMPLATE.format(
            types_with_desc=types_desc,
            max_types=self.max_types
        )
    
    def _prepare_image_url(self, image_path: str, convert_to_base64: bool = False) -> str:
        """
        预处理图片路径，根据协议类型和转换选项返回最终 URL
        
        Args:
            image_path: 图片路径，支持 http/https URL、file:// 本地路径、data URI
            convert_to_base64: 是否将图片转换为 base64 格式
            
        Returns:
            处理后的图片 URL（可能是原 URL 或 base64 data URI）
        """
        # 已经是 base64 格式，直接返回
        if image_path.startswith("data:"):
            return image_path
        
        # file:// 协议，转换为 base64
        if image_path.startswith("file://"):
            return file_to_base64(image_path)
        
        # http/https URL
        if image_path.startswith("http://") or image_path.startswith("https://"):
            if convert_to_base64:
                return url_to_base64(image_path)
            return image_path
        
        # 其他情况，尝试作为本地文件路径处理
        # 自动添加 file:// 前缀
        file_url = f"file://{image_path}" if not image_path.startswith("/") else f"file://{image_path}"
        return file_to_base64(file_url)
    
    def _create_messages(self, image_url: str) -> MessagesSet:
        """
        创建包含图片的消息集合
        
        Args:
            image_url: 处理后的图片 URL（http/https 或 base64 data URI）
        """
        prompt_text = self._build_prompt()
        
        # 构建内容列表
        content: List[ContentUnion] = [
            TextContent(text=prompt_text),
            ImageURLContent.from_url(image_url)
        ]
        
        messages = MessagesSet()
        messages.add_user(content)
        return messages
    
    def _parse_result(self, response: str) -> ImageClassificationResult:
        """解析 LLM 返回结果"""
        result: ImageClassificationResult = json_observation(
            response, ImageClassificationResult
        )
        
        # 验证类型有效性
        valid_types = []
        all_types = self.registry.get_type_list()
        for t in result.types:
            if t in all_types:
                valid_types.append(t)
            elif t.lower() in all_types:
                valid_types.append(t.lower())
        
        # 如果没有有效类型，使用 other
        if not valid_types:
            valid_types = ["other"]
        
        result.types = valid_types[:self.max_types]
        return result
    
    def run(
        self,
        image_path: str,
        convert_to_base64: bool = False,
        **kwargs
    ) -> ImageClassificationResult:
        """
        执行图片类型分类
        
        Args:
            image_path: 图片路径，支持以下格式:
                - http/https URL: "https://example.com/image.png"
                - file:// 本地路径: "file:///path/to/image.png" 
                - 直接本地路径: "/path/to/image.png" (自动添加 file://)
                - base64 data URI: "data:image/png;base64,..."
            convert_to_base64: 是否将 http/https 图片下载并转换为 base64
                - True: 下载图片并转换为 base64 后发送
                - False: 直接发送图片 URL（默认）
                - 注意: file:// 和本地路径始终会转换为 base64
            **kwargs: 传递给 LLM 的额外参数
            
        Returns:
            ImageClassificationResult: 分类结果，包含类型列表和摘要
        """
        image_url = self._prepare_image_url(image_path, convert_to_base64)
        messages = self._create_messages(image_url)
        
        for i in range(self.retry_cnt):
            try:
                response = stream_to_string(
                    self.llm_instance.chat_for_stream(messages=messages, **kwargs)
                )
                return self._parse_result(response)
            except (ObserverException, Exception) as e:
                if i == self.retry_cnt - 1:
                    # 最后一次重试失败，返回 other
                    return ImageClassificationResult(
                        types=["other"],
                        summary="图片类型识别失败"
                    )
    
    async def arun(
        self,
        image_path: str,
        convert_to_base64: bool = False,
        **kwargs
    ) -> ImageClassificationResult:
        """
        异步执行图片类型分类
        
        Args:
            image_path: 图片路径（同 run 方法）
            convert_to_base64: 是否转换为 base64（同 run 方法）
            **kwargs: 传递给 LLM 的额外参数
        """
        image_url = self._prepare_image_url(image_path, convert_to_base64)
        messages = self._create_messages(image_url)
        
        for i in range(self.retry_cnt):
            try:
                response = await self.llm_instance.achat(messages=messages, **kwargs)
                return self._parse_result(response)
            except (ObserverException, Exception) as e:
                if i == self.retry_cnt - 1:
                    return ImageClassificationResult(
                        types=["other"],
                        summary="图片类型识别失败"
                    )


# =============================================================================
# 图片内容提取器
# =============================================================================


class ImageExtractor(BaseLLMComponent):
    """
    图片内容提取器
    
    根据图片类型动态拼接提示词，提取图片中的详细内容。
    
    Args:
        llm_instance: 多模态语言模型实例
        registry: 图片元素类型注册表，默认自动加载
        
    Example:
        extractor = ImageExtractor(llm_instance)
        
        # 使用预先分类的结果
        result = extractor.run(
            image_path="https://example.com/chart.png",
            classification=classification_result
        )
        
        # 或者手动指定类型
        result = extractor.run(
            image_path="/path/to/image.png",
            types=["chart_bar", "table_simple"],
            summary="销售数据分析"
        )
    """
    
    EXTRACTION_PROMPT_TEMPLATE = """你是一个专业的文档图片内容提取专家。

## 图片概述
{summary}

## 提取任务
请根据以下要求，分别提取图片中的各类内容：

{extraction_requirements}

## 输出要求
- 按上述各项要求，分区块输出提取结果
- 每个区块使用对应的格式要求
- 确保每个区块有清晰的标题标识
- 尽可能完整、准确地提取信息"""

    def __init__(
        self,
        llm_instance: BaseAIChat,
        registry: Optional[ImageElementRegistry] = None,
        **kwargs
    ):
        super().__init__(llm_instance, **kwargs)
        self.registry = registry or ImageElementRegistry.load()
    
    def _build_extraction_prompt(
        self,
        types: List[str],
        summary: str
    ) -> str:
        """
        根据分类结果动态构建提取提示词
        
        Args:
            types: 图片元素类型列表
            summary: 图片摘要
        """
        elements = self.registry.get_many(types)
        
        if not elements:
            # 没有找到对应类型，使用 other
            other_elem = self.registry.get("other")
            if other_elem:
                elements = [other_elem]
        
        # 拼接提取要求
        requirements = []
        for i, elem in enumerate(elements, 1):
            section = f"### {i}. {elem.name}\n{elem.prompt.strip()}"
            if elem.output_format:
                section += f"\n> 输出格式: {elem.output_format}"
            requirements.append(section)
        
        extraction_requirements = "\n\n".join(requirements)
        
        return self.EXTRACTION_PROMPT_TEMPLATE.format(
            summary=summary,
            extraction_requirements=extraction_requirements
        )
    
    def _prepare_image_url(self, image_path: str, convert_to_base64: bool = False) -> str:
        """预处理图片路径"""
        if image_path.startswith("data:"):
            return image_path
        
        if image_path.startswith("file://"):
            return file_to_base64(image_path)
        
        if image_path.startswith("http://") or image_path.startswith("https://"):
            if convert_to_base64:
                return url_to_base64(image_path)
            return image_path
        
        file_url = f"file://{image_path}" if not image_path.startswith("/") else f"file://{image_path}"
        return file_to_base64(file_url)
    
    def _create_messages(
        self,
        image_url: str,
        types: List[str],
        summary: str
    ) -> MessagesSet:
        """创建包含图片和提取提示词的消息集合"""
        prompt_text = self._build_extraction_prompt(types, summary)
        
        content: List[ContentUnion] = [
            TextContent(text=prompt_text),
            ImageURLContent.from_url(image_url)
        ]
        
        messages = MessagesSet()
        messages.add_user(content)
        return messages
    
    def run(
        self,
        image_path: str,
        types: Optional[List[str]] = None,
        summary: Optional[str] = None,
        classification: Optional[ImageClassificationResult] = None,
        convert_to_base64: bool = False,
        **kwargs
    ) -> str:
        """
        执行图片内容提取
        
        Args:
            image_path: 图片路径，支持 http/https URL、file:// 本地路径、直接本地路径
            types: 图片元素类型列表（与 classification 二选一）
            summary: 图片摘要（与 classification 二选一）
            classification: 分类结果对象（优先使用）
            convert_to_base64: 是否将 http/https 图片转换为 base64
            **kwargs: 传递给 LLM 的额外参数
            
        Returns:
            str: Markdown 格式的提取内容
        """
        if classification:
            types = classification.types
            summary = classification.summary
        
        if not types:
            types = ["other"]
        if not summary:
            summary = "图片内容"
        
        image_url = self._prepare_image_url(image_path, convert_to_base64)
        messages = self._create_messages(image_url, types, summary)
        
        return stream_to_string(
            self.llm_instance.chat_for_stream(messages=messages, **kwargs)
        )
    
    async def arun(
        self,
        image_path: str,
        types: Optional[List[str]] = None,
        summary: Optional[str] = None,
        classification: Optional[ImageClassificationResult] = None,
        convert_to_base64: bool = False,
        **kwargs
    ) -> str:
        """
        异步执行图片内容提取
        
        Returns:
            str: Markdown 格式的提取内容
        """
        if classification:
            types = classification.types
            summary = classification.summary
        
        if not types:
            types = ["other"]
        if not summary:
            summary = "图片内容"
        
        image_url = self._prepare_image_url(image_path, convert_to_base64)
        messages = self._create_messages(image_url, types, summary)
        
        return await self.llm_instance.achat(messages=messages, **kwargs)


# =============================================================================
# 便捷接口：一步完成分类+提取
# =============================================================================


class ImageInterpreter(BaseLLMComponent):
    """
    图片解析器 - 一步完成分类和内容提取
    
    组合 ImageClassifier 和 ImageExtractor，提供简单的一步调用接口。
    
    Args:
        llm_instance: 多模态语言模型实例
        registry: 图片元素类型注册表，默认自动加载
        max_types: 分类时最多返回的类型数量，默认 5
        
    Example:
        interpreter = ImageInterpreter(llm_instance)
        
        # 使用 URL
        result = interpreter.run("https://example.com/chart.png")
        
        # 使用本地文件
        result = interpreter.run("/path/to/image.png")
        
        # 转换为 base64
        result = interpreter.run("https://example.com/chart.png", convert_to_base64=True)
        
        print(result.types)    # 识别到的类型
        print(result.summary)  # 图片摘要
        print(result.content)  # 提取的内容
    """
    
    def __init__(
        self,
        llm_instance: BaseAIChat,
        registry: Optional[ImageElementRegistry] = None,
        max_types: int = 5,
        **kwargs
    ):
        super().__init__(llm_instance, **kwargs)
        self.registry = registry or ImageElementRegistry.load()
        self.classifier = ImageClassifier(
            llm_instance, 
            registry=self.registry, 
            max_types=max_types,
            **kwargs
        )
        self.extractor = ImageExtractor(
            llm_instance, 
            registry=self.registry,
            **kwargs
        )
    
    def run(
        self,
        image_path: str,
        convert_to_base64: bool = False,
        **kwargs
    ) -> str:
        """
        执行完整的图片解析流程（分类 + 提取）
        
        Args:
            image_path: 图片路径，支持 http/https URL、file:// 本地路径、直接本地路径
            convert_to_base64: 是否将 http/https 图片转换为 base64
            **kwargs: 传递给 LLM 的额外参数
            
        Returns:
            str: Markdown 格式的提取内容
        """
        # Step 1: 分类
        classification = self.classifier.run(image_path, convert_to_base64, **kwargs)
        
        # Step 2: 提取
        return self.extractor.run(
            image_path=image_path,
            classification=classification,
            convert_to_base64=convert_to_base64,
            **kwargs
        )
    
    async def arun(
        self,
        image_path: str,
        convert_to_base64: bool = False,
        **kwargs
    ) -> str:
        """
        异步执行完整的图片解析流程
        
        Args:
            image_path: 图片路径（同 run 方法）
            convert_to_base64: 是否转换为 base64（同 run 方法）
            **kwargs: 传递给 LLM 的额外参数
            
        Returns:
            str: Markdown 格式的提取内容
        """
        classification = await self.classifier.arun(image_path, convert_to_base64, **kwargs)
        return await self.extractor.arun(
            image_path=image_path,
            classification=classification,
            convert_to_base64=convert_to_base64,
            **kwargs
        )


# =============================================================================
# 模块导出
# =============================================================================

__all__ = [
    # 数据模型
    "ImageElementDef",
    "ImageClassificationResult",
    # 注册表
    "ImageElementRegistry",
    # 组件
    "ImageClassifier",
    "ImageExtractor",
    "ImageInterpreter",
]

