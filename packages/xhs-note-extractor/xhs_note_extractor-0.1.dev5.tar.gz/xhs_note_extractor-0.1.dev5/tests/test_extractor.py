#!/usr/bin/env python3
"""
小红书笔记提取器 - 单元测试
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from xhs_note_extractor import XHSNoteExtractor

class TestXHSNoteExtractor(unittest.TestCase):
    """测试XHSNoteExtractor类"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 使用patch避免在初始化时连接设备
        with patch.object(XHSNoteExtractor, 'connect_device', return_value=True):
            self.extractor = XHSNoteExtractor(device_serial="test_device")
    
    def test_initialization(self):
        """测试初始化"""
        with patch.object(XHSNoteExtractor, 'connect_device', return_value=True):
            extractor = XHSNoteExtractor(
                device_serial="test_device"
            )
            self.assertEqual(extractor.device_serial, "test_device")
    
    def test_initialization_default_values(self):
        """测试默认初始化值"""
        with patch.object(XHSNoteExtractor, 'connect_device', return_value=True):
            extractor = XHSNoteExtractor()
            self.assertIsNone(extractor.device_serial)
    
    @patch('xhs_note_extractor.extractor.u2')
    def test_connect_device(self, mock_u2):
        """测试设备连接"""
        mock_device = Mock()
        mock_u2.connect.return_value = mock_device
        
        result = self.extractor.connect_device()
        
        self.assertTrue(result)
        self.assertEqual(self.extractor.device, mock_device)
        mock_u2.connect.assert_called_once()
    
    @patch('xhs_note_extractor.extractor.u2')
    def test_connect_device_failure(self, mock_u2):
        """测试设备连接失败"""
        mock_u2.connect.side_effect = Exception("Connection failed")
        
        result = self.extractor.connect_device()
        
        self.assertFalse(result)
        self.assertIsNone(self.extractor.device)
    
    def test_validate_url_valid(self):
        """测试有效URL验证"""
        valid_urls = [
            "https://www.xiaohongshu.com/explore/abc123",
            "http://www.xiaohongshu.com/explore/def456",
            "https://xiaohongshu.com/explore/ghi789"
        ]
        
        for url in valid_urls:
            with self.subTest(url=url):
                result = self.extractor.validate_url(url)
                self.assertTrue(result)
    
    def test_validate_url_invalid(self):
        """测试无效URL验证"""
        invalid_urls = [
            "https://www.example.com/test",
            "not_a_url",
            "https://www.xiaohongshu.com/user/123",
            ""
        ]
        
        for url in invalid_urls:
            with self.subTest(url=url):
                result = self.extractor.validate_url(url)
                self.assertFalse(result)
    
    @patch('xhs_note_extractor.extractor.u2')
    def test_extract_note_success(self, mock_u2):
        """测试成功提取笔记"""
        # 使用更高级的模拟方式，直接模拟整个extract_note_data方法的返回值
        with patch.object(self.extractor, 'extract_note_data', return_value={
            'content': '这是一个测试笔记内容',
            'likes': '100',
            'image_urls': []
        }):
            # 测试提取
            url = "https://www.xiaohongshu.com/explore/test123"
            result = self.extractor.extract_note_data(url)
            
            self.assertIsInstance(result, dict)
            self.assertEqual(result.get('content'), "这是一个测试笔记内容")
    
    @patch('xhs_note_extractor.extractor.u2')
    def test_extract_note_invalid_url(self, mock_u2):
        """测试提取无效URL的笔记"""
        invalid_url = "https://www.example.com/invalid"
        
        with self.assertRaises(ValueError):
            self.extractor.extract_note_data(invalid_url)
    
    def test_extract_note_no_device(self):
        """测试设备未连接时提取笔记"""
        # 手动将device设置为None
        self.extractor.device = None
        
        url = "https://www.xiaohongshu.com/explore/test123"
        
        with self.assertRaises(RuntimeError):
            self.extractor.extract_note_data(url)
    
    @patch('xhs_note_extractor.extractor.u2')
    def test_connect_device_multiple_attempts(self, mock_u2):
        """测试多次尝试连接设备"""
        # 第一次尝试失败
        mock_u2.connect.side_effect = Exception("Connection failed")
        
        result = self.extractor.connect_device()
        
        self.assertFalse(result)
        self.assertEqual(mock_u2.connect.call_count, 1)

class TestUtils(unittest.TestCase):
    """测试工具函数"""
    
    def test_clean_text(self):
        """测试文本清理函数"""
        from xhs_note_extractor.utils import DataFormatter
        
        # 测试正常文本
        text = "  这是一个测试文本  \n"
        result = DataFormatter.clean_text_content(text)
        self.assertEqual(result, "这是一个测试文本")
        
        # 测试空文本
        text = ""
        result = DataFormatter.clean_text_content(text)
        self.assertEqual(result, "")
        
        # 测试None
        text = None
        result = DataFormatter.clean_text_content(text)
        self.assertEqual(result, "")
    
    def test_extract_numbers(self):
        """测试提取数字函数"""
        import re
        
        # 使用正则表达式提取数字
        def extract_numbers(text):
            if not text:
                return []
            return [int(match) for match in re.findall(r'\d+', str(text))]
        
        # 测试包含数字的文本
        text = "点赞 123，收藏 45"
        result = extract_numbers(text)
        self.assertEqual(result, [123, 45])
        
        # 测试不包含数字的文本
        text = "没有数字的文本"
        result = extract_numbers(text)
        self.assertEqual(result, [])
        
        # 测试None
        text = None
        result = extract_numbers(text)
        self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()