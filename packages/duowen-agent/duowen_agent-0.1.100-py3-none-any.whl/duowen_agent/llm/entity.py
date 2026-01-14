import base64
import json
import mimetypes
import os
import re
from typing import Literal, List, Union, Dict, Optional
from urllib.parse import unquote, urlparse

from duowen_agent.utils.core_utils import remove_think
from duowen_agent.utils.image_utils import file_to_base64, url_to_base64
from pydantic import BaseModel, Field



openai_params_list = {
    "messages",
    "model",
    "audio",
    "frequency_penalty",
    "function_call",
    "functions",
    "logit_bias",
    "logprobs",
    "max_completion_tokens",
    "max_tokens",
    "metadata",
    "modalities",
    "n",
    "parallel_tool_calls",
    "prediction",
    "presence_penalty",
    "response_format",
    "seed",
    "service_tier",
    "stop",
    "store",
    "stream",
    "stream_options",
    "temperature",
    "tool_choice",
    "tools",
    "top_logprobs",
    "top_p",
    "user",
}


class BaseContent(BaseModel):
    """内容基类"""


class TextContent(BaseContent):
    type: Literal["text"] = "text"
    text: str

    def to_dict(self):
        return {"type": self.type, "text": self.text}

    def __str__(self):
        return f"[text] {self.text}"


class ImageURL(BaseModel):
    """OpenAI Vision API 图片 URL 对象"""
    url: str
    detail: Optional[Literal["low", "high", "auto"]] = None


class ImageURLContent(BaseContent):
    type: Literal["image_url"] = "image_url"
    image_url: ImageURL

    @classmethod
    def from_url(
        cls,
        url: str,
        detail: Optional[Literal["low", "high", "auto"]] = None
    ) -> "ImageURLContent":
        """从 URL 创建图片内容"""
        return cls(image_url=ImageURL(url=url, detail=detail))

    @classmethod
    def from_base64(
        cls,
        base64_data: str,
        media_type: str = "image/jpeg",
        detail: Optional[Literal["low", "high", "auto"]] = None
    ) -> "ImageURLContent":
        """从 base64 数据创建图片内容"""
        data_uri = f"data:{media_type};base64,{base64_data}"
        return cls(image_url=ImageURL(url=data_uri, detail=detail))

    def to_dict(self):
        result = {"url": self.image_url.url}
        if self.image_url.detail:
            result["detail"] = self.image_url.detail
        return {"type": self.type, "image_url": result}

    def __str__(self):
        url = self.image_url.url
        if url.startswith("data:"):
            return "[image] <base64 data>"
        return f"[image] {url}"


ContentUnion = Union[TextContent, ImageURLContent]


class Message(BaseModel):
    role: Literal["system", "user", "assistant"] = "user"
    content: Union[str, List[ContentUnion]]

    def __init__(
        self,
        content: Union[str, List[ContentUnion]],
        role: Literal["system", "user", "assistant"] = "user",
    ):
        super().__init__(content=content, role=role)

    def __getitem__(self, item):
        if item == "content":
            return self.content
        elif item == "role":
            return self.role
        else:
            raise KeyError(f"Message has no key {item}")

    def format_str(self) -> str:
        if isinstance(self.content, str):
            return (
                f"<{self.role}>\n"
                + "\n".join(["  " + j for j in self.content.split("\n")])
                + f"\n</{self.role}>"
            )
        else:
            return (
                f"<{self.role}>\n"
                + "\n".join([f"  {str(j)}" for j in self.content])
                + f"\n</{self.role}>"
            )

    def to_dict(self) -> dict:

        if isinstance(self.content, str):
            return {"role": self.role, "content": self.content}
        else:
            return {"role": self.role, "content": [i.to_dict() for i in self.content]}


class SystemMessage(Message):
    def __init__(self, content: Union[str, List[ContentUnion]]):
        super().__init__(content, "system")


class UserMessage(Message):
    def __init__(self, content: Union[str, List[ContentUnion]]):
        super().__init__(content, "user")


class AssistantMessage(Message):
    def __init__(self, content: Union[str, List[ContentUnion]]):
        super().__init__(content, "assistant")


def parse_content(content: Union[str, List[dict], List[ContentUnion]]) -> Union[str, List[ContentUnion]]:
    """
    将 content 解析为正确的类型
    
    支持:
    - str: 直接返回
    - List[ContentUnion]: 直接返回
    - List[dict]: 转换为 List[ContentUnion]
    """
    if isinstance(content, str):
        return content
    
    if not content:
        return content
    
    # 如果已经是 ContentUnion 对象，直接返回
    if isinstance(content[0], (TextContent, ImageURLContent)):
        return content
    
    # 解析 dict 列表
    result: List[ContentUnion] = []
    for item in content:
        if not isinstance(item, dict):
            continue
        content_type = item.get("type")
        if content_type == "text":
            result.append(TextContent(text=item.get("text", "")))
        elif content_type == "image_url":
            image_url_data = item.get("image_url", {})
            if isinstance(image_url_data, dict):
                result.append(ImageURLContent(
                    image_url=ImageURL(
                        url=image_url_data.get("url", ""),
                        detail=image_url_data.get("detail")
                    )
                ))
            else:
                result.append(ImageURLContent(image_url=image_url_data))
    return result


class MessagesSet(BaseModel):
    message_list: List[Message] = []

    def __init__(self, message_list: List[dict] | List[Message] = None):
        if message_list:
            if isinstance(message_list[0], dict):
                # 解析 dict 列表，支持 ContentUnion 格式的 content
                parsed_list = []
                for msg in message_list:
                    role = msg.get("role", "user")
                    content = parse_content(msg.get("content", ""))
                    parsed_list.append(Message(content=content, role=role))
                message_list = parsed_list
            elif isinstance(message_list[0], Message):
                pass
            else:
                raise ValueError("MessagesSet init message_list type error")
            super().__init__(message_list=message_list)
        else:
            super().__init__()

    def remove_assistant_think(self):
        """推理模型需要剔除think部分"""
        for message in self.message_list:
            if message.role == "assistant":
                message.content = remove_think(message.content)
        return self

    def add_user(self, content: Union[str, ContentUnion, List[ContentUnion]]):
        self.message_list.append(UserMessage(content))
        return self

    def add_assistant(self, content: Union[str, ContentUnion, List[ContentUnion]]):
        self.message_list.append(AssistantMessage(content))
        return self

    def add_system(self, content: Union[str, ContentUnion, List[ContentUnion]]):
        self.message_list.append(SystemMessage(content))
        return self

    def has_images(self) -> bool:
        """
        判断消息集合中是否包含图片内容
        
        用于判断是否需要调用多模态模型。
        
        Returns:
            bool: 如果任意消息包含 ImageURLContent 则返回 True,否则返回 False
        """
        for message in self.message_list:
            if isinstance(message.content, list):
                for item in message.content:
                    if isinstance(item, ImageURLContent):
                        return True
        return False

    def parse_image_urls(
        self,
        image_extensions: tuple = (".jpg", ".jpeg", ".png", ".gif", ".webp"),
        convert_to_base64: bool = False,
        roles: tuple = ("user",),
        tag: Optional[str] = None
    ):
        """
        识别消息内容中的图片链接并转换为 ContentUnion 格式
        
        将纯文本 content 中的图片 URL 提取出来，转换为 List[TextContent | ImageURLContent] 格式。
        支持 http/https 链接、file:// 本地路径和 data:image base64 格式。
        
        Args:
            image_extensions: 需要识别的图片扩展名元组
            convert_to_base64: 是否将 http/https 图片 URL 下载并转换为 base64 格式
            roles: 需要处理的消息角色类型，默认只处理 user 消息
            tag: 特殊标签名称，当指定时只处理被 <tag>...</tag> 包裹的 URL
                 例如 tag="image" 时，只识别 <image>https://...</image> 格式
                 默认为 None，表示匹配所有符合条件的 URL（向后兼容）
            
        Returns:
            self，支持链式调用
            
        Note:
            file:// 协议的本地文件路径会自动转换为 base64 格式
        """
        # 构建扩展名匹配模式
        ext_pattern = '|'.join(re.escape(ext) for ext in image_extensions)
        
        # 构建 URL 匹配模式 - 支持 http/https、file:// 和 data URI
        url_inner_pattern = (
            # http/https URL
            r'https?://[^\s<>"\']+?(?:' + ext_pattern + r')(?:\?[^\s<>"\']*)?|'
            # file:// 本地路径
            r'file://[^\s<>"\']+?(?:' + ext_pattern + r')|'
            # data URI
            r'data:image/[a-zA-Z]+;base64,[A-Za-z0-9+/=]+'
        )
        
        if tag:
            # 使用特殊标签包裹的模式
            url_pattern = re.compile(
                rf'<{re.escape(tag)}>\s*({url_inner_pattern})\s*</{re.escape(tag)}>',
                re.IGNORECASE
            )
        else:
            # 原有的直接匹配模式
            url_pattern = re.compile(
                rf'({url_inner_pattern})',
                re.IGNORECASE
            )
        
        for message in self.message_list:
            # 仅处理指定角色的纯文本内容
            if message.role not in roles:
                continue
            if not isinstance(message.content, str):
                continue
            
            matches = list(url_pattern.finditer(message.content))
            if not matches:
                continue
            
            # 构建 ContentUnion 列表
            content_parts: List[ContentUnion] = []
            last_end = 0
            
            for match in matches:
                # 添加图片链接前的文本
                if match.start() > last_end:
                    text_before = message.content[last_end:match.start()].strip()
                    if text_before:
                        content_parts.append(TextContent(text=text_before))
                
                # 添加图片内容 - 使用捕获组获取纯 URL
                image_url = match.group(1)
                
                # file:// 协议默认转换为 base64
                if image_url.startswith("file://"):
                    image_url = file_to_base64(image_url)
                elif convert_to_base64 and image_url.startswith("http"):
                    image_url = url_to_base64(image_url)
                
                content_parts.append(ImageURLContent.from_url(image_url))
                last_end = match.end()
            
            # 添加最后一个图片后的剩余文本
            if last_end < len(message.content):
                text_after = message.content[last_end:].strip()
                if text_after:
                    content_parts.append(TextContent(text=text_after))
            
            # 更新消息内容
            if content_parts:
                message.content = content_parts
        
        return self

    def convert_images_to_base64(
        self,
        roles: tuple = ("user",),
        timeout: int = 30
    ):
        """
        将消息中已存在的 ImageURLContent 中的图片 URL 转换为 base64 格式
        
        此方法遍历已经包含 ImageURLContent 的消息，将其中的 http/https URL 
        下载并转换为 base64 data URI 格式。
        
        与 parse_image_urls 的区别：
        - parse_image_urls: 从纯文本中解析识别图片 URL 并创建 ImageURLContent
        - convert_images_to_base64: 将已存在的 ImageURLContent 中的 URL 图片转换为 base64
        
        Args:
            roles: 需要处理的消息角色类型，默认只处理 user 消息
            timeout: 下载图片的超时时间（秒），默认 30 秒
            
        Returns:
            self，支持链式调用
            
        Note:
            - 已经是 base64 格式（data: URI）的图片会被跳过
            - file:// 协议的本地文件会被转换为 base64
            - 下载失败时保留原 URL
        """

        
        for message in self.message_list:
            if message.role not in roles:
                continue
            
            # 只处理包含 ContentUnion 列表的消息
            if not isinstance(message.content, list):
                continue
            
            for item in message.content:
                if not isinstance(item, ImageURLContent):
                    continue
                
                current_url = item.image_url.url
                
                # 跳过已经是 base64 格式的
                if current_url.startswith("data:"):
                    continue
                
                # 转换 file:// 或 http/https URL
                if current_url.startswith("file://"):
                    new_url = file_to_base64(current_url)
                elif current_url.startswith("http://") or current_url.startswith("https://"):
                    new_url = url_to_base64(current_url, timeout)
                else:
                    continue
                
                # 更新 URL
                item.image_url.url = new_url
        
        return self

    def append_messages(
        self, messages_set: Union["MessagesSet", List[UserMessage | AssistantMessage]]
    ):
        """追加消息集合到当前集合"""
        if type(messages_set) is MessagesSet:
            self.message_list = self.message_list + messages_set.message_list
        else:
            for message in messages_set:
                if type(message) is Message:
                    self.message_list.append(message)
                else:
                    raise ValueError("MessagesSet append_messages type error")
        return self

    def append(self, message: Message):
        """追加单个消息"""
        if not isinstance(message, Message):
            raise TypeError("Only Message objects can be appended to MessagesSet")
        self.message_list.append(message)
        return self

    def pop(self, index: int = -1):
        """移除并返回指定位置的消息"""
        return self.message_list.pop(index)

    def index(self, message: Message, start: int = 0, end: int = None):
        """查找消息的位置"""
        if end is None:
            end = len(self.message_list)
        return self.message_list.index(message, start, end)

    def count(self, message: Message):
        """统计消息出现的次数"""
        return self.message_list.count(message)

    def copy_message(self):
        """创建消息集合的浅拷贝"""
        return MessagesSet(self.message_list.copy())

    def filter_by_role(self, role: Literal["system", "user", "assistant"]):
        """根据角色过滤消息"""
        filtered = [msg for msg in self.message_list if msg.role == role]
        return MessagesSet(filtered)

    def get_first_message(self):
        """获取第一条消息"""
        return self.message_list[0] if self.message_list else None

    def get_last_message(self):
        """获取最后一条消息"""
        return self.message_list[-1] if self.message_list else None

    def remove_first_message(self):
        """移除第一条消息"""
        if self.message_list:
            self.message_list.pop(0)
        return self

    def remove_last_message(self):
        """移除最后一条消息"""
        if self.message_list:
            self.message_list.pop()
        return self

    def is_empty(self):
        """检查是否为空"""
        return len(self.message_list) == 0

    def __contains__(self, message: Message):
        """支持 in 操作符"""
        return message in self.message_list

    def to_dict(self) -> List[dict]:
        """
        序列化为 dict 列表，可通过 MessagesSet(data) 反序列化
        
        Returns:
            消息的 dict 列表，格式兼容 OpenAI API
        """
        return [i.to_dict() for i in self.message_list]

    # 别名，保持向后兼容
    get_messages = to_dict

    def get_format_messages(self):
        _data = []

        for i in self.message_list:
            _data.append(i.format_str())

        return "\n\n".join(_data)

    def pretty_print(self):
        print(self.get_format_messages())

    def __add__(self, other: "MessagesSet") -> "MessagesSet":
        if not isinstance(other, MessagesSet):
            raise TypeError("Can only add MessagesSet to MessagesSet")
        return MessagesSet(self.message_list + other.message_list)

    def __iadd__(self, other: "MessagesSet") -> "MessagesSet":
        if not isinstance(other, MessagesSet):
            raise TypeError("Can only add MessagesSet to MessagesSet")
        return MessagesSet(self.message_list + other.message_list)

    def __getitem__(self, item):
        """支持索引访问和切片操作"""
        if isinstance(item, slice):
            # 切片操作
            return MessagesSet(self.message_list[item])
        return self.message_list[item]

    def __setitem__(self, index, value):
        """支持通过索引设置消息"""
        if not isinstance(value, Message):
            raise TypeError("Only Message objects can be assigned to MessagesSet")
        self.message_list[index] = value

    def __delitem__(self, index):
        """支持通过索引删除消息"""
        del self.message_list[index]

    def insert(self, index, value):
        """在指定位置插入消息"""
        if not isinstance(value, Message):
            raise TypeError("Only Message objects can be inserted into MessagesSet")
        self.message_list.insert(index, value)
        return self

    def extend(self, messages):
        """扩展消息列表"""
        if isinstance(messages, MessagesSet):
            self.message_list.extend(messages.message_list)
        elif isinstance(messages, list):
            for msg in messages:
                if not isinstance(msg, Message):
                    raise TypeError("All items in the list must be Message objects")
            self.message_list.extend(messages)
        else:
            raise TypeError(
                "Can only extend with MessagesSet or list of Message objects"
            )
        return self

    def reverse(self):
        """反转消息顺序"""
        self.message_list.reverse()
        return self

    def clear(self):
        """清空所有消息"""
        self.message_list.clear()
        return self

    def __len__(self):
        return len(self.message_list)

    def __bool__(self):
        return bool(self.message_list)

    def __iter__(self):
        for item in self.message_list:
            yield item

    def __repr__(self):
        return f"MessagesSet({self.message_list})"

    def __str__(self):
        return f"MessagesSet({str(self.message_list)[:200]})"


class Tool(BaseModel):
    name: str
    arguments: Dict = Field(default_factory=dict)
    think: str = None

    def __str__(self):
        return json.dumps(
            {"name": self.name, "arguments": self.arguments, "think": self.think},
            ensure_ascii=False,
        )


class ToolsCall(BaseModel):
    think: str = None
    tools: List[Tool] = Field(default_factory=list)

    def __str__(self):
        return json.dumps(
            {"think": self.think, "tools": [i.model_dump() for i in self.tools]},
            ensure_ascii=False,
        )
