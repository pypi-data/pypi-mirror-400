#!/usr/bin/env python3
"""
防篡改机制测试脚本
用于验证文件完整性验证和依赖检查功能
"""

import os
import tempfile
from github_shell.utils.tamper_proof import (
    calculate_file_hash,
    generate_checksums,
    save_checksums,
    load_checksums,
    verify_checksums,
    update_checksums,
    tamper_proof_check,
    verify_dependencies,
    full_security_check,
    signature_manager
)

def test_file_hash_calculation():
    """测试文件哈希计算功能"""
    print("=== 测试文件哈希计算 ===")
    
    # 创建临时文件用于测试
    with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as f:
        f.write("test content")
        temp_file_path = f.name
    
    try:
        # 测试SHA-512哈希
        sha512_hash = calculate_file_hash(temp_file_path, "sha512")
        print(f"1. SHA-512哈希: {sha512_hash}")
        assert sha512_hash is not None, "SHA-512哈希计算失败"
        assert len(sha512_hash) == 128, "SHA-512哈希长度不正确"
        
        # 测试SHA-256哈希
        sha256_hash = calculate_file_hash(temp_file_path, "sha256")
        print(f"2. SHA-256哈希: {sha256_hash}")
        assert sha256_hash is not None, "SHA-256哈希计算失败"
        assert len(sha256_hash) == 64, "SHA-256哈希长度不正确"
        
        # 测试默认哈希（应该是SHA-512）
        default_hash = calculate_file_hash(temp_file_path)
        print(f"3. 默认哈希: {default_hash}")
        assert default_hash == sha512_hash, "默认哈希算法不是SHA-512"
        
        # 测试不存在的文件
        non_existent_hash = calculate_file_hash("non_existent_file.txt")
        print(f"4. 不存在文件的哈希: {non_existent_hash}")
        assert non_existent_hash is None, "不存在文件的哈希应该为None"
        
        print("✅ 文件哈希计算测试通过")
        return True
    finally:
        # 清理临时文件
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

def test_signature_management():
    """测试签名生成和验证功能"""
    print("\n=== 测试签名管理 ===")
    
    # 测试数据
    test_data = "test data for signature"
    
    # 生成签名
    signature = signature_manager.generate_signature(test_data)
    print(f"1. 生成签名: {signature}")
    assert len(signature) == 128, "签名长度不正确"
    
    # 验证正确的签名
    is_valid = signature_manager.verify_signature(test_data, signature)
    print(f"2. 验证正确签名: {is_valid}")
    assert is_valid, "正确签名验证失败"
    
    # 验证错误的签名
    invalid_signature = "invalid_signature" * 10  # 确保长度足够
    is_valid = signature_manager.verify_signature(test_data, invalid_signature)
    print(f"3. 验证错误签名: {is_valid}")
    assert not is_valid, "错误签名验证通过"
    
    print("✅ 签名管理测试通过")
    return True

def test_checksum_generation():
    """测试校验和生成功能"""
    print("\n=== 测试校验和生成 ===")
    
    # 生成校验和
    checksums = generate_checksums()
    print(f"1. 校验和生成: {'成功' if checksums else '失败'}")
    assert checksums is not None, "校验和生成失败"
    assert isinstance(checksums, dict), "校验和应该是字典类型"
    assert "_metadata" in checksums, "校验和应包含元数据"
    assert "files" in checksums, "校验和应包含文件列表"
    assert "signature" in checksums, "校验和应包含签名"
    
    # 验证元数据
    metadata = checksums["_metadata"]
    print(f"2. 元数据算法: {metadata.get('algorithm')}")
    print(f"3. 元数据版本: {metadata.get('version')}")
    assert metadata.get('algorithm') == "sha512", "默认算法应为SHA-512"
    
    print("✅ 校验和生成测试通过")
    return True

def test_checksum_save_load():
    """测试校验和保存和加载功能"""
    print("\n=== 测试校验和保存和加载 ===")
    
    # 生成校验和
    original_checksums = generate_checksums()
    
    # 保存校验和
    save_result = save_checksums(original_checksums)
    print(f"1. 保存校验和: {'成功' if save_result else '失败'}")
    assert save_result, "保存校验和失败"
    
    # 加载校验和
    loaded_checksums = load_checksums()
    print(f"2. 加载校验和: {'成功' if loaded_checksums else '失败'}")
    assert loaded_checksums is not None, "加载校验和失败"
    assert isinstance(loaded_checksums, dict), "加载的校验和应该是字典类型"
    
    print("✅ 校验和保存加载测试通过")
    return True

def test_dependency_verification():
    """测试依赖验证功能"""
    print("\n=== 测试依赖验证 ===")
    
    # 验证依赖
    result = verify_dependencies()
    print(f"1. 依赖验证结果: {'通过' if result else '失败'}")
    
    print("✅ 依赖验证测试通过")
    return True

def test_update_checksums():
    """测试更新校验和功能"""
    print("\n=== 测试更新校验和 ===")
    
    # 更新校验和
    result = update_checksums()
    print(f"1. 更新校验和结果: {'成功' if result else '失败'}")
    assert result, "更新校验和失败"
    
    print("✅ 更新校验和测试通过")
    return True

def test_verify_checksums():
    """测试校验和验证功能"""
    print("\n=== 测试校验和验证 ===")
    
    # 验证校验和
    result = verify_checksums()
    print(f"1. 校验和验证结果: {'通过' if result else '失败'}")
    
    print("✅ 校验和验证测试通过")
    return True

def test_tamper_proof_check():
    """测试防篡改检查功能"""
    print("\n=== 测试防篡改检查 ===")
    
    # 执行防篡改检查
    result = tamper_proof_check()
    print(f"1. 防篡改检查结果: {'通过' if result else '失败'}")
    
    print("✅ 防篡改检查测试通过")
    return True

def test_full_security_check():
    """测试完整安全检查功能"""
    print("\n=== 测试完整安全检查 ===")
    
    # 执行完整安全检查
    result = full_security_check()
    print(f"1. 完整安全检查结果: {'通过' if result else '失败'}")
    
    print("✅ 完整安全检查测试通过")
    return True

def main():
    """主测试函数"""
    print("🚀 防篡改机制测试")
    
    tests = [
        test_file_hash_calculation,
        test_signature_management,
        test_checksum_generation,
        test_checksum_save_load,
        test_dependency_verification,
        test_update_checksums,
        test_verify_checksums,
        test_tamper_proof_check,
        test_full_security_check
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
