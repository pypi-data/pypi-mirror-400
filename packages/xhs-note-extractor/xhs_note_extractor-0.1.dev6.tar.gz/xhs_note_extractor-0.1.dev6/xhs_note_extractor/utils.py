"""
小红书工具模块

该模块提供了小红书相关的辅助功能，包括：
- 设备管理和连接
- 页面操作和元素查找
- 数据格式化和验证
- 错误处理和日志记录

作者: JoyCode Agent
版本: 1.0.0
"""

import uiautomator2 as u2
import time
import re
import requests
import logging
from typing import Dict, List, Optional, Union, Any
from functools import wraps

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    重试装饰器
    
    Args:
        max_attempts (int): 最大重试次数
        delay (float): 初始延迟时间(秒)
        backoff (float): 延迟时间倍增因子
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay
            
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        logger.error(f"函数 {func.__name__} 在 {max_attempts} 次尝试后仍然失败: {e}")
                        raise
                    
                    logger.warning(f"函数 {func.__name__} 第 {attempt} 次尝试失败: {e}，{current_delay}秒后重试...")
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            return None
        return wrapper
    return decorator


class DeviceManager:
    """设备管理类"""
    
    @staticmethod
    def connect_device(device_serial: Optional[str] = None) -> u2.Device:
        """
        连接设备
        
        Args:
            device_serial (str, optional): 设备序列号
            
        Returns:
            u2.Device: 设备对象
        """
        try:
            if device_serial:
                device = u2.connect(device_serial)
                logger.info(f"✓ 已连接指定设备: {device.serial}")
            else:
                device = u2.connect()
                logger.info(f"✓ 已连接设备: {device.serial}")
            return device
        except Exception as e:
            logger.error(f"✗ 设备连接失败: {e}")
            raise
    
    @staticmethod
    def check_device_status(device: u2.Device) -> Dict[str, Any]:
        """
        检查设备状态
        
        Args:
            device (u2.Device): 设备对象
            
        Returns:
            Dict[str, Any]: 设备状态信息
        """
        try:
            info = device.info
            return {
                "serial": device.serial,
                "status": "connected",
                "sdk_version": info.get('sdkInt', 'unknown'),
                "screen_size": f"{info.get('displayWidth', 0)}x{info.get('displayHeight', 0)}",
                "battery": info.get('battery', {})
            }
        except Exception as e:
            logger.error(f"✗ 获取设备状态失败: {e}")
            return {"status": "error", "error": str(e)}


class ElementFinder:
    """元素查找器类"""
    
    def __init__(self, device: u2.Device):
        """
        初始化元素查找器
        
        Args:
            device (u2.Device): 设备对象
        """
        self.device = device
    
    @retry(max_attempts=3, delay=0.5)
    def find_element_by_text(self, text: str, timeout: float = 5.0) -> Optional[u2.UiObject]:
        """
        通过文本查找元素
        
        Args:
            text (str): 要查找的文本
            timeout (float): 超时时间(秒)
            
        Returns:
            Optional[u2.UiObject]: 找到的元素对象，未找到返回None
        """
        element = self.device(text=text)
        if element.wait(timeout=timeout):
            return element
        return None
    
    @retry(max_attempts=3, delay=0.5)
    def find_element_by_description(self, description: str, timeout: float = 5.0) -> Optional[u2.UiObject]:
        """
        通过描述查找元素
        
        Args:
            description (str): 要查找的描述
            timeout (float): 超时时间(秒)
            
        Returns:
            Optional[u2.UiObject]: 找到的元素对象，未找到返回None
        """
        element = self.device(description=description)
        if element.wait(timeout=timeout):
            return element
        return None
    
    @retry(max_attempts=3, delay=0.5)
    def find_element_by_resource_id(self, resource_id: str, timeout: float = 5.0) -> Optional[u2.UiObject]:
        """
        通过资源ID查找元素
        
        Args:
            resource_id (str): 资源ID
            timeout (float): 超时时间(秒)
            
        Returns:
            Optional[u2.UiObject]: 找到的元素对象，未找到返回None
        """
        element = self.device(resourceId=resource_id)
        if element.wait(timeout=timeout):
            return element
        return None
    
    def wait_for_element(self, condition_func, timeout: float = 10.0, check_interval: float = 0.5) -> bool:
        """
        等待元素出现
        
        Args:
            condition_func: 条件函数，返回True表示找到元素
            timeout (float): 超时时间(秒)
            check_interval (float): 检查间隔(秒)
            
        Returns:
            bool: 是否找到元素
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if condition_func():
                return True
            time.sleep(check_interval)
        return False


class DataFormatter:
    """数据格式化类"""
    
    @staticmethod
    def format_like_count(like_text: str) -> str:
        """
        格式化点赞数字符串
        
        Args:
            like_text (str): 原始点赞数字符串
            
        Returns:
            str: 格式化后的点赞数
        """
        if not like_text:
            return "0"
        
        # 提取数字和可能的单位
        match = re.search(r'([\d.]+)\s*([wW万]?)\s*', str(like_text))
        if match:
            number = match.group(1)
            unit = match.group(2).lower()
            
            # 处理单位转换
            if unit in ['w', '万']:
                try:
                    num = float(number)
                    return str(int(num * 10000))
                except ValueError:
                    return number
            else:
                return number
        
        # 如果没有匹配到模式，返回原始文本中的数字
        digits = ''.join(c for c in str(like_text) if c.isdigit())
        return digits if digits else "0"
    
    @staticmethod
    def extract_image_urls_from_html(html: str) -> List[str]:
        """
        从HTML中提取图片URL
        
        Args:
            html (str): HTML内容
            
        Returns:
            List[str]: 图片URL列表
        """
        img_patterns = [
            r'property="og:image" content="(https://[^"]+)"',
            r'"url":"(https://sns-img-[^"]+)"',
            r'"url":"(https://sns-img-qc\.xhscdn\.com/[^"]+)"',
            r'data-src="(https://[^"]+)"',
            r'src="(https://[^"]+\.(?:jpg|jpeg|png|gif))"'
        ]
        
        found_urls = []
        for pattern in img_patterns:
            matches = re.findall(pattern, html)
            for match in matches:
                clean_url = match.replace('\\u002F', '/').replace('\\/', '/')
                if clean_url not in found_urls:
                    found_urls.append(clean_url)
        
        return found_urls
    
    @staticmethod
    def clean_text_content(text: str) -> str:
        """
        清理文本内容
        
        Args:
            text (str): 原始文本
            
        Returns:
            str: 清理后的文本
        """
        if not text:
            return ""
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        # 移除特殊字符
        text = re.sub(r'[^\w\s\u4e00-\u9fff，。！？；：""''（）【】]', '', text)
        # 移除前后空格
        text = text.strip()
        
        return text


class NetworkUtils:
    """网络工具类"""
    
    @staticmethod
    @retry(max_attempts=3, delay=1.0)
    def fetch_html(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 10) -> str:
        """
        获取网页HTML内容
        
        Args:
            url (str): 目标URL
            headers (dict, optional): 请求头
            timeout (int): 超时时间(秒)
            
        Returns:
            str: HTML内容
            
        Raises:
            requests.RequestException: 请求失败时抛出异常
        """
        default_headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1"
        }
        
        if headers:
            default_headers.update(headers)
        
        response = requests.get(url, headers=default_headers, timeout=timeout)
        response.raise_for_status()
        
        return response.text
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        验证URL是否有效
        
        Args:
            url (str): 要验证的URL
            
        Returns:
            bool: URL是否有效
        """
        try:
            from urllib.parse import urlparse
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def is_valid_xhs_url(url: str) -> bool:
        """
        验证小红书URL是否有效
        
        Args:
            url (str): 要验证的小红书笔记URL
            
        Returns:
            bool: URL是否有效的小红书笔记URL
        """
        try:
            from urllib.parse import urlparse
            result = urlparse(url)
            
            # 检查是否为有效的URL
            if not all([result.scheme, result.netloc]):
                return False
            
            # 检查是否为小红书域名
            valid_domains = ['xiaohongshu.com', 'www.xiaohongshu.com', 'm.xiaohongshu.com']
            if result.netloc not in valid_domains:
                return False
            
            # 检查是否为笔记详情页URL
            if '/explore/' not in url and '/discovery/item/' not in url:
                return False
            
            return True
        except Exception:
            return False


class FileManager:
    """文件管理类"""
    
    @staticmethod
    def save_data_to_file(data: str, filename: str, encoding: str = "utf-8") -> bool:
        """
        将数据保存到文件
        
        Args:
            data (str): 要保存的数据
            filename (str): 文件名
            encoding (str): 文件编码
            
        Returns:
            bool: 是否保存成功
        """
        try:
            with open(filename, "w", encoding=encoding) as f:
                f.write(data)
            logger.info(f"✓ 数据已保存到: {filename}")
            return True
        except Exception as e:
            logger.error(f"✗ 保存数据失败: {e}")
            return False
    
    @staticmethod
    def load_data_from_file(filename: str, encoding: str = "utf-8") -> Optional[str]:
        """
        从文件加载数据
        
        Args:
            filename (str): 文件名
            encoding (str): 文件编码
            
        Returns:
            Optional[str]: 文件内容，失败返回None
        """
        try:
            with open(filename, "r", encoding=encoding) as f:
                return f.read()
        except Exception as e:
            logger.error(f"✗ 加载数据失败: {e}")
            return None


class XHSUtils:
    """小红书工具类 - 兼容原有接口"""
    
    @staticmethod
    def get_detail_data(device: u2.Device) -> Dict[str, Union[str, List[str]]]:
        """
        从当前已经打开的小红书详情页提取完整正文、图片和点赞数。
        这是为了向后兼容而保留的方法，实际功能已迁移到extractor.py中。
        
        Args:
            device (u2.Device): 设备对象
            
        Returns:
            Dict[str, Union[str, List[str]]]: 包含笔记数据的字典
        """
        # 导入extractor模块中的方法
        from .extractor import XHSNoteExtractor
        
        # 创建临时提取器实例
        extractor = XHSNoteExtractor.__new__(XHSNoteExtractor)
        extractor.device = device
        
        # 调用提取方法
        return extractor._get_detail_data()


# 便捷函数
def connect_device(device_serial: Optional[str] = None) -> u2.Device:
    """
    便捷函数：连接设备
    
    Args:
        device_serial (str, optional): 设备序列号
        
    Returns:
        u2.Device: 设备对象
    """
    return DeviceManager.connect_device(device_serial)


def format_like_count(like_text: str) -> str:
    """
    便捷函数：格式化点赞数
    
    Args:
        like_text (str): 原始点赞数字符串
        
    Returns:
        str: 格式化后的点赞数
    """
    return DataFormatter.format_like_count(like_text)


def extract_image_urls_from_html(html: str) -> List[str]:
    """
    便捷函数：从HTML中提取图片URL
    
    Args:
        html (str): HTML内容
        
    Returns:
        List[str]: 图片URL列表
    """
    return DataFormatter.extract_image_urls_from_html(html)


def fetch_html(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 10) -> str:
    """
    便捷函数：获取网页HTML内容
    
    Args:
        url (str): 目标URL
        headers (dict, optional): 请求头
        timeout (int): 超时时间(秒)
        
    Returns:
        str: HTML内容
    """
    return NetworkUtils.fetch_html(url, headers, timeout)