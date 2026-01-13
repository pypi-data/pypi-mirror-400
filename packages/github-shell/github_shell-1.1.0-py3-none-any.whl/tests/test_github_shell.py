#!/usr/bin/env python3
"""
GitHub仿真Shell测试脚本
用于验证各个命令的返回值功能
"""

from github_shell.commands.repo_commands import RepoCommands
from github_shell.commands.user_commands import UserCommands
from github_shell.commands.search_commands import SearchCommands
from github_shell.commands.org_commands import OrgCommands

def test_repo_commands():
    """测试仓库命令"""
    print("\n=== 测试仓库命令 ===")
    repo_cmds = RepoCommands()
    
    # 测试列出仓库并返回值
    print("\n1. 测试 list_repos 返回值：")
    repos = repo_cmds.list_repos(output_format="return")
    print(f"返回类型: {type(repos)}")
    print(f"返回数量: {len(repos)}")
    if repos:
        print(f"第一个仓库: {repos[0]['name']} (⭐ {repos[0]['stars']})")
    
    # 测试打印功能
    print("\n2. 测试 list_repos 打印功能：")
    repo_cmds.list_repos(output_format="print")

def test_user_commands():
    """测试用户命令"""
    print("\n=== 测试用户命令 ===")
    user_cmds = UserCommands()
    
    # 测试用户信息返回值
    print("\n1. 测试 show_user 返回值：")
    user_info = user_cmds.show_user("octocat", output_format="return")
    print(f"返回类型: {type(user_info)}")
    if user_info:
        print(f"用户名称: {user_info['name']}")
        print(f"关注者数量: {user_info['followers']}")
    
    # 测试打印功能
    print("\n2. 测试 show_user 打印功能：")
    user_cmds.show_user("octocat", output_format="print")

def test_search_commands():
    """测试搜索命令"""
    print("\n=== 测试搜索命令 ===")
    search_cmds = SearchCommands()
    
    # 测试搜索返回值
    print("\n1. 测试 search_repos 返回值：")
    search_results = search_cmds.search_repos("python", output_format="return")
    print(f"返回类型: {type(search_results)}")
    print(f"返回数量: {len(search_results)}")
    if search_results:
        print(f"第一个结果: {search_results[0]['full_name']} (⭐ {search_results[0]['stars']})")
    
    # 测试打印功能
    print("\n2. 测试 search_repos 打印功能：")
    search_cmds.search_repos("python", output_format="print")

def test_org_commands():
    """测试组织命令"""
    print("\n=== 测试组织命令 ===")
    org_cmds = OrgCommands()
    
    # 测试组织信息返回值
    print("\n1. 测试 show_org 返回值：")
    org_info = org_cmds.show_org("github", output_format="return")
    print(f"返回类型: {type(org_info)}")
    if org_info:
        print(f"组织名称: {org_info['name']}")
        print(f"公开仓库: {org_info['public_repos']}")
    
    # 测试打印功能
    print("\n2. 测试 show_org 打印功能：")
    org_cmds.show_org("github", output_format="print")

def main():
    """主测试函数"""
    print("🚀 GitHub仿真Shell 返回值测试")
    
    test_repo_commands()
    test_user_commands()
    test_search_commands()
    test_org_commands()
    
    print("\n✅ 所有测试完成！")

if __name__ == "__main__":
    main()
