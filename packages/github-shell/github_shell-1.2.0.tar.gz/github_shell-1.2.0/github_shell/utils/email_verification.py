#!/usr/bin/env python3
"""
邮箱发送模块
用于生成和发送验证码
"""

import smtplib
import random
import string
import time
from email.mime.text import MIMEText
from email.header import Header
from github_shell.utils.language import _

class EmailVerification:
    """邮箱验证码类"""
    
    def __init__(self):
        """初始化邮箱验证码类"""
        # 默认配置，后续可以从配置文件读取
        self.config = {
            "smtp_server": "smtp.126.com",
            "smtp_port": 465,
            "sender_email": "wangjinrui_150328@126.com",
            "sender_password": "",  # 需要在配置文件中设置
            "email_to": "wangjinrui_150328@126.com",
            "verification_expiry": 300,  # 验证码有效期（秒）
            "verification_length": 6  # 验证码长度
        }
    
    def generate_verification_code(self, length=6):
        """生成随机验证码
        
        Args:
            length: 验证码长度，默认为6位
            
        Returns:
            str: 随机生成的验证码
        """
        # 生成包含数字和大写字母的验证码
        characters = string.digits + string.ascii_uppercase
        return ''.join(random.choice(characters) for _ in range(length))
    
    def send_verification_email(self, code):
        """发送验证码邮件
        
        Args:
            code: 验证码
            
        Returns:
            bool: 发送是否成功
        """
        try:
            # 创建邮件内容
            subject = "GitHub Shell 开发者模式验证码"
            body = f"""
            您好！
            
            您正在尝试访问 GitHub Shell 开发者模式，验证码如下：
            
            🔐 {code}
            
            验证码有效期为5分钟，请在有效期内使用。
            
            如果您没有尝试访问开发者模式，请忽略此邮件。
            
            GitHub Shell 团队
            """
            
            # 创建MIMEText对象
            msg = MIMEText(body, 'plain', 'utf-8')
            msg['From'] = Header(self.config["sender_email"])
            msg['To'] = Header(self.config["email_to"])
            msg['Subject'] = Header(subject, 'utf-8')
            
            # 发送邮件
            with smtplib.SMTP_SSL(self.config["smtp_server"], self.config["smtp_port"]) as server:
                server.login(self.config["sender_email"], self.config["sender_password"])
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(_("email_send_failed", e))
            return False
    
    def validate_code(self, input_code, stored_code, expiry_time):
        """验证验证码
        
        Args:
            input_code: 用户输入的验证码
            stored_code: 存储的验证码
            expiry_time: 验证码过期时间戳
            
        Returns:
            bool: 验证是否成功
        """
        # 检查验证码是否过期
        if time.time() > expiry_time:
            return False
        
        # 检查验证码是否匹配
        return input_code == stored_code

# 全局实例
email_verifier = EmailVerification()

# 工具函数
def generate_and_send_verification():
    """生成并发送验证码
    
    Returns:
        tuple: (验证码, 过期时间) 或 (None, None) 如果发送失败
    """
    code = email_verifier.generate_verification_code()
    if email_verifier.send_verification_email(code):
        expiry_time = time.time() + email_verifier.config["verification_expiry"]
        return code, expiry_time
    return None, None

def verify_code(input_code, stored_code, expiry_time):
    """验证验证码
    
    Args:
        input_code: 用户输入的验证码
        stored_code: 存储的验证码
        expiry_time: 验证码过期时间
        
    Returns:
        bool: 验证是否成功
    """
    return email_verifier.validate_code(input_code, stored_code, expiry_time)