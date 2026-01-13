#!/usr/bin/env python3
"""
历史命令管理模块
用于记录和管理用户输入的命令历史
"""

import os
import json
from pathlib import Path
from github_shell.utils.config import get_config

# 历史文件路径
HISTORY_FILE = Path.home() / ".github_shell" / "history.json"

def load_history():
    """加载命令历史
    
    Returns:
        list: 命令历史列表
    """
    # 确保目录存在
    HISTORY_FILE.parent.mkdir(exist_ok=True)
    
    # 如果历史文件不存在，返回空列表
    if not HISTORY_FILE.exists():
        return []
    
    # 加载历史文件
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
        return history
    except (json.JSONDecodeError, IOError):
        return []

def save_history(history):
    """保存命令历史到文件
    
    Args:
        history: 命令历史列表
    """
    # 确保目录存在
    HISTORY_FILE.parent.mkdir(exist_ok=True)
    
    # 获取历史大小限制
    history_size = get_config("history_size", 100)
    
    # 只保存最近的history_size条记录
    if len(history) > history_size:
        history = history[-history_size:]
    
    # 保存历史文件
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def add_to_history(command):
    """添加命令到历史记录
    
    Args:
        command: 要添加的命令
    """
    # 忽略空命令和重复的最后一条命令
    if not command.strip():
        return
    
    history = load_history()
    
    # 如果历史不为空且最后一条命令与当前命令相同，则不添加
    if history and history[-1] == command:
        return
    
    # 添加命令到历史
    history.append(command)
    
    # 保存历史
    save_history(history)

def clear_history():
    """清空命令历史"""
    # 删除历史文件
    if HISTORY_FILE.exists():
        HISTORY_FILE.unlink()
    print("✅ 命令历史已清空")

def show_history():
    """显示命令历史
    
    Returns:
        list: 命令历史列表
    """
    history = load_history()
    for i, cmd in enumerate(history, 1):
        print(f"  {i}. {cmd}")
    return history
