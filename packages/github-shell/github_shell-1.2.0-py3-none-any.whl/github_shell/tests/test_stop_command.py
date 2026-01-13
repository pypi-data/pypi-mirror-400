#!/usr/bin/env python3
"""
测试GitHub Shell停止命令功能
"""
import subprocess
import sys
import time

def test_stop_command():
    """测试停止命令功能"""
    print("测试GitHub Shell停止命令功能...")
    
    # 启动GitHub Shell进程
    process = subprocess.Popen(
        [sys.executable, "-m", "github_shell"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    try:
        # 等待启动
        time.sleep(1)
        
        # 切换到开发者模式（会自动发送验证码）
        process.stdin.write("mode developer\n")
        process.stdin.flush()
        time.sleep(1)
        
        # 输入测试验证码（这里使用模拟方式，实际测试时需要从邮箱获取）
        # 注意：在实际测试环境中，需要修改为真实的验证码获取方式
        process.stdin.write("123456\n")
        process.stdin.flush()
        time.sleep(1)
        
        # 执行停止命令
        process.stdin.write("stop\n")
        process.stdin.flush()
        
        # 等待进程结束
        stdout, stderr = process.communicate(timeout=5)
        
        # 检查输出
        if "Stopping GitHub Simulation Shell" in stdout or "停止 GitHub 仿真 Shell" in stdout:
            print("✅ 停止命令测试通过！")
            return True
        else:
            print("❌ 停止命令测试失败！")
            print(f"输出: {stdout}")
            print(f"错误: {stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 测试超时，进程可能没有正确停止！")
        process.kill()
        stdout, stderr = process.communicate()
        print(f"输出: {stdout}")
        print(f"错误: {stderr}")
        return False
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        process.kill()
        return False

if __name__ == "__main__":
    success = test_stop_command()
    sys.exit(0 if success else 1)