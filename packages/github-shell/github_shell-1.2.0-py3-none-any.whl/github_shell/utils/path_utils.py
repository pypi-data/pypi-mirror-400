#!/usr/bin/env python3
"""
路径管理模块
用于处理系统PATH相关操作
"""

import os
import sys
import platform
import subprocess


def get_python_scripts_path():
    """获取Python脚本目录路径
    
    Returns:
        str: Python脚本目录的绝对路径
    """
    if platform.system() == "Windows":
        # Windows系统
        return os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Python", f"Python{sys.version_info.major}{sys.version_info.minor}", "Scripts")
    else:
        # 非Windows系统
        if sys.prefix == sys.base_prefix:
            # 系统Python
            return os.path.join(sys.prefix, "bin")
        else:
            # 虚拟环境
            return os.path.join(sys.prefix, "bin")


def is_script_in_path(script_name="github-shell"):
    """检查脚本是否在系统PATH中
    
    Args:
        script_name: 要检查的脚本名称
        
    Returns:
        bool: 如果脚本在PATH中则返回True，否则返回False
    """
    if platform.system() == "Windows":
        script_name += ".exe"
    
    for path in os.environ["PATH"].split(os.pathsep):
        script_path = os.path.join(path, script_name)
        if os.path.exists(script_path):
            return True
    return False


def is_scripts_dir_in_path():
    """检查Python Scripts目录是否在系统PATH中
    
    Returns:
        bool: 如果Scripts目录在PATH中则返回True，否则返回False
    """
    scripts_path = get_python_scripts_path()
    paths = os.environ["PATH"].split(os.pathsep)
    return scripts_path in paths


def add_scripts_dir_to_path():
    """将Python Scripts目录添加到系统PATH
    
    Returns:
        bool: 操作是否成功
    """
    if is_scripts_dir_in_path():
        return True
    
    scripts_path = get_python_scripts_path()
    
    if platform.system() == "Windows":
        # Windows系统
        try:
            # 使用setx命令添加到用户PATH
            subprocess.run(
                ["setx", "PATH", f"%PATH%;{scripts_path}"],
                check=True,
                shell=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
    else:
        # 非Windows系统
        shell_rc = None
        if os.path.exists(os.path.expanduser("~/.bashrc")):
            shell_rc = os.path.expanduser("~/.bashrc")
        elif os.path.exists(os.path.expanduser("~/.zshrc")):
            shell_rc = os.path.expanduser("~/.zshrc")
        
        if shell_rc:
            try:
                with open(shell_rc, "a") as f:
                    f.write(f"\nexport PATH=${{PATH}}:{scripts_path}")
                return True
            except IOError:
                return False
    
    return False


def get_path_help():
    """获取PATH相关帮助信息
    
    Returns:
        str: 帮助信息
    """
    scripts_path = get_python_scripts_path()
    
    help_text = f"""
PATH配置帮助：

当前Python Scripts目录：
{scripts_path}

添加到PATH的方法：

1. 临时添加（仅当前会话）：
   - Windows: set PATH=%PATH%;{scripts_path}
   - Linux/Mac: export PATH=$PATH:{scripts_path}

2. 永久添加：
   - Windows: 
     右键"此电脑" → 属性 → 高级系统设置 → 环境变量 → 用户变量 → PATH → 编辑 → 新建 → 粘贴上述路径
   - Linux: 
     echo 'export PATH=$PATH:{scripts_path}' >> ~/.bashrc
     source ~/.bashrc
   - Mac: 
     echo 'export PATH=$PATH:{scripts_path}' >> ~/.zshrc
     source ~/.zshrc

3. 使用命令自动添加：
   github-shell --add-path
"""
    
    return help_text
