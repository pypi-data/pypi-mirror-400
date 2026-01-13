import os
import json
import time

# 配置文件路径
CONFIG_FILE = os.path.expanduser("~/.github_shell_config.json")

# 导入加密模块
from github_shell.utils.encryption import encrypt_sensitive_config, decrypt_sensitive_config

# GitHub API基础URL
GITHUB_API = "https://api.github.com"

# 自动更新配置
UPDATE_CONFIG = {
    "repo_owner": "wjr-2015",
    "repo_name": "github-shell",
    "remote_url": "https://raw.githubusercontent.com/wjr-2015/github-shell/main/github_shell/utils/config.py",
    "version": "1.2.0"  # 当前版本
}

# 配置管理功能
def load_config():
    """加载配置"""
    # 默认配置 - 移除了默认的隐私设置
    default_config = {
        "language": "english",
        "history_size": 100,
        "theme": "default",
        "github_username": "",
        "github_email": "",
        "github_token": "",
        "mode": "user",  # 默认用户模式，可选值：user, developer
        "developer_locked": False,  # 开发者模式是否锁定
        # 邮箱验证码配置
        "verification_code": "",  # 存储的验证码
        "verification_expiry": 0,  # 验证码过期时间戳
        "smtp_server": "smtp.126.com",
        "smtp_port": 465,
        "sender_email": "wangjinrui_150328@126.com",
        "sender_password": "",  # 需要在配置文件中设置
        "recipient_email": "wangjinrui_150328@126.com",
        # 登录安全配置
        "login_failures": 0,  # 连续登录失败次数
        "login_lockout_until": 0,  # 登录锁定截止时间
        "max_login_failures": 5,  # 最大连续失败次数
        "lockout_duration": 300,  # 锁定持续时间（秒）
        # 配置变更审计
        "config_version": "1.2",
        "last_config_change": time.time()
    }
    
    # 如果配置文件存在，加载配置
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                loaded_config = json.load(f)
                # 合并默认配置和加载的配置
                default_config.update(loaded_config)
        except (json.JSONDecodeError, IOError):
            pass
    
    # 解密敏感配置项
    return decrypt_sensitive_config(default_config)

def save_config(config):
    """保存配置"""
    try:
        # 加密敏感配置项
        encrypted_config = encrypt_sensitive_config(config)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(encrypted_config, f, indent=2, ensure_ascii=False)
        return True
    except IOError:
        return False

def get_config(key, default=None):
    """获取配置项"""
    config = load_config()
    return config.get(key, default)

def set_config(key, value):
    """设置配置项"""
    # 检查是否在用户模式下尝试修改核心配置
    current_mode = get_mode()
    # 核心配置项，只有开发者模式可以修改
    core_configs = [
        "developer_locked",
        "login_failures",
        "login_lockout_until",
        "max_login_failures",
        "lockout_duration",
        "verification_code",
        "verification_expiry"
    ]
    
    if current_mode == "user" and key in core_configs:
        return False
    
    # 加载当前配置
    config = load_config()
    
    # 获取旧值用于日志记录
    old_value = config.get(key, "")
    
    # 更新配置项
    config[key] = value
    
    # 更新配置变更时间
    config["last_config_change"] = time.time()
    
    # 保存配置
    if save_config(config):
        # 记录配置变更（排除敏感信息）
        if key not in ["sender_password", "github_token"]:
            from github_shell.utils.tamper_proof import log_config_change
            log_config_change(key, old_value, value, current_mode)
        return True
    
    return False

def reset_config():
    """重置配置"""
    # 重置配置只能在开发者模式下进行
    current_mode = get_mode()
    if current_mode != "developer":
        return False
    
    default_config = {
        "language": "english",
        "history_size": 100,
        "theme": "default",
        "github_username": "",
        "github_email": "",
        "github_token": "",
        "mode": "user",
        "developer_locked": False,
        # 邮箱验证码配置
        "verification_code": "",
        "verification_expiry": 0,
        "smtp_server": "smtp.126.com",
        "smtp_port": 465,
        "sender_email": "wangjinrui_150328@126.com",
        "sender_password": "",
        "recipient_email": "wangjinrui_150328@126.com",
        # 登录安全配置
        "login_failures": 0,
        "login_lockout_until": 0,
        "max_login_failures": 5,
        "lockout_duration": 300,
        # 配置变更审计
        "config_version": "1.2",
        "last_config_change": time.time()
    }
    save_config(default_config)
    return default_config



# 获取开发者模式锁定状态
def get_developer_locked():
    """获取开发者模式锁定状态
    
    Returns:
        bool: 是否锁定
    """
    return get_config("developer_locked", False)

# 设置开发者模式锁定状态
def set_developer_locked(locked):
    """设置开发者模式锁定状态
    
    Args:
        locked: 是否锁定
        
    Returns:
        bool: 操作是否成功
    """
    return set_config("developer_locked", locked)

# 获取当前模式
def get_mode():
    """获取当前模式"""
    return get_config("mode", "user")

# 设置模式
def set_mode(mode):
    """设置当前模式
    
    Args:
        mode: 模式名称，可选值：user (用户模式), developer (开发者模式)
        
    Returns:
        bool: 操作是否成功
    """
    if mode in ["user", "developer"]:
        return set_config("mode", mode)
    return False

# 获取GitHub用户名
def get_github_username():
    """获取GitHub用户名"""
    return get_config("github_username", "")

# 设置GitHub用户名
def set_github_username(username):
    """设置GitHub用户名"""
    return set_config("github_username", username)

# 获取GitHub邮箱
def get_github_email():
    """获取GitHub邮箱"""
    return get_config("github_email", "")

# 设置GitHub邮箱
def set_github_email(email):
    """设置GitHub邮箱"""
    return set_config("github_email", email)

# 获取GitHub令牌
def get_github_token():
    """获取GitHub令牌"""
    return get_config("github_token", "")

# 设置GitHub令牌
def set_github_token(token):
    """设置GitHub令牌"""
    return set_config("github_token", token)

# 清除GitHub令牌
def clear_github_token():
    """清除GitHub令牌"""
    return set_config("github_token", "")

# 命令帮助信息
HELP_TEXT = """
GitHub 仿真 Shell 命令列表：

仓库操作：
  repos                 - 列出当前用户的仓库
  repo <owner>/<repo>   - 查看指定仓库信息
  issues <repo>         - 查看仓库的Issues
  branches <repo>       - 查看仓库的分支
  commits <repo>        - 查看仓库的最近提交
  contributors <repo>   - 查看仓库的贡献者
  prs <repo>            - 查看仓库的Pull Requests
  gists <username>      - 查看用户的Gists

搜索功能：
  search <query>        - 搜索GitHub仓库

组织操作：
  org <orgname>         - 查看指定组织信息

用户操作：
  user <username>       - 查看指定用户信息
  followers             - 查看当前用户的关注者
  following             - 查看当前用户关注的人

系统命令：
  help                  - 显示此帮助信息
  clear                 - 清除屏幕
  exit                  - 退出仿真Shell
  stop/shutdown         - 停止GitHub Shell（仅开发者模式）
  update                - 检查并更新到最新版本
  version               - 显示当前版本
"""
