#!/usr/bin/env python3
"""
小红书笔记提取器 - 高级使用示例
"""

import json
import csv
from datetime import datetime
from xhs_note_extractor import XHSNoteExtractor

def save_to_json(data, filename):
    """将数据保存为JSON文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"数据已保存到 {filename}")

def save_to_csv(notes_data, filename):
    """将笔记数据保存为CSV文件"""
    if not notes_data:
        print("没有数据可保存")
        return
    
    # 获取所有可能的字段
    all_fields = set()
    for note in notes_data:
        all_fields.update(note.keys())
    
    # 标准字段顺序
    fieldnames = ['content', 'image_urls', 'likes']
    # 添加其他字段
    for field in all_fields:
        if field not in fieldnames:
            fieldnames.append(field)
    
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for note in notes_data:
            writer.writerow(note)
    
    print(f"数据已保存到 {filename}")

def extract_user_notes(user_id, max_notes=10):
    """提取指定用户的所有笔记"""
    extractor = XHSNoteExtractor()
    
    try:
        # 这里应该实现获取用户笔记列表的逻辑
        # 由于小红书API限制，这里只是一个示例框架
        note_urls = [
            f"https://www.xiaohongshu.com/explore/note1",
            f"https://www.xiaohongshu.com/explore/note2",
            # ... 更多笔记URL
        ]
        
        notes_data = []
        for i, url in enumerate(note_urls[:max_notes]):
            print(f"正在提取第 {i+1} 个笔记...")
            try:
                note_data = extractor.extract_note_data(url)
                notes_data.append(note_data)
                print(f"✓ 成功提取: 点赞数 {note_data.get('likes', 0)}, 图片数 {len(note_data.get('image_urls', []))}")
            except Exception as e:
                print(f"✗ 提取失败: {e}")
        
        return notes_data
    
    except Exception as e:
        print(f"获取用户笔记失败: {e}")
        return []

def search_and_extract(keyword, max_results=10):
    """搜索关键词并提取相关笔记"""
    extractor = XHSNoteExtractor()
    
    try:
        # 这里应该实现搜索功能的逻辑
        # 由于小红书API限制，这里只是一个示例框架
        search_results = [
            "https://www.xiaohongshu.com/explore/result1",
            "https://www.xiaohongshu.com/explore/result2",
            # ... 更多搜索结果
        ]
        
        notes_data = []
        for i, url in enumerate(search_results[:max_results]):
            print(f"正在提取搜索结果 {i+1}...")
            try:
                note_data = extractor.extract_note_data(url)
                notes_data.append(note_data)
                print(f"✓ 成功提取: 点赞数 {note_data.get('likes', 0)}, 图片数 {len(note_data.get('image_urls', []))}")
            except Exception as e:
                print(f"✗ 提取失败: {e}")
        
        return notes_data
    
    except Exception as e:
        print(f"搜索失败: {e}")
        return []

def main():
    extractor = XHSNoteExtractor()
    
    # 示例1: 批量提取并保存数据
    print("=== 示例1: 批量提取并保存数据 ===")
    note_urls = [
        "https://www.xiaohongshu.com/explore/example1",
        "https://www.xiaohongshu.com/explore/example2",
        # 添加更多笔记URL
    ]
    
    all_notes = []
    for i, url in enumerate(note_urls):
        try:
            note_data = extractor.extract_note_data(url=url)
            all_notes.append(note_data)
            print(f"成功提取笔记 {i+1}: {note_data.get('title', '无标题')}")
        except Exception as e:
            print(f"笔记 {i+1} 提取失败: {e}")
    
    if all_notes:
        # 保存为JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_to_json(all_notes, f"notes_{timestamp}.json")
        
        # 保存为CSV
        save_to_csv(all_notes, f"notes_{timestamp}.csv")
    
    # 示例2: 使用代理和自定义配置
    print("\n=== 示例2: 使用代理和自定义配置 ===")
    proxy_extractor = XHSNoteExtractor(device_serial="custom_device")
    
    try:
        note_data = proxy_extractor.extract_note_data(url="https://www.xiaohongshu.com/explore/example")
        print(f"使用代理提取成功: {note_data.get('title', '无标题')}")
    except Exception as e:
        print(f"代理提取失败: {e}")
    
    # 示例3: 错误处理和重试机制
    print("\n=== 示例3: 错误处理和重试机制 ===")
    urls_with_errors = [
        "https://www.xiaohongshu.com/explore/valid_url",
        "https://www.xiaohongshu.com/explore/invalid_url",
        "https://www.xiaohongshu.com/explore/another_valid_url",
    ]
    
    for url in urls_with_errors:
        retry_count = 0
        max_retries = 3
        
        while retry_count < max_retries:
            try:
                note_data = extractor.extract_note_data(url=url)
                print(f"✓ 成功提取: {note_data.get('title', '无标题')}")
                break
            except Exception as e:
                retry_count += 1
                if retry_count < max_retries:
                    print(f"⚠ 第{retry_count}次重试: {e}")
                else:
                    print(f"✗ 最终失败: {e}")

if __name__ == "__main__":
    main()