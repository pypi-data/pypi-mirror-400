#!/usr/bin/env python3
"""
配置管理和模式切换测试脚本
用于验证配置管理功能和开发者模式/用户模式的切换
"""

from github_shell.utils.config import (
    reset_config, set_mode,
    set_config, get_mode, get_config
)

def test_config_management():
    """测试配置管理功能"""
    print("\n=== 测试配置管理功能 ===")
    
    # 确保初始状态正确
    set_mode("developer")  # 切换到开发者模式才能重置配置
    reset_config()  # 重置配置
    
    # 测试1: 配置项获取
    print("\n1. 测试配置项获取：")
    mode = get_config("mode")
    print(f"当前模式: {mode}")
    assert mode == "user", f"模式获取错误，应为 'user'，实际为 '{mode}'"
    print("✅ 配置项获取正确")
    
    # 测试2: 配置项设置
    print("\n2. 测试配置项设置：")
    set_mode("developer")  # 切换到开发者模式
    result = set_config("language", "chinese")
    print(f"设置语言返回: {result}")
    assert result is True, "配置项设置失败"
    language = get_config("language")
    print(f"设置后语言: {language}")
    assert language == "chinese", f"语言设置错误，应为 'chinese'，实际为 '{language}'"
    print("✅ 配置项设置正确")
    
    # 测试3: 验证码配置项
    print("\n3. 测试验证码配置项：")
    # 检查是否存在验证码相关配置
    smtp_server = get_config("smtp_server")
    print(f"SMTP服务器: {smtp_server}")
    assert smtp_server is not None, "SMTP服务器配置缺失"
    
    sender_email = get_config("sender_email")
    print(f"发件人邮箱: {sender_email}")
    assert sender_email is not None, "发件人邮箱配置缺失"
    
    recipient_email = get_config("recipient_email")
    print(f"收件人邮箱: {recipient_email}")
    assert recipient_email is not None, "收件人邮箱配置缺失"
    
    print("✅ 验证码配置项存在")

def test_mode_switching():
    """测试模式切换功能"""
    print("\n=== 测试模式切换功能 ===")
    
    # 测试1: 切换到开发者模式
    print("\n1. 测试切换到开发者模式：")
    result = set_mode("developer")
    print(f"切换到开发者模式返回: {result}")
    assert result is True, "切换到开发者模式失败"
    mode = get_mode()
    print(f"当前模式: {mode}")
    assert mode == "developer", f"模式切换错误，应为 'developer'，实际为 '{mode}'"
    print("✅ 切换到开发者模式成功")
    
    # 测试2: 切换到用户模式
    print("\n2. 测试切换到用户模式：")
    result = set_mode("user")
    print(f"切换到用户模式返回: {result}")
    assert result is True, "切换到用户模式失败"
    mode = get_mode()
    print(f"当前模式: {mode}")
    assert mode == "user", f"模式切换错误，应为 'user'，实际为 '{mode}'"
    print("✅ 切换到用户模式成功")
    
    # 测试3: 无效模式切换
    print("\n3. 测试无效模式切换：")
    result = set_mode("invalid_mode")
    print(f"无效模式切换返回: {result}")
    assert result is False, "无效模式切换应该失败"
    print("✅ 无效模式切换处理正确")

def test_core_config_protection():
    """测试核心配置保护功能"""
    print("\n=== 测试核心配置保护功能 ===")
    
    # 测试1: 用户模式无法修改核心配置
    print("\n1. 测试用户模式核心配置保护：")
    set_mode("user")  # 切换到用户模式
    
    # 测试修改验证码配置
    result = set_config("smtp_server", "test_server")
    print(f"用户模式修改验证码配置返回: {result}")
    assert result is True, "用户模式应该可以修改验证码配置"
    
    # 测试修改开发者锁定配置
    result = set_config("developer_locked", True)
    print(f"用户模式修改开发者锁定配置返回: {result}")
    assert result is False, "用户模式应该无法修改开发者锁定配置"
    print("✅ 用户模式核心配置保护生效")
    
    # 测试2: 开发者模式可以修改所有配置
    print("\n2. 测试开发者模式配置访问：")
    set_mode("developer")  # 切换到开发者模式
    
    # 测试修改验证码配置
    result = set_config("smtp_server", "test_server")
    print(f"开发者模式修改验证码配置返回: {result}")
    assert result is True, "开发者模式应该可以修改验证码配置"
    
    # 测试修改开发者锁定配置
    result = set_config("developer_locked", False)
    print(f"开发者模式修改开发者锁定配置返回: {result}")
    assert result is True, "开发者模式应该可以修改开发者锁定配置"
    print("✅ 开发者模式可以修改所有配置，访问正常")
    
    # 恢复默认配置
    reset_config()

def main():
    """主测试函数"""
    print("🚀 配置管理和模式切换测试")
    
    test_config_management()
    test_mode_switching()
    test_core_config_protection()
    
    print("\n✅ 所有测试完成！")

if __name__ == "__main__":
    main()