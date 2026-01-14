#!/usr/bin/env python3
"""
CLI工具测试脚本
"""

import subprocess
import sys
import os

def test_cli_help():
    """测试CLI帮助命令"""
    print("=== 测试CLI帮助命令 ===")
    try:
        result = subprocess.run(['xhs-extract', '--help'], 
                              capture_output=True, text=True, timeout=10)
        print("✅ CLI帮助命令执行成功")
        print("输出:")
        print(result.stdout)
        return True
    except Exception as e:
        print(f"❌ CLI帮助命令执行失败: {e}")
        return False

def test_cli_with_invalid_url():
    """测试CLI处理无效URL"""
    print("\n=== 测试CLI处理无效URL ===")
    try:
        result = subprocess.run(['xhs-extract', 'invalid-url'], 
                              capture_output=True, text=True, timeout=10)
        print("✅ CLI无效URL测试执行完成")
        print("返回码:", result.returncode)
        print("输出:", result.stdout)
        if result.stderr:
            print("错误:", result.stderr)
        return True
    except Exception as e:
        print(f"❌ CLI无效URL测试执行失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试小红书笔记提取器CLI工具...\n")
    
    # 检查CLI工具是否安装
    try:
        subprocess.run(['xhs-extract', '--help'], capture_output=True, check=True)
        print("✅ CLI工具已正确安装")
    except subprocess.CalledProcessError:
        print("❌ CLI工具未正确安装，请运行: pip install -e .")
        return
    except FileNotFoundError:
        print("❌ CLI工具未找到，请运行: pip install -e .")
        return
    
    # 运行测试
    test_cli_help()
    test_cli_with_invalid_url()
    
    print("\n=== 测试完成 ===")
    print("如果所有测试都通过，CLI工具应该可以正常使用。")
    print("注意: 实际提取功能需要连接Android设备。")

if __name__ == "__main__":
    main()