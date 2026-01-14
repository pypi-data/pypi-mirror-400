"""
小红书笔记提取器包

这是一个用于从小红书URL中提取笔记信息的Python包。
支持URL解析、设备连接、页面跳转和笔记内容提取。

主要功能：
- URL解析和转换（支持标准格式和xhsdiscover协议格式）
- 设备连接和自动化操作
- 笔记内容提取（正文、图片、点赞数等）
- 结构化数据返回

示例:
    >>> from xhs_note_extractor import XHSNoteExtractor
    >>> extractor = XHSNoteExtractor()
    >>> data = extractor.extract_note_data(url="https://www.xiaohongshu.com/explore/...")
    >>> print(data['content'])
"""

__version__ = "1.0.0"
__author__ = "JoyCode Agent"
__email__ = "agent@joycode.com"

from .extractor import XHSNoteExtractor
from .utils import (
    DeviceManager,
    ElementFinder,
    DataFormatter,
    NetworkUtils,
    FileManager,
    XHSUtils,
    connect_device,
    format_like_count,
    extract_image_urls_from_html,
    fetch_html
)

__all__ = [
    "XHSNoteExtractor",
    "DeviceManager",
    "ElementFinder",
    "DataFormatter",
    "NetworkUtils",
    "FileManager",
    "XHSUtils",
    "connect_device",
    "format_like_count",
    "extract_image_urls_from_html",
    "fetch_html",
]