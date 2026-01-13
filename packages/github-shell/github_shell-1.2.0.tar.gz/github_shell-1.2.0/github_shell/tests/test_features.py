#!/usr/bin/env python3

# 测试新功能：命令测试和语言切换
import subprocess
import sys

# 测试命令测试功能
def test_command_testing():
    print("测试功能：命令测试")
    result = subprocess.run([
        sys.executable, "-c", "from github_shell.main import main; main()"
    ], 
    input="test test-lang\nexit\n", 
    text=True, 
    capture_output=True, 
    encoding='utf-8',
    errors='replace')
    
    print("输出:")
    print(result.stdout)
    
    # 检查输出中是否包含语言切换测试信息
    if "Testing language switching" in result.stdout:
        print("✅ 命令测试功能正常")
    else:
        print("❌ 命令测试功能失败")

# 测试语言切换功能
def test_language_switching():
    print("\n测试功能：语言切换")
    result = subprocess.run([
        sys.executable, "-c", "from github_shell.main import main; main()"
    ], 
    input="language zh\nhelp\nlanguage en\nhelp\nexit\n", 
    text=True, 
    capture_output=True, 
    encoding='utf-8',
    errors='replace')
    
    print("输出:")
    print(result.stdout)
    
    # 检查输出中是否包含中英文帮助信息
    if "仓库操作" in result.stdout and "Repository Operations" in result.stdout:
        print("✅ 语言切换功能正常")
    else:
        print("❌ 语言切换功能失败")

if __name__ == "__main__":
    test_command_testing()
    test_language_switching()