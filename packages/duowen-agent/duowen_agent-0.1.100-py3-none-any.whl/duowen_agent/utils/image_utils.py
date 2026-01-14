"""
图片处理工具函数

提供图片 URL 和 base64 之间的转换功能。
"""

import base64
import mimetypes
import os
from urllib.parse import unquote, urlparse


def file_to_base64(file_url: str) -> str:
    """
    将本地文件路径 (file:// URL) 转换为 base64 data URI
    
    Args:
        file_url: file:// 协议的本地文件路径，例如:
            - "file:///path/to/image.png"
            - "file:///C:/path/to/image.png" (Windows)
        
    Returns:
        base64 data URI 格式的字符串，例如:
            "data:image/png;base64,iVBORw0KGgo..."
        如果转换失败，返回原 URL
        
    Example:
        >>> url = file_to_base64("file:///tmp/test.png")
        >>> url.startswith("data:image/")
        True
    """
    try:
        parsed = urlparse(file_url)
        file_path = unquote(parsed.path)
        
        # Windows 路径处理: file:///C:/path -> C:/path
        if file_path.startswith('/') and len(file_path) > 2 and file_path[2] == ':':
            file_path = file_path[1:]
        
        if not os.path.isfile(file_path):
            return file_url
        
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type or not mime_type.startswith("image/"):
            mime_type = "image/jpeg"
        
        with open(file_path, "rb") as f:
            b64_data = base64.b64encode(f.read()).decode("utf-8")
        
        return f"data:{mime_type};base64,{b64_data}"
    except Exception:
        return file_url


def url_to_base64(url: str, timeout: int = 30) -> str:
    """
    将图片 URL 下载并转换为 base64 data URI
    
    Args:
        url: http/https 图片 URL
        timeout: 下载超时时间（秒），默认 30 秒
        
    Returns:
        base64 data URI 格式的字符串，例如:
            "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
        如果已经是 data URI 或下载失败，返回原 URL
        
    Example:
        >>> url = url_to_base64("https://example.com/image.jpg")
        >>> url.startswith("data:image/")
        True
    """
    if url.startswith("data:"):
        return url
    
    try:
        import requests
        response = requests.get(url, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        
        content_type = response.headers.get("content-type", "").split(";")[0].strip()
        if not content_type or not content_type.startswith("image/"):
            ext = "." + url.split("?")[0].split(".")[-1].lower()
            content_type = mimetypes.types_map.get(ext, "image/jpeg")
        
        b64_data = base64.b64encode(response.content).decode("utf-8")
        return f"data:{content_type};base64,{b64_data}"
    except Exception:
        return url


__all__ = [
    "file_to_base64",
    "url_to_base64",
]
