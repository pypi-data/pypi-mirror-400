#!/usr/bin/env python3
"""
系统命令测试脚本
用于验证系统命令功能，包括stop命令
"""

import os
import sys
import subprocess
import time
from github_shell.utils.config import set_mode, reset_config

def test_stop_command():
    """测试stop命令功能"""
    print("\n=== 测试stop命令功能 ===")
    
    # 确保在开发者模式下
    set_mode("developer")
    
    # 测试stop命令语法（通过检查main.py中的实现）
    print("\n1. 测试stop命令语法：")
    main_py_path = os.path.join(os.path.dirname(__file__), "..", "main.py")
    with open(main_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查stop命令是否存在于main.py中
    assert "elif cmd == \"stop\" or cmd == \"shutdown\"" in content, "stop命令语法未找到"
    print("✅ stop命令语法正确实现")
    
    # 检查stop命令是否有开发者模式限制
    assert "get_mode() != \"developer\"" in content, "stop命令缺少开发者模式限制"
    assert "developer_commands_restricted" in content, "stop命令缺少开发者命令限制文本"
    print("✅ stop命令有开发者模式限制")


def test_system_commands():
    """测试系统命令"""
    print("\n=== 测试系统命令 ===")
    
    # 测试1: 检查帮助信息中是否包含stop命令
    print("\n1. 测试帮助信息中stop命令：")
    from github_shell.utils.config import HELP_TEXT
    assert "stop/shutdown" in HELP_TEXT, "帮助信息中缺少stop命令"
    print("✅ 帮助信息中包含stop命令")
    
    # 测试2: 检查语言文件中是否包含stop命令翻译
    print("\n2. 测试语言文件中stop命令翻译：")
    from github_shell.utils.language import LANGUAGES
    for lang, translations in LANGUAGES.items():
        assert "stop_msg" in translations, f"{lang}语言中缺少stop_msg翻译"
    print("✅ 所有语言中都包含stop_msg翻译")


def main():
    """主测试函数"""
    print("🚀 系统命令测试")
    
    success = True
    success &= test_stop_command()
    success &= test_system_commands()
    
    if success:
        print("\n✅ 所有测试通过！")
        sys.exit(0)
    else:
        print("\n❌ 测试失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()