#!/usr/bin/env python3
"""
加密工具模块
用于加密和解密敏感配置项
"""

import os
import json
from cryptography.fernet import Fernet

# 加密密钥文件路径
ENCRYPTION_KEY_FILE = os.path.expanduser("~/.github_shell_encryption_key.json")

# 需要加密的敏感配置项列表
SENSITIVE_CONFIG_ITEMS = [
    "github_token",
    "sender_password"
]

class ConfigEncryption:
    """配置加密类"""
    
    def __init__(self):
        """初始化加密类"""
        self.key = self.load_or_generate_key()
        self.cipher = Fernet(self.key)
    
    def load_or_generate_key(self):
        """加载或生成加密密钥
        
        Returns:
            bytes: 加密密钥
        """
        if os.path.exists(ENCRYPTION_KEY_FILE):
            try:
                with open(ENCRYPTION_KEY_FILE, "r", encoding="utf-8") as f:
                    key_data = json.load(f)
                    return key_data.get("key").encode()
            except (json.JSONDecodeError, IOError):
                pass
        
        # 生成新密钥
        new_key = Fernet.generate_key()
        try:
            with open(ENCRYPTION_KEY_FILE, "w", encoding="utf-8") as f:
                json.dump({"key": new_key.decode(), "generated_at": time.time()}, f, indent=2, ensure_ascii=False)
            # 设置文件权限，仅当前用户可读写
            if os.name != "nt":  # 非Windows系统
                os.chmod(ENCRYPTION_KEY_FILE, 0o600)
        except IOError:
            pass
        
        return new_key
    
    def encrypt(self, data):
        """加密数据
        
        Args:
            data: 要加密的数据
            
        Returns:
            str: 加密后的数据
        """
        if not data:
            return ""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data):
        """解密数据
        
        Args:
            encrypted_data: 要解密的数据
            
        Returns:
            str: 解密后的数据
        """
        if not encrypted_data:
            return ""
        try:
            return self.cipher.decrypt(encrypted_data.encode()).decode()
        except Exception:
            # 解密失败，返回原始数据
            return encrypted_data
    
    def is_encrypted(self, data):
        """检查数据是否已加密
        
        Args:
            data: 要检查的数据
            
        Returns:
            bool: 是否已加密
        """
        if not data:
            return False
        # 简单检查是否是base64编码的字符串（Fernet加密的特征）
        return len(data) % 4 == 0 and "=" not in data[1:-1] and ("+" in data or "/" in data)

# 创建全局加密实例
import time
config_encryption = ConfigEncryption()

def encrypt_sensitive_config(config):
    """加密配置中的敏感项
    
    Args:
        config: 配置字典
        
    Returns:
        dict: 加密后的配置字典
    """
    encrypted_config = config.copy()
    
    for key in SENSITIVE_CONFIG_ITEMS:
        if key in encrypted_config and config_encryption.is_encrypted(encrypted_config[key]):
            # 已经加密，跳过
            continue
        if key in encrypted_config and encrypted_config[key]:
            encrypted_config[key] = config_encryption.encrypt(encrypted_config[key])
    
    return encrypted_config

def decrypt_sensitive_config(config):
    """解密配置中的敏感项
    
    Args:
        config: 配置字典
        
    Returns:
        dict: 解密后的配置字典
    """
    decrypted_config = config.copy()
    
    for key in SENSITIVE_CONFIG_ITEMS:
        if key in decrypted_config and decrypted_config[key]:
            decrypted_config[key] = config_encryption.decrypt(decrypted_config[key])
    
    return decrypted_config
