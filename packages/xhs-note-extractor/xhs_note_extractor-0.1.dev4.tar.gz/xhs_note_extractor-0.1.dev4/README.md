# 小红书笔记提取器 (Xiaohongshu Note Extractor)

一个用于从小红书提取笔记数据的Python工具，支持命令行界面和编程接口。

## 功能特性

- 🔍 从小红书笔记URL提取详细数据
- 📊 支持JSON和CSV输出格式
- 🖥️ 命令行界面支持
- 🔧 可配置的设备连接选项
- 📱 Android设备集成（通过uiautomator2）
- 🛡️ 优雅的错误处理和设备状态检查

## 安装

### 从源码安装

```bash
# 克隆仓库
git clone <repository-url>
cd xhs-note-extractor

# 安装依赖
pip install -r requirements.txt

# 安装包（开发模式）
pip install -e .
```

### 依赖要求

- Python 3.7+
- Android设备（用于完整功能）
- ADB工具

## 使用方法

### 命令行界面（CLI）

安装完成后，可以直接使用 `xhs-extract` 命令：

```bash
# 提取笔记并输出到控制台（JSON格式）
xhs-extract https://www.xiaohongshu.com/explore/note_id

# 保存到文件
xhs-extract https://www.xiaohongshu.com/explore/note_id -o note_data.json

# 输出CSV格式
xhs-extract https://www.xiaohongshu.com/explore/note_id -f csv -o note_data.csv

# 启用详细输出模式
xhs-extract https://www.xiaohongshu.com/explore/note_id -v

# 查看帮助
xhs-extract --help
```

### 编程接口

```python
from xhs_note_extractor import XHSNoteExtractor
import json

# 创建提取器实例
extractor = XHSNoteExtractor()

# 检查设备连接状态
if extractor.is_device_connected():
    # 提取笔记数据
    note_data = extractor.extract_note_data("https://www.xiaohongshu.com/explore/note_id")
    print(json.dumps(note_data, ensure_ascii=False, indent=2))
else:
    print("请连接Android设备并启用USB调试")
```

## 输出数据结构

提取的数据包含以下字段：

```json
{
  "title": "笔记标题",
  "content": "笔记完整内容",
  "author": {
    "nickname": "作者昵称",
    "user_id": "用户ID"
  },
  "likes": 100,
  "collects": 50,
  "comments": 25,
  "shares": 10,
  "image_urls": [
    "图片URL1",
    "图片URL2"
  ],
  "video_url": "视频URL（如果有）",
  "tags": ["标签1", "标签2"],
  "publish_time": "发布时间",
  "note_id": "笔记ID"
}
```

## 设备连接

### 连接Android设备

1. 在Android设备上启用**开发者选项**和**USB调试**
2. 通过USB连接设备到电脑
3. 授权USB调试权限（设备上会弹出提示）

### 检查设备状态

```bash
# 使用ADB检查设备
adb devices

# 使用CLI工具检查
xhs-extract --help  # 会显示设备连接状态
```

## 故障排除

### 设备连接问题

如果CLI工具提示设备未连接：

1. 检查USB连接是否正常
2. 确认已在设备上启用USB调试
3. 确认已授权USB调试权限
4. 尝试重新插拔USB线缆
5. 重启ADB服务：
   ```bash
   adb kill-server
   adb start-server
   ```

### 权限问题

在Linux/Mac上，可能需要为ADB添加权限：

```bash
sudo adb kill-server
sudo adb start-server
```

## 示例

查看 `examples/basic_usage.py` 文件获取更多使用示例：

```bash
# 运行示例
python examples/basic_usage.py
```

## 开发

### 项目结构

```
xhs-note-extractor/
├── xhs_note_extractor/
│   ├── __init__.py
│   ├── cli.py          # 命令行界面
│   ├── extractor.py    # 核心提取器
│   └── utils.py        # 工具函数
├── examples/
│   └── basic_usage.py  # 使用示例
├── tests/
├── requirements.txt
├── setup.py
└── README.md
```

### 运行测试

```bash
# 运行示例
python examples/basic_usage.py

# 使用CLI工具
xhs-extract --help
```

## 注意事项

- 本工具仅供学习和研究使用
- 请遵守小红书的使用条款和API限制
- 过度频繁的请求可能导致IP被封禁
- 建议在合理范围内使用，避免对平台造成负担

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！