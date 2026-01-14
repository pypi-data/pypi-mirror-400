#!/usr/bin/env python3
"""
小红书笔记提取器 - 基础使用示例
"""

from xhs_note_extractor import XHSNoteExtractor
import json
import sys

def main():
    # 创建提取器实例
    print("=== 初始化小红书笔记提取器 ===")
    try:
        extractor = XHSNoteExtractor()
        
        # 检查设备连接状态
        if not extractor.is_device_connected():
            print("⚠️  警告: 未检测到Android设备连接")
            print("   请确保:")
            print("   1. Android设备已通过USB连接")
            print("   2. 已启用USB调试模式")
            print("   3. 已授权USB调试权限")
            print("   4. 如需使用CLI工具，请直接运行: xhs-extract <URL>")
            return
        
        print("✅ 设备连接成功")
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return
    
    # 示例1: 提取单个笔记
    print("\n=== 示例1: 提取单个笔记 ===")
    note_url = "https://www.xiaohongshu.com/explore/695d0654000000000b0094e3?xsec_token=ABtNxAHqEd2-vRgXXZf7H_vjY0_svO3V1oI5AlpbSgwMs=&xsec_source=pc_search&source=unknown"  # 替换为实际的笔记URL
    
    try:
        note_data = extractor.extract_note_data(note_url)
        print(f"✅ 提取成功!")
        print(f"   标题: {note_data.get('title', '无标题')}")
        print(f"   点赞数: {note_data.get('likes', 0)}")
        print(f"   收藏数: {note_data.get('collects', 0)}")
        print(f"   评论数: {note_data.get('comments', 0)}")
        print(f"   图片数: {len(note_data.get('image_urls', []))}")
        print(f"   笔记内容: {note_data.get('content', '')[:100]}...")
        print(f"   作者: {note_data.get('author', {}).get('nickname', '未知')}")
    except Exception as e:
        print(f"❌ 提取失败: {e}")
    
    # 示例2: 批量提取笔记
    print("\n=== 示例2: 批量提取笔记 ===")
    note_urls = [
        "https://www.xiaohongshu.com/explore/695ccd5a000000000a02f1f2?xsec_token=ABs2TMlXRspSpWYyYIhgIa676REIkaoiT8F1JJUesGB8g=&xsec_source=pc_search&source=unknown",
        "https://www.xiaohongshu.com/explore/695d9e4a000000002202f0a6?xsec_token=ABtNxAHqEd2-vRgXXZf7H_vsVuDsoUOtqxvBhH91SwAHY=&xsec_source=pc_search&source=unknown",
        # 添加更多笔记URL
    ]
    
    success_count = 0
    for i, url in enumerate(note_urls):
        try:
            print(f"  正在提取笔记 {i+1}...")
            note_data = extractor.extract_note_data(url)
            print(f"✅ 提取成功!")
            print(f"   标题: {note_data.get('title', '无标题')}")
            print(f"   点赞数: {note_data.get('likes', 0)}")
            print(f"   收藏数: {note_data.get('collects', 0)}")
            print(f"   评论数: {note_data.get('comments', 0)}")
            print(f"   图片数: {len(note_data.get('image_urls', []))}")
            print(f"   笔记内容: {note_data.get('content', '')[:100]}...")
            print(f"   作者: {note_data.get('author_name', '未知')}")
            success_count += 1
        except Exception as e:
            print(f"  ❌ 笔记 {i+1} 提取失败: {e}")
    
    print(f"\n📊 批量提取完成: 成功 {success_count}/{len(note_urls)}")
    
    # 示例3: 自定义配置
    print("\n=== 示例3: 使用自定义配置 ===")
    try:
        custom_extractor = XHSNoteExtractor(
            device_serial="b520805"  # 如果需要指定特定设备序列号
        )
        
        if custom_extractor.is_device_connected():
            print("✅ 自定义配置初始化成功")
            # 使用自定义配置提取笔记
            try:
                note_data = custom_extractor.extract_note_data(note_url)
                print(f"✅ 自定义配置提取成功: {note_data.get('title', '无标题')} (点赞: {note_data.get('likes', 0)})")
            except Exception as e:
                print(f"❌ 自定义配置提取失败: {e}")
        else:
            print("⚠️  自定义配置: 设备连接失败")
            
    except Exception as e:
        print(f"❌ 自定义配置初始化失败: {e}")
    
    # 示例4: 使用CLI工具（推荐方式）
    print("\n=== 示例4: 使用CLI工具（推荐）===")
    print("在终端中运行以下命令:")
    print("  # 提取笔记并输出JSON格式")
    print("  xhs-extract https://www.xiaohongshu.com/explore/xxx")
    print("")
    print("  # 提取笔记并保存到文件")
    print("  xhs-extract https://www.xiaohongshu.com/explore/xxx -o note.json")
    print("")
    print("  # 提取笔记并输出CSV格式")
    print("  xhs-extract https://www.xiaohongshu.com/explore/xxx -f csv")
    print("")
    print("  # 启用详细输出模式")
    print("  xhs-extract https://www.xiaohongshu.com/explore/xxx -v")
    print("")
    print("  # 获取帮助")
    print("  xhs-extract --help")

if __name__ == "__main__":
    main()