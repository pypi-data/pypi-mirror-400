#!/usr/bin/env python3
"""
项目防篡改机制
用于验证关键文件的完整性
"""

import hashlib
import os
import json
import hmac
import time
from github_shell.utils.config import load_config, save_config
from github_shell.utils.language import _

# 关键文件列表，需要验证完整性的文件
CRITICAL_FILES = [
    "github_shell/main.py",
    "github_shell/utils/config.py",
    "github_shell/utils/email_verification.py",
    "github_shell/utils/tamper_proof.py",
    "github_shell/commands/repo_commands.py",
    "github_shell/commands/user_commands.py",
    "github_shell/commands/search_commands.py",
    "github_shell/commands/org_commands.py",
    "github_shell/commands/update_commands.py"
]

# 校验和文件路径
CHECKSUM_FILE = os.path.expanduser("~/.github_shell_checksums.json")

# 签名密钥文件路径
SIGNATURE_KEY_FILE = os.path.expanduser("~/.github_shell_signature_key.json")

# 配置变更日志文件路径
CONFIG_CHANGE_LOG = os.path.expanduser("~/.github_shell_config_changes.log")

def calculate_file_hash(file_path, algorithm="sha512"):
    """计算文件的哈希值
    
    Args:
        file_path: 文件路径
        algorithm: 哈希算法，支持sha256, sha512等
        
    Returns:
        str: 文件的哈希值，或者None如果文件不存在
    """
    if not os.path.exists(file_path):
        return None
    
    # 选择哈希算法
    if algorithm == "sha512":
        hasher = hashlib.sha512()
    elif algorithm == "sha256":
        hasher = hashlib.sha256()
    else:
        hasher = hashlib.sha512()  # 默认使用sha512
    
    with open(file_path, "rb") as f:
        # 分块读取文件，避免内存占用过大
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    
    return hasher.hexdigest()

class SignatureManager:
    """签名管理类，用于生成和验证数字签名"""
    
    def __init__(self):
        """初始化签名管理器"""
        self.key = self.load_or_generate_key()
    
    def load_or_generate_key(self):
        """加载或生成签名密钥
        
        Returns:
            str: 签名密钥
        """
        if os.path.exists(SIGNATURE_KEY_FILE):
            try:
                with open(SIGNATURE_KEY_FILE, "r", encoding="utf-8") as f:
                    key_data = json.load(f)
                    return key_data.get("key")
            except (json.JSONDecodeError, IOError):
                pass
        
        # 生成新密钥
        new_key = hashlib.sha256(os.urandom(64)).hexdigest()
        try:
            with open(SIGNATURE_KEY_FILE, "w", encoding="utf-8") as f:
                json.dump({"key": new_key, "generated_at": time.time()}, f, indent=2, ensure_ascii=False)
            # 设置文件权限，仅当前用户可读写
            if os.name != "nt":  # 非Windows系统
                os.chmod(SIGNATURE_KEY_FILE, 0o600)
        except IOError:
            pass
        
        return new_key
    
    def generate_signature(self, data):
        """生成数据的HMAC签名
        
        Args:
            data: 要签名的数据
            
        Returns:
            str: HMAC签名
        """
        return hmac.new(self.key.encode(), data.encode(), hashlib.sha512).hexdigest()
    
    def verify_signature(self, data, signature):
        """验证数据的HMAC签名
        
        Args:
            data: 要验证的数据
            signature: 签名
            
        Returns:
            bool: 签名是否有效
        """
        expected_signature = self.generate_signature(data)
        return hmac.compare_digest(expected_signature, signature)

# 创建全局签名管理器实例
signature_manager = SignatureManager()

def generate_checksums():
    """生成关键文件的校验和
    
    Returns:
        dict: 文件名到哈希值的映射
    """
    checksums = {
        "_metadata": {
            "algorithm": "sha512",
            "generated_at": time.time(),
            "version": "1.2"
        },
        "files": {}
    }
    
    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    for file_path in CRITICAL_FILES:
        full_path = os.path.join(project_root, file_path)
        file_hash = calculate_file_hash(full_path, "sha512")
        if file_hash:
            checksums["files"][file_path] = file_hash
    
    # 生成签名
    checksums_data = json.dumps(checksums, sort_keys=True, ensure_ascii=False)
    checksums["signature"] = signature_manager.generate_signature(checksums_data)
    
    return checksums

def save_checksums(checksums):
    """保存校验和到文件
    
    Args:
        checksums: 校验和字典
        
    Returns:
        bool: 保存是否成功
    """
    try:
        with open(CHECKSUM_FILE, "w", encoding="utf-8") as f:
            json.dump(checksums, f, indent=2, ensure_ascii=False)
        # 设置文件权限，仅当前用户可读写
        if os.name != "nt":  # 非Windows系统
            os.chmod(CHECKSUM_FILE, 0o600)
        return True
    except IOError as e:
        print(_("tamper_saving_checksum_failed", e))
        return False

def load_checksums():
    """从文件加载校验和
    
    Returns:
        dict: 校验和字典，如果文件不存在或无效则返回空字典
    """
    if os.path.exists(CHECKSUM_FILE):
        try:
            with open(CHECKSUM_FILE, "r", encoding="utf-8") as f:
                checksums = json.load(f)
            
            # 验证签名
            signature = checksums.pop("signature", "")
            checksums_data = json.dumps(checksums, sort_keys=True, ensure_ascii=False)
            
            if signature_manager.verify_signature(checksums_data, signature):
                return checksums
            else:
                print(_("tamper_invalid_signature"))
                return {}
                
        except (json.JSONDecodeError, IOError) as e:
            print(_("tamper_loading_checksum_failed", e))
            return {}
    return {}

def verify_checksums():
    """验证关键文件的完整性
    
    Returns:
        bool: 所有文件都通过验证返回True，否则返回False
    """
    # 加载保存的校验和
    saved_checksums = load_checksums()
    
    if not saved_checksums or "files" not in saved_checksums:
        # 如果没有保存的校验和，生成并保存
        print(_("tamper_no_valid_checksum"))
        new_checksums = generate_checksums()
        if save_checksums(new_checksums):
            print(_("tamper_checksum_generated"))
            return True
        else:
            print(_("tamper_checksum_generation_failed"))
            return False
    
    # 生成当前文件的校验和
    current_files = {}
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    for file_path in CRITICAL_FILES:
        full_path = os.path.join(project_root, file_path)
        file_hash = calculate_file_hash(full_path, "sha512")
        if file_hash:
            current_files[file_path] = file_hash
    
    # 验证每个文件
    all_valid = True
    algorithm = saved_checksums["_metadata"].get("algorithm", "sha512")
    
    print(_("tamper_verifying_files", algorithm))
    
    # 检查是否有新增文件
    for file_path in current_files:
        if file_path not in saved_checksums["files"]:
            print(_("tamper_new_file_detected", file_path))
            # 新增文件不导致验证失败，但需要提醒
    
    # 检查是否有文件缺失或篡改
    for file_path, expected_hash in saved_checksums["files"].items():
        if file_path in current_files:
            actual_hash = current_files[file_path]
            if actual_hash == expected_hash:
                print(_("tamper_file_verified", file_path))
            else:
                print(_("tamper_file_tampered", file_path))
                print(_("tamper_expected_hash", expected_hash))
                print(_("tamper_actual_hash", actual_hash))
                all_valid = False
        else:
            print(_("tamper_file_missing", file_path))
            all_valid = False
    
    return all_valid

def update_checksums():
    """更新校验和文件
    
    Returns:
        bool: 更新是否成功
    """
    checksums = generate_checksums()
    return save_checksums(checksums)

def tamper_proof_check():
    """防篡改检查的主函数
    
    Returns:
        bool: 检查是否通过
    """
    print(_("tamper_verifying_integrity"))
    return verify_checksums()

def log_config_change(key, old_value, new_value, user_mode):
    """记录配置变更
    
    Args:
        key: 配置项名称
        old_value: 旧值
        new_value: 新值
        user_mode: 用户模式
    """
    try:
        with open(CONFIG_CHANGE_LOG, "a", encoding="utf-8") as f:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] MODE: {user_mode} - CONFIG: {key} - OLD: {old_value} -> NEW: {new_value}\n")
    except IOError:
        pass

def verify_dependencies():
    """验证依赖完整性
    
    Returns:
        bool: 依赖验证是否通过
    """
    print("\n" + _("tamper_verifying_dependencies"))
    
    # 检查关键依赖是否存在
    required_dependencies = [
        "requests",
        "hashlib",
        "json",
        "os",
        "hmac",
        "time"
    ]
    
    all_present = True
    for dep in required_dependencies:
        try:
            __import__(dep)
            print(_("tamper_dependency_verified", dep))
        except ImportError:
            print(_("tamper_dependency_missing", dep))
            all_present = False
    
    return all_present

def full_security_check():
    """完整的安全性检查
    
    Returns:
        bool: 所有检查是否通过
    """
    print(_("tamper_full_security_check"))
    
    # 执行所有安全检查
    checks = [
        (_("tamper_file_integrity_check"), tamper_proof_check),
        (_("tamper_dependency_integrity_check"), verify_dependencies)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        print(f"\n{check_name}:")
        if not check_func():
            all_passed = False
    
    if all_passed:
        print("\n" + _("tamper_all_checks_passed"))
    else:
        print("\n" + _("tamper_security_check_failed"))
    
    return all_passed