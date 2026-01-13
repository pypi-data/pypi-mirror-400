#!/usr/bin/env python3
"""
依赖管理测试脚本
"""

from github_shell.utils.dependency_manager import (
    check_and_install_dependencies,
    check_module,
    install_module
)

def test_check_module():
    """测试检查模块功能"""
    print("=== 测试检查模块功能 ===")
    
    # 测试存在的模块
    assert check_module("os") == True
    print("✅ 检查存在的模块：os - 成功")
    
    # 测试不存在的模块
    assert check_module("non_existent_module_12345") == False
    print("✅ 检查不存在的模块：non_existent_module_12345 - 成功")
    
    # 测试requests模块
    requests_exists = check_module("requests")
    print(f"✅ 检查requests模块 - {'已安装' if requests_exists else '未安装'}")

def test_dependency_check():
    """测试依赖检查功能"""
    print("\n=== 测试依赖检查功能 ===")
    
    # 调用依赖检查函数
    result = check_and_install_dependencies()
    print(f"✅ 依赖检查结果：{'成功' if result else '失败'}")
    
    # 验证requests模块已安装
    assert check_module("requests") == True
    print("✅ requests模块已安装")

def test_install_module():
    """测试安装模块功能"""
    print("\n=== 测试安装模块功能 ===")
    
    # 测试安装一个临时模块（会被立即卸载）
    test_module = "pytest"
    
    # 检查模块是否已安装
    if check_module(test_module):
        print(f"✅ {test_module} 已安装，跳过安装测试")
    else:
        # 尝试安装模块
        print(f"📦 尝试安装 {test_module}...")
        result = install_module(test_module)
        print(f"✅ 安装结果：{'成功' if result else '失败'}")
        
        if result:
            assert check_module(test_module) == True
            print(f"✅ {test_module} 安装成功并可导入")

# 修复后的主函数
if __name__ == "__main__":
    print("🚀 测试依赖管理功能")
    
    try:
        test_check_module()
        test_dependency_check()
        test_install_module()
        print("\n🎉 所有测试通过！")
    except AssertionError as e:
        print(f"\n❌ 测试失败：{e}")
    except Exception as e:
        print(f"\n❌ 测试异常：{e}")
