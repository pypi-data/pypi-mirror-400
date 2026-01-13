#!/usr/bin/env python3
"""
邮箱验证码测试脚本
用于验证验证码生成和验证功能
"""

import time
from github_shell.utils.email_verification import (
    email_verifier,
    generate_and_send_verification,
    verify_code
)

def test_verification_code_generation():
    """测试验证码生成功能"""
    print("=== 测试验证码生成 ===")
    
    # 测试6位验证码
    code = email_verifier.generate_verification_code()
    print(f"1. 6位验证码: {code}")
    assert len(code) == 6, f"验证码长度应为6位，实际为{len(code)}位"
    assert code.isalnum(), "验证码应只包含字母和数字"
    
    # 测试8位验证码
    code_8 = email_verifier.generate_verification_code(8)
    print(f"2. 8位验证码: {code_8}")
    assert len(code_8) == 8, f"验证码长度应为8位，实际为{len(code_8)}位"
    
    # 测试10位验证码
    code_10 = email_verifier.generate_verification_code(10)
    print(f"3. 10位验证码: {code_10}")
    assert len(code_10) == 10, f"验证码长度应为10位，实际为{len(code_10)}位"
    
    print("✅ 验证码生成测试通过")
    return True

def test_code_validation():
    """测试验证码验证功能"""
    print("\n=== 测试验证码验证 ===")
    
    # 生成测试验证码
    code = "123456"
    
    # 测试1: 正确的验证码
    current_time = time.time()
    expiry_time = current_time + 300  # 5分钟后过期
    is_valid = email_verifier.validate_code(code, code, expiry_time)
    print(f"1. 正确验证码验证结果: {is_valid}")
    assert is_valid, "正确验证码验证失败"
    
    # 测试2: 错误的验证码
    is_valid = email_verifier.validate_code("wrong_code", code, expiry_time)
    print(f"2. 错误验证码验证结果: {is_valid}")
    assert not is_valid, "错误验证码验证通过"
    
    # 测试3: 过期的验证码
    expired_time = current_time - 60  # 1分钟前过期
    is_valid = email_verifier.validate_code(code, code, expired_time)
    print(f"3. 过期验证码验证结果: {is_valid}")
    assert not is_valid, "过期验证码验证通过"
    
    print("✅ 验证码验证测试通过")
    return True

def test_generate_and_verify():
    """测试生成和验证验证码的整体流程"""
    print("\n=== 测试生成和验证验证码流程 ===")
    
    # 注意：我们只测试generate_and_verify的验证部分，不实际发送邮件
    # 因为实际发送邮件需要正确的SMTP配置
    
    # 生成验证码和过期时间
    test_code = "ABC123"
    expiry_time = time.time() + 300  # 5分钟后过期
    
    # 测试验证
    is_valid = verify_code(test_code, test_code, expiry_time)
    print(f"1. 工具函数验证结果: {is_valid}")
    assert is_valid, "工具函数验证失败"
    
    # 测试错误验证
    is_valid = verify_code("wrong", test_code, expiry_time)
    print(f"2. 工具函数错误验证结果: {is_valid}")
    assert not is_valid, "工具函数错误验证通过"
    
    print("✅ 生成和验证验证码流程测试通过")
    return True

def main():
    """主测试函数"""
    print("🚀 邮箱验证码测试")
    
    tests = [
        test_verification_code_generation,
        test_code_validation,
        test_generate_and_verify
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} 测试失败: {e}")
            failed += 1
    
    print(f"\n📊 测试结果: 共 {len(tests)} 项测试，{passed} 项通过，{failed} 项失败")
    
    if failed == 0:
        print("🎉 所有测试通过！")
        return True
    else:
        print("❌ 部分测试失败！")
        return False

if __name__ == "__main__":
    main()
