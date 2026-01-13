#!/usr/bin/env python3
"""
语言切换测试脚本
"""

from github_shell.utils.language import _, get_language, set_language
from github_shell.commands.repo_commands import RepoCommands

def test_language_switch():
    """测试语言切换功能"""
    print("=== 测试语言切换功能 ===")
    
    # 初始语言应该是英文
    print(f"\n1. 初始语言: {get_language()}")
    print(f"   欢迎消息: {_('welcome')}")
    
    # 切换到中文
    print("\n2. 切换到中文...")
    set_language("zh")
    print(f"   当前语言: {get_language()}")
    print(f"   欢迎消息: {_('welcome')}")
    print(f"   帮助提示: {_('help_tip')}")
    
    # 切换回英文
    print("\n3. 切换回英文...")
    set_language("en")
    print(f"   当前语言: {get_language()}")
    print(f"   Welcome message: {_('welcome')}")
    print(f"   Help tip: {_('help_tip')}")
    
    # 测试无效语言
    print("\n4. 测试无效语言...")
    result = set_language("invalid_lang")
    print(f"   设置结果: {result}")
    print(f"   当前语言: {get_language()}")
    print(f"   消息: {_('welcome')}")

def test_commands_with_language():
    """测试命令在不同语言下的输出"""
    print("\n=== 测试命令在不同语言下的输出 ===")
    
    repo_cmds = RepoCommands()
    
    # 英文环境测试
    print("\n1. 英文环境测试:")
    set_language("en")
    print(f"   当前语言: {get_language()}")
    # 只返回值，不打印
    repos = repo_cmds.list_repos(output_format="return")
    print(f"   列出仓库返回数量: {len(repos)}")
    
    # 中文环境测试
    print("\n2. 中文环境测试:")
    set_language("zh")
    print(f"   当前语言: {get_language()}")
    # 只返回值，不打印
    repos = repo_cmds.list_repos(output_format="return")
    print(f"   列出仓库返回数量: {len(repos)}")

if __name__ == "__main__":
    test_language_switch()
    test_commands_with_language()
    print("\n✅ 语言切换测试完成！")
