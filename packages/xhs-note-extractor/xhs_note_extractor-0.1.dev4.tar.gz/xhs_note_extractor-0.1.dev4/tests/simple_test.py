#!/usr/bin/env python3
"""
简单测试脚本，用于验证xhs-note-extractor包的基本功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from xhs_note_extractor import XHSNoteExtractor
    from xhs_note_extractor.utils import DataFormatter
    print("✅ 成功导入 xhs_note_extractor 包")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

def test_utils():
    """测试工具函数"""
    print("测试工具函数...")
    
    # 测试 clean_text_content
    test_text = "  Hello  World  \n  \t  "
    cleaned = DataFormatter.clean_text_content(test_text)
    expected = "Hello World"
    assert cleaned == expected, f"clean_text_content 失败: 期望 '{expected}', 得到 '{cleaned}'"
    print("✅ clean_text_content 测试通过")
    
    # 测试 format_like_count
    test_like_text = "1.2w"
    formatted = DataFormatter.format_like_count(test_like_text)
    expected = "12000"
    assert formatted == expected, f"format_like_count 失败: 期望 {expected}, 得到 {formatted}"
    print("✅ format_like_count 测试通过")

def test_extractor_class():
    """测试提取器类"""
    print("测试提取器类...")
    
    # 测试静态方法
    valid_url = "https://www.xiaohongshu.com/explore/123456789"
    invalid_url = "https://example.com"
    
    # 测试URL解析
    try:
        parsed = XHSNoteExtractor.parse_xhs_url(valid_url)
        assert "note_id" in parsed, "URL解析应该包含note_id"
        print("✅ URL解析测试通过")
    except Exception as e:
        print(f"❌ URL解析测试失败: {e}")
    
    # 测试无效URL
    try:
        XHSNoteExtractor.parse_xhs_url(invalid_url)
        print("❌ 无效URL应该抛出异常")
    except ValueError:
        print("✅ 无效URL测试通过")
    except Exception as e:
        print(f"❌ 无效URL测试失败: {e}")

def main():
    """运行所有测试"""
    print("开始运行 xhs-note-extractor 简单测试...\n")
    
    try:
        test_utils()
        print()
        test_extractor_class()
        print("\n🎉 所有测试都通过了！")
        return 0
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())