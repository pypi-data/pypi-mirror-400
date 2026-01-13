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

def test_all_translations():
    """测试所有翻译键，确保它们在中英文下都能正常工作"""
    print("\n=== 测试所有翻译键 ===")
    
    # 测试键列表
    test_keys = [
        # 防篡改相关
        ("tamper_saving_checksum_failed", "test error"),
        ("tamper_invalid_signature",),
        ("tamper_loading_checksum_failed", "test error"),
        ("tamper_no_valid_checksum",),
        ("tamper_checksum_generated",),
        ("tamper_checksum_generation_failed",),
        ("tamper_verifying_files", "sha512"),
        ("tamper_new_file_detected", "test_file.py"),
        ("tamper_file_verified", "test_file.py"),
        ("tamper_file_tampered", "test_file.py"),
        ("tamper_expected_hash", "expected_hash"),
        ("tamper_actual_hash", "actual_hash"),
        ("tamper_file_missing", "missing_file.py"),
        ("tamper_verifying_integrity",),
        ("tamper_verifying_dependencies",),
        ("tamper_dependency_verified", "test_dep"),
        ("tamper_dependency_missing", "missing_dep"),
        ("tamper_full_security_check",),
        ("tamper_file_integrity_check",),
        ("tamper_dependency_integrity_check",),
        ("tamper_all_checks_passed",),
        ("tamper_security_check_failed",),
        # 邮箱验证相关
        ("email_send_failed", "connection error"),
        # 安全检查相关
        ("security_check_failed_exit",),
        # 测试相关
        ("testing_command", "test_cmd"),
        ("testing_language_switching",),
        ("testing_current_language", "en"),
        ("testing_switched_to", "zh")
    ]
    
    # 测试英文
    print("\n1. 英文翻译测试:")
    set_language("english")
    for key_tuple in test_keys:
        key = key_tuple[0]
        args = key_tuple[1:]
        try:
            translated = _(key, *args)
            print(f"   ✅ {key}: {translated}")
        except Exception as e:
            print(f"   ❌ {key}: 翻译失败 - {e}")
    
    # 测试中文
    print("\n2. 中文翻译测试:")
    set_language("chinese")
    for key_tuple in test_keys:
        key = key_tuple[0]
        args = key_tuple[1:]
        try:
            translated = _(key, *args)
            print(f"   ✅ {key}: {translated}")
        except Exception as e:
            print(f"   ❌ {key}: 翻译失败 - {e}")

if __name__ == "__main__":
    test_language_switch()
    test_commands_with_language()
    test_all_translations()
    print("\n✅ 语言切换测试完成！")
