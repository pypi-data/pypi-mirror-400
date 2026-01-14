# 小红书笔记提取器 - 快速开始指南

## 1. 安装

```bash
# 克隆仓库（如果需要）
# git clone <repository-url>
# cd xhs-note-extractor

# 安装依赖
pip install -r requirements.txt

# 安装包（开发模式）
pip install -e .
```

## 2. 连接Android设备

1. 在Android设备上启用**开发者选项**和**USB调试**
2. 通过USB连接设备到电脑
3. 在设备上授权USB调试权限

## 3. 使用CLI工具

### 基本用法

```bash
# 提取笔记并输出到控制台
xhs-extract https://www.xiaohongshu.com/explore/note_id

# 保存到文件
xhs-extract https://www.xiaohongshu.com/explore/note_id -o note_data.json

# 输出CSV格式
xhs-extract https://www.xiaohongshu.com/explore/note_id -f csv -o note_data.csv

# 启用详细输出
xhs-extract https://www.xiaohongshu.com/explore/note_id -v
```

### 查看帮助

```bash
xhs-extract --help
```

## 4. 编程接口使用

```python
from xhs_note_extractor import XHSNoteExtractor
import json

# 创建提取器实例
extractor = XHSNoteExtractor()

# 检查设备连接
if extractor.is_device_connected():
    # 提取笔记数据
    note_data = extractor.extract_note_data("https://www.xiaohongshu.com/explore/note_id")
    print(json.dumps(note_data, ensure_ascii=False, indent=2))
else:
    print("请连接Android设备")
```

## 5. 故障排除

### 设备未连接

如果看到"未检测到Android设备连接"：

1. 检查USB连接
2. 确认已启用USB调试
3. 确认已授权USB调试权限
4. 运行 `adb devices` 检查设备是否被识别

### 无设备模式

CLI工具现在可以优雅处理无设备情况，会显示清晰的错误信息而不是抛出异常。

## 6. 测试

运行测试脚本验证安装：

```bash
python test_cli.py
```

## 7. 示例

运行示例脚本查看使用方法：

```bash
python examples/basic_usage.py
```

## 8. 完成！

现在您可以开始使用小红书笔记提取器了。CLI工具已完全可用，支持JSON和CSV输出格式，并能优雅处理设备连接错误。