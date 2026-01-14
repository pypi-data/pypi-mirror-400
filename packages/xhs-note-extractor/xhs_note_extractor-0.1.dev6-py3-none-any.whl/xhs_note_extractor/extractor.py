"""
小红书笔记提取器模块

该模块提供了从小红书URL中提取笔记信息的功能，包括：
- URL解析和转换
- 设备连接和页面跳转
- 笔记内容提取（正文、图片、点赞数等）
- 结构化数据返回

作者: JoyCode Agent
版本: 1.0.0
"""

import uiautomator2 as u2
import time
import re
import requests
import logging
from typing import Dict, List, Optional, Union
from urllib.parse import urlparse, parse_qs
import xml.etree.ElementTree as ET

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class XHSNoteExtractor:
    """
    小红书笔记提取器类
    
    提供了从小红书URL中提取笔记信息的完整功能，
    包括URL解析、设备连接、页面跳转和笔记内容提取。
    """
    
    def __init__(self, device_serial: Optional[str] = None, enable_time_logging: bool = True):
        """
        初始化小红书笔记提取器
        
        Args:
            device_serial (str, optional): 设备序列号，如果为None则自动连接可用设备
            enable_time_logging (bool, optional): 是否启用耗时打印，默认为True
            
        Raises:
            RuntimeError: 当没有可用设备时抛出异常
        """
        self.device = None
        self.device_serial = device_serial
        self.enable_time_logging = enable_time_logging
        if not self.connect_device():
            raise RuntimeError("未找到可用的Android设备，请连接设备后再试")
    
    def _time_method(self, method_name, start_time):
        """
        记录方法执行时间
        
        Args:
            method_name (str): 方法名称
            start_time (float): 开始时间
        """
        if self.enable_time_logging:
            elapsed_time = time.time() - start_time
            logger.info(f"[{method_name}] 耗时: {elapsed_time:.3f}秒")
    
    def connect_device(self) -> bool:
        """
        连接设备
        
        Returns:
            bool: 是否成功连接设备
        """
        start_time = time.time()
        try:
            if self.device_serial:
                self.device = u2.connect(self.device_serial)
            else:
                self.device = u2.connect()
            logger.info(f"✓ 已连接设备: {self.device.serial}")
            self._time_method("connect_device", start_time)
            return True
        except Exception as e:
            logger.error(f"✗ 设备连接失败: {e}")
            self._time_method("connect_device", start_time)
            return False
    def is_device_connected(self) -> bool:
        """
        检查设备是否仍然连接
        
        Returns:
            bool: 设备是否连接
        """
        if not self.device:
            return False
        try:
            # 通过获取设备信息来验证连接
            self.device.info
            return True
        except:
            return False

    @staticmethod
    def parse_xhs_url(url: str) -> Dict[str, str]:
        """
        解析小红书URL，提取note_id和xsec_token
        
        Args:
            url (str): 小红书URL，支持标准格式或xhsdiscover协议格式
            
        Returns:
            Dict[str, str]: 包含note_id和xsec_token的字典
            
        Raises:
            ValueError: 当URL格式不正确时抛出异常
        """
        start_time = time.time()
        # 处理xhsdiscover协议格式
        if url.startswith("xhsdiscover://"):
            # 提取note_id
            note_id_match = re.search(r'item/([^?]+)', url)
            if not note_id_match:
                raise ValueError("无法从xhsdiscover URL中提取note_id")
            
            note_id = note_id_match.group(1)
            
            # 尝试从open_url参数中提取原始URL
            open_url_match = re.search(r'open_url=([^&]+)', url)
            xsec_token = ""
            if open_url_match:
                open_url = open_url_match.group(1)
                # 解码URL
                import urllib.parse
                decoded_url = urllib.parse.unquote(open_url)
                # 从原始URL中提取xsec_token
                token_match = re.search(r'xsec_token=([^&]+)', decoded_url)
                if token_match:
                    xsec_token = token_match.group(1)
            
            return {
                "note_id": note_id,
                "xsec_token": xsec_token,
                "original_url": url
            }
        
        # 处理标准URL格式
        elif "xiaohongshu.com" in url:
            parsed_url = urlparse(url)
            path_parts = parsed_url.path.strip('/').split('/')
            
            # 查找explore部分和note_id
            if 'explore' in path_parts:
                explore_index = path_parts.index('explore')
                if explore_index + 1 < len(path_parts):
                    note_id = path_parts[explore_index + 1]
                else:
                    raise ValueError("URL中缺少note_id")
            # 兼容 /discovery/item/ 格式
            elif 'discovery' in path_parts and 'item' in path_parts:
                item_index = path_parts.index('item')
                if item_index + 1 < len(path_parts):
                    note_id = path_parts[item_index + 1]
                else:
                    raise ValueError("URL中缺少note_id")
            else:
                raise ValueError("URL格式不正确，缺少/explore/或/discovery/item/路径")
            
            # 提取查询参数中的xsec_token
            query_params = parse_qs(parsed_url.query)
            xsec_token = query_params.get('xsec_token', [''])[0]
            
            elapsed_time = time.time() - start_time
            logger.info(f"[parse_xhs_url] 耗时: {elapsed_time:.3f}秒")
            return {
                "note_id": note_id,
                "xsec_token": xsec_token,
                "original_url": url
            }
        
        else:
            elapsed_time = time.time() - start_time
            logger.info(f"[parse_xhs_url] 耗时: {elapsed_time:.3f}秒")
            raise ValueError("不支持的URL格式")
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """
        验证URL是否是有效的小红书URL
        
        Args:
            url (str): 要验证的URL
            
        Returns:
            bool: URL是否有效
        """
        try:
            XHSNoteExtractor.parse_xhs_url(url)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def convert_to_xhsdiscover_format(note_id: str, xsec_token: str = "") -> str:
        """
        将note_id和xsec_token转换为xhsdiscover协议格式
        
        Args:
            note_id (str): 笔记ID
            xsec_token (str): xsec_token参数
            
        Returns:
            str: xhsdiscover协议格式的URL
        """
        start_time = time.time()
        result = ""
        if xsec_token:
            original_url = f"http://www.xiaohongshu.com/explore/{note_id}?xsec_token={xsec_token}&xsec_source=pc_feed"
            encoded_url = requests.utils.quote(original_url)
            result = f"xhsdiscover://item/{note_id}?open_url={encoded_url}"
        else:
            result = f"xhsdiscover://item/{note_id}"
        
        elapsed_time = time.time() - start_time
        logger.info(f"[convert_to_xhsdiscover_format] 耗时: {elapsed_time:.3f}秒")
        return result
    
    def extract_note_data(self, url: Optional[str] = None, note_id: Optional[str] = None, 
                         xsec_token: Optional[str] = None) -> Dict[str, Union[str, List[str]]]:
        """
        从小红书笔记中提取数据
        
        Args:
            url (str, optional): 小红书URL，如果提供则会解析其中的note_id和xsec_token
            note_id (str, optional): 笔记ID，如果提供则直接使用
            xsec_token (str, optional): xsec_token参数
            
        Returns:
            Dict[str, Union[str, List[str]]]: 包含笔记数据的字典，格式与xhs_utils.get_detail_data()一致
            
        Raises:
            RuntimeError: 当设备未连接时抛出异常
            Exception: 当提取过程中出现错误时抛出异常
        """
        start_time = time.time()
        # 如果提供了URL，则先解析它（验证URL有效性）
        if url:
            parsed_data = self.parse_xhs_url(url)
            note_id = parsed_data["note_id"]
            xsec_token = parsed_data["xsec_token"]
            
        # 检查设备是否连接
        if self.device is None:
            self._time_method("extract_note_data", start_time)
            raise RuntimeError("设备未连接，请先连接设备")
        
        # 构建跳转URL
        jump_url = self.convert_to_xhsdiscover_format(note_id, xsec_token)
        
        logger.info(f"正在尝试跳转至笔记: {note_id}")
        
        try:
            # 发起跳转
            self.device.open_url(jump_url)
            logger.info("✓ 已发送跳转指令，等待页面加载...")
            
            # 使用现有的xhs_utils功能提取数据
            data = self._get_detail_data()
            
            logger.info(f"✓ 成功提取笔记数据，点赞数: {data['likes']}, 图片数: {len(data['image_urls'])}")
            
            self._time_method("extract_note_data", start_time)
            return data
            
        except Exception as e:
            logger.error(f"✗ 提取笔记数据失败: {e}")
            self._time_method("extract_note_data", start_time)
            raise
    
    def _get_detail_data(self) -> Dict[str, Union[str, List[str]]]:
        """
        从当前已经打开的小红书详情页提取完整正文、图片和点赞数。
        优化版本: 使用 dump_hierarchy 替代遍历，大幅提升速度。
        
        Returns:
            Dict[str, Union[str, List[str]]]: 包含笔记数据的字典
        """
        start_time = time.time()
        logger.info("🔍 进入深度提取模式 (XML优化版)...")
        
        # 1. 验证是否进入详情页 & 展开全文
        detail_loaded = False
        detail_keywords = ["说点什么", "写评论", "写点什么", "收藏", "点赞", "评论", "分享", "发弹幕"]
        
        # 尝试点击展开 (预先动作)
        try:
            # 快速检查是否有展开按钮
            for btn_text in ["展开", "查看全部", "全文"]:
                if self.device(text=btn_text).exists:
                    self.device(text=btn_text).click()
                    break
        except: pass

        # 等待加载完整
        for i in range(5):
            if any(self.device(textContains=kw).exists or self.device(descriptionContains=kw).exists for kw in detail_keywords):
                detail_loaded = True
                break
            if i == 2:
                # 可能是视频，点击屏幕中心尝试激活 UI
                self.device.click(540, 900)
            time.sleep(0.5)
        
        if not detail_loaded:
            logger.warning("⚠ 警告：详情页特征未发现，提取可能不完整")

        # 2. 获取 UI层级 (核心优化)
        xml_dump_start = time.time()
        xml_content = self.device.dump_hierarchy()
        self._time_method("dump_hierarchy", xml_dump_start)
        
        # 3. 解析 XML
        root = ET.fromstring(xml_content)
        
        content = ""
        likes = "0"
        collects = "0"
        comments = "0"
        author_name = "Unknown"
        image_urls = []
        
        # 收集所有 TextView 节点信息
        text_nodes = []
        
        def parse_nodes(node):
            if node.attrib.get('class') == 'android.widget.TextView':
                text = node.attrib.get('text', '')
                bounds_str = node.attrib.get('bounds', '[0,0][0,0]')
                # 解析 bounds: [x1,y1][x2,y2]
                try:
                    coords = bounds_str.replace('][', ',').replace('[', '').replace(']', '').split(',')
                    x1, y1, x2, y2 = map(int, coords)
                    if text:
                        text_nodes.append({
                            'text': text,
                            'l': x1, 't': y1, 'r': x2, 'b': y2,
                            'cx': (x1 + x2) / 2, 'cy': (y1 + y2) / 2
                        })
                except: pass
            for child in node:
                parse_nodes(child)
                
        parse_nodes(root)
        
        # 4. 分析节点数据
        
        # A. 作者提取 (寻找 "关注" 附近的文本)
        # 策略: 找到包含 "关注" 的节点，取其左侧最近的节点
        follow_node = None
        for n in text_nodes:
            if n['text'] in ["关注", "已关注"]:
                follow_node = n
                break
        
        if follow_node:
            best_dist = 9999
            for n in text_nodes:
                if n == follow_node: continue
                if n['text'] in ["关注", "已关注"] or len(n['text']) > 30: continue
                
                # 垂直接近
                if abs(n['cy'] - follow_node['cy']) < 100:
                    # 在左侧
                    if n['r'] <= follow_node['l'] + 50:
                        dist = follow_node['l'] - n['r']
                        if dist < best_dist:
                            best_dist = dist
                            author_name = n['text']
            logger.info(f"✓ 识别到作者: {author_name}")

        # B. 互动数据提取 (底部区域)
        bottom_nodes = [n for n in text_nodes if n['t'] > 2000] # 假设屏幕高度足够
        bottom_nodes.sort(key=lambda x: x['l']) # 从左到右
        
        for n in bottom_nodes:
            txt = n['text']
            num_txt = ''.join(c for c in txt if c.isdigit() or c in ['.', 'w', 'W'])
            if not num_txt: continue
            
            cx = n['cx']
            if 500 < cx < 750:
                likes = num_txt
            elif 750 < cx < 900:
                collects = num_txt
            elif cx >= 900:
                comments = num_txt

        # C. 正文提取
        # 过滤掉非正文内容
        content_lines = []
        exclude_keywords = ['收藏', '点赞', '评论', '分享', '发布于', '说点什么', '条评论', '关注', author_name]
        
        # 按照垂直位置排序
        content_nodes = [n for n in text_nodes if 200 < n['t'] < 2000]
        content_nodes.sort(key=lambda x: x['t'])
        
        for n in content_nodes:
            t = n['text']
            if len(t) < 2: continue
            if any(k in t for k in exclude_keywords): continue
            
            # 简单的去重策略
            if content_lines and t in content_lines[-1]: continue
            content_lines.append(t)
            
        content = "\n".join(content_lines)

        # 5. 图片提取 (保持原有逻辑但优化等待)
        try:
             # 这里还是需要交互，无法纯靠XML
            share_btn = self.device(description="分享")
            if share_btn.exists:
                share_btn.click()
                # 显式等待 "复制链接"
                copy_link = self.device(text="复制链接")
                if copy_link.wait(timeout=2.0):
                    copy_link.click()
                    # 等待剪贴板更新? 稍微缓一下
                    time.sleep(0.5)
                    share_link = self.device.clipboard
                    if "http" in str(share_link):
                        image_urls = self._fetch_web_images(share_link)
                else:
                    logger.warning("未找到复制链接按钮")
                    self.device.press("back")
        except Exception as e:
            logger.warning(f"⚠ 图片提取异常: {e}")

        self._time_method("_get_detail_data", start_time)
        return {
            "content": content,
            "image_urls": image_urls,
            "likes": likes,
            "collects": collects,
            "comments": comments,
            "author_name": author_name
        }
    
    def _fetch_web_images(self, url: str) -> List[str]:
        """
        从分享链接中解析图片地址
        
        Args:
            url (str): 分享链接URL
            
        Returns:
            List[str]: 图片URL列表
        """
        start_time = time.time()
        try:
            headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1"}
            res = requests.get(url, headers=headers, timeout=10)
            html = res.text
            img_patterns = [
                r'property="og:image" content="(https://[^"]+)"',
                r'"url":"(https://sns-img-[^"]+)"',
                r'"url":"(https://sns-img-qc\.xhscdn\.com/[^"]+)"'
            ]
            found = []
            for pattern in img_patterns:
                matches = re.findall(pattern, html)
                for m in matches:
                    clean_url = m.replace('\\u002F', '/')
                    if clean_url not in found: found.append(clean_url)
            self._time_method("_fetch_web_images", start_time)
            return found
        except:
            self._time_method("_fetch_web_images", start_time)
            return []
    
    def save_note_data(self, data: Dict[str, Union[str, List[str]]], 
                      filename: str = "last_extracted_note.txt", 
                      note_url: str = "") -> None:
        """
        保存笔记数据到文件
        
        Args:
            data (Dict[str, Union[str, List[str]]]): 笔记数据
            filename (str): 保存文件名
            note_url (str): 笔记URL
        """
        start_time = time.time()
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("=" * 50 + "\n")
                f.write("【小红书笔记提取结果】\n")
                f.write("=" * 50 + "\n")
                if note_url:
                    f.write(f"笔记URL: {note_url}\n")
                    f.write("=" * 50 + "\n")
                f.write(f"作者: {data.get('author_name', 'Unknown')}\n")
                f.write(f"点赞数: {data.get('likes', '0')}\n")
                f.write(f"收藏数: {data.get('collects', '0')}\n")
                f.write(f"评论数: {data.get('comments', '0')}\n")
                f.write(f"图片数: {len(data.get('image_urls', []))}\n")
                f.write("=" * 50 + "\n")
                f.write("【正文内容】\n")
                f.write(data['content'])
                f.write("\n" + "=" * 50 + "\n")
                if data['image_urls']:
                    f.write("【图片URL】\n")
                    for i, url in enumerate(data['image_urls'], 1):
                        f.write(f"{i}. {url}\n")
                    f.write("=" * 50 + "\n")
            
            logger.info(f"✓ 笔记数据已保存到: {filename}")
            self._time_method("save_note_data", start_time)
        except Exception as e:
            logger.error(f"✗ 保存笔记数据失败: {e}")
            self._time_method("save_note_data", start_time)
            raise


def extract_note_from_url(url: str, device_serial: Optional[str] = None, enable_time_logging: bool = True) -> Dict[str, Union[str, List[str]]]:
    """
    便捷函数：直接从URL提取笔记数据
    
    Args:
        url (str): 小红书笔记URL
        device_serial (str, optional): 设备序列号
        enable_time_logging (bool, optional): 是否启用耗时打印，默认为True
        
    Returns:
        Dict[str, Union[str, List[str]]]: 笔记数据
    """
    start_time = time.time()
    logger.info(f"[extract_note_from_url] 开始处理URL: {url}")
    extractor = XHSNoteExtractor(device_serial=device_serial, enable_time_logging=enable_time_logging)
    result = extractor.extract_note_data(url=url)
    elapsed_time = time.time() - start_time
    logger.info(f"[extract_note_from_url] 总耗时: {elapsed_time:.3f}秒")
    return result


def convert_url_format(url: str) -> str:
    """
    便捷函数：转换URL格式
    
    Args:
        url (str): 输入URL
        
    Returns:
        str: 转换后的xhsdiscover协议格式URL
    """
    start_time = time.time()
    logger.info(f"[convert_url_format] 开始转换URL: {url}")
    parsed_data = XHSNoteExtractor.parse_xhs_url(url)
    result = XHSNoteExtractor.convert_to_xhsdiscover_format(
        parsed_data["note_id"], 
        parsed_data["xsec_token"]
    )
    elapsed_time = time.time() - start_time
    logger.info(f"[convert_url_format] 耗时: {elapsed_time:.3f}秒，结果: {result}")
    return result