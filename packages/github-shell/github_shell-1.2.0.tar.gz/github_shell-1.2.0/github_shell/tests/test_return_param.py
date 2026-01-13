#!/usr/bin/env python3

# 测试参数返回功能
import subprocess
import sys

# 测试命令：repos --json
def test_repos_json():
    print("测试命令: repos --json")
    result = subprocess.run([
        sys.executable, "-c", "from github_shell.main import main; main()"
    ], 
    input="repos --json\nexit\n", 
    text=True, 
    capture_output=True)
    
    print("输出:")
    print(result.stdout)
    print("错误:")
    print(result.stderr)
    
    # 检查输出中是否包含JSON格式的数据
    if "[" in result.stdout and "]" in result.stdout:
        print("✅ 测试通过：repos --json 成功返回JSON数据")
    else:
        print("❌ 测试失败：repos --json 没有返回JSON数据")

# 测试命令：repo wjr-2015/github-shell --json
def test_repo_json():
    print("\n测试命令: repo wjr-2015/github-shell --json")
    result = subprocess.run([
        sys.executable, "-c", "from github_shell.main import main; main()"
    ], 
    input="repo wjr-2015/github-shell --json\nexit\n", 
    text=True, 
    capture_output=True)
    
    print("输出:")
    print(result.stdout)
    print("错误:")
    print(result.stderr)
    
    # 检查输出中是否包含JSON格式的数据
    if "{" in result.stdout and "}" in result.stdout:
        print("✅ 测试通过：repo --json 成功返回JSON数据")
    else:
        print("❌ 测试失败：repo --json 没有返回JSON数据")

if __name__ == "__main__":
    test_repos_json()
    test_repo_json()