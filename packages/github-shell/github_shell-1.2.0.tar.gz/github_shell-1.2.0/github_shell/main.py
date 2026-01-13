import os
import sys
import time
from github_shell.commands.repo_commands import RepoCommands
from github_shell.commands.user_commands import UserCommands
from github_shell.commands.search_commands import SearchCommands
from github_shell.commands.org_commands import OrgCommands
from github_shell.commands.update_commands import UpdateCommands
from github_shell.commands.rate_limit import RateLimitCommand
from github_shell.utils.config import UPDATE_CONFIG
from github_shell.utils.config import (
    load_config, save_config, set_config, reset_config,
    get_github_username, set_github_username,
    get_github_email, set_github_email,
    get_github_token, set_github_token, clear_github_token,
    get_mode, set_mode,
    get_developer_locked, set_developer_locked
)
import getpass
from github_shell.utils.language import _, get_language, set_language
from github_shell.utils.dependency_manager import check_and_install_dependencies
from github_shell.utils.history import add_to_history, show_history, clear_history

class GitHubShell:
    """GitHub仿真Shell主类"""
    
    def __init__(self):
        self.repo_commands = RepoCommands()
        self.user_commands = UserCommands()
        self.search_commands = SearchCommands()
        self.org_commands = OrgCommands()
        self.update_commands = UpdateCommands()
        self.rate_limit_cmd = RateLimitCommand()
        # 加载配置
        self.config = load_config()
        # 设置初始语言
        lang = self.config.get("language", "english")
        # 转换简写为完整语言名
        lang_map = {"en": "english", "zh": "chinese"}
        if lang in lang_map:
            lang = lang_map[lang]
        set_language(lang)
    
    def clear_screen(self):
        """清除屏幕"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def run(self):
        """运行仿真Shell"""
        # 程序启动时执行完整安全检查
        from github_shell.utils.tamper_proof import full_security_check
        if not full_security_check():
            print(_("security_check_failed_exit"))
            return
        
        # 根据当前模式显示欢迎信息
        current_mode = get_mode()
        if current_mode == "developer":
            print(_("welcome_developer_mode"))
        else:
            print(_("welcome_user_mode"))
        
        print(_("current_version", UPDATE_CONFIG['version']))
        username = get_github_username() or "unknown"
        print(_("welcome_user", username))
        print(_("help_tip"))
        
        while True:
            try:
                # 获取当前用户名
                USERNAME = get_github_username() or "unknown"
                # 获取用户输入
                command = input(_("prompt", USERNAME)).strip()
                
                # 添加命令到历史记录
                add_to_history(command)
                
                # 解析命令
                parts = command.split()
                if not parts:
                    continue
                
                cmd = parts[0].lower()
                args = parts[1:]
                
                # 处理命令返回格式选项
                return_format = "print"
                actual_args = args
                if args and args[-1] in ["--json", "--return"]:
                    return_format = "json"
                    actual_args = args[:-1]
                
                # 处理命令
                if cmd == "exit":
                    print(_("exit_msg"))
                    break
                elif cmd == "help":
                    print(_("help_text"))
                elif cmd == "test" and actual_args:
                    # 测试命令只能在开发者模式下使用
                    if get_mode() != "developer":
                        print(_("developer_commands_restricted"))
                        continue
                    
                    # 新功能：命令测试
                    test_command = " ".join(actual_args)
                    print(_("testing_command", test_command))
                    print(_("separator_line"))
                    
                    # 保存当前返回格式
                    original_return_format = return_format
                    
                    # 执行测试命令
                    if test_command == "test-lang":
                        # 测试语言切换
                        print(_("testing_language_switching"))
                        print(_("testing_current_language", get_language()))
                        set_language("chinese")
                        print(_("testing_switched_to", get_language()))
                        print(_("welcome"))
                        set_language("english")
                        print(_("testing_switched_back", get_language()))
                        print(_("welcome"))
                    else:
                        # 解析并执行测试命令
                        test_parts = test_command.split()
                        if not test_parts:
                            print(_("testing_invalid_command"))
                            continue
                        
                        test_cmd = test_parts[0].lower()
                        test_args = test_parts[1:]
                        
                        # 模拟执行测试命令
                        if test_cmd == "repos":
                            result = self.repo_commands.list_repos(output_format=original_return_format)
                            if original_return_format == "json":
                                import json
                                print(json.dumps(result, indent=2))
                        elif test_cmd == "repo" and test_args:
                            result = self.repo_commands.show_repo(test_args[0], output_format=original_return_format)
                            if original_return_format == "json":
                                import json
                                print(json.dumps(result, indent=2))
                        elif test_cmd == "user" and test_args:
                            result = self.user_commands.show_user(test_args[0], output_format=original_return_format)
                            if original_return_format == "json":
                                import json
                                print(json.dumps(result, indent=2))
                        else:
                            print(_("testing_unsupported_command", test_cmd))
                    
                    print(_("separator_line"))
                    print(_("testing_completed"))
                elif cmd == "clear":
                    self.clear_screen()
                elif cmd == "repos":
                    result = self.repo_commands.list_repos(output_format=return_format)
                    if return_format == "json":
                        import json
                        print(json.dumps(result, indent=2))
                elif cmd == "repo" and actual_args:
                    result = self.repo_commands.show_repo(actual_args[0], output_format=return_format)
                    if return_format == "json":
                        import json
                        print(json.dumps(result, indent=2))
                elif cmd == "issues" and actual_args:
                    repo = actual_args[0]
                    if "/" not in repo:
                        repo = f"{USERNAME}/{repo}"
                    result = self.repo_commands.show_issues(repo, output_format=return_format)
                    if return_format == "json":
                        import json
                        print(json.dumps(result, indent=2))
                elif cmd == "branches" and actual_args:
                    repo = actual_args[0]
                    if "/" not in repo:
                        repo = f"{USERNAME}/{repo}"
                    result = self.repo_commands.show_branches(repo, output_format=return_format)
                    if return_format == "json":
                        import json
                        print(json.dumps(result, indent=2))
                elif cmd == "commits" and actual_args:
                    repo = actual_args[0]
                    if "/" not in repo:
                        repo = f"{USERNAME}/{repo}"
                    result = self.repo_commands.show_commits(repo, output_format=return_format)
                    if return_format == "json":
                        import json
                        print(json.dumps(result, indent=2))
                elif cmd == "user" and actual_args:
                    result = self.user_commands.show_user(actual_args[0], output_format=return_format)
                    if return_format == "json":
                        import json
                        print(json.dumps(result, indent=2))
                elif cmd == "followers":
                    result = self.user_commands.list_followers(output_format=return_format)
                    if return_format == "json":
                        import json
                        print(json.dumps(result, indent=2))
                elif cmd == "following":
                    result = self.user_commands.list_following(output_format=return_format)
                    if return_format == "json":
                        import json
                        print(json.dumps(result, indent=2))
                elif cmd == "contributors" and actual_args:
                    repo = actual_args[0]
                    if "/" not in repo:
                        repo = f"{USERNAME}/{repo}"
                    result = self.repo_commands.show_contributors(repo, output_format=return_format)
                    if return_format == "json":
                        import json
                        print(json.dumps(result, indent=2))
                elif cmd == "prs" and actual_args:
                    repo = actual_args[0]
                    if "/" not in repo:
                        repo = f"{USERNAME}/{repo}"
                    result = self.repo_commands.show_prs(repo, output_format=return_format)
                    if return_format == "json":
                        import json
                        print(json.dumps(result, indent=2))
                elif cmd == "gists" and actual_args:
                    result = self.repo_commands.show_gists(actual_args[0], output_format=return_format)
                    if return_format == "json":
                        import json
                        print(json.dumps(result, indent=2))
                elif cmd == "search" and actual_args:
                    result = self.search_commands.search_repos(" ".join(actual_args), output_format=return_format)
                    if return_format == "json":
                        import json
                        print(json.dumps(result, indent=2))
                elif cmd == "org" and actual_args:
                    result = self.org_commands.show_org(actual_args[0], output_format=return_format)
                    if return_format == "json":
                        import json
                        print(json.dumps(result, indent=2))
                elif cmd == "update":
                    self.update_commands.check_for_updates()
                elif cmd == "version":
                    self.update_commands.show_version()
                elif cmd == "language" and args:
                    # 语言切换命令
                    lang = args[0]
                    # 转换简写为完整语言名
                    lang_map = {"en": "english", "zh": "chinese"}
                    if lang in lang_map:
                        lang = lang_map[lang]
                    if set_language(lang):
                        print(_("language_changed", lang))
                        # 保存语言设置到配置文件
                        set_config("language", lang)
                    else:
                        print(_("invalid_language", lang))
                # 新功能：速率限制
                elif cmd == "rate" or cmd == "limit" or cmd == "rate-limit":
                    self.rate_limit_cmd.show_rate_limit()
                # 新功能：历史命令
                elif cmd == "history":
                    show_history()
                # 新功能：清空历史
                elif cmd == "clear-history":
                    clear_history()
                # 新功能：配置相关
                elif cmd == "config" and len(args) >= 2:
                    # 设置配置项
                    key = args[0]
                    value = args[1]
                    # 核心配置项，只有开发者模式可以修改
                    core_configs = [
                        "developer_password",
                        "developer_locked"
                    ]
                    if key in core_configs and get_mode() != "developer":
                        print(_("developer_commands_restricted"))
                        continue
                    if set_config(key, value):
                        print(_("config_set_success", key, value))
                    else:
                        print(_("config_set_failed", key))
                elif cmd == "config" and len(args) == 1:
                    # 查看配置项
                    key = args[0]
                    config = load_config()
                    if key in config:
                        print(_("config_value", key, config[key]))
                    else:
                        print(_("config_not_found", key))
                elif cmd == "config" and len(args) == 0:
                    # 查看所有配置
                    config = load_config()
                    print(_("config_current"))
                    for key, value in config.items():
                        print(_("config_value", key, value))
                elif cmd == "reset-config":
                    # 重置配置只能在开发者模式下使用
                    if get_mode() != "developer":
                        print(_("developer_commands_restricted"))
                        continue
                    reset_config()
                    print(_("config_reset_success"))
                # 新功能：账号管理命令
                elif cmd == "github-username" and actual_args:
                    # 设置GitHub用户名
                    username = actual_args[0]
                    if set_github_username(username):
                        print(_("github_username_set", username))
                    else:
                        print(_("github_username_failed"))
                elif cmd == "github-username" and len(actual_args) == 0:
                    # 查看GitHub用户名
                    username = get_github_username()
                    if username:
                        print(_("github_username_show", username))
                    else:
                        print(_("github_username_not_set"))
                elif cmd == "github-email" and actual_args:
                    # 设置GitHub邮箱
                    email = actual_args[0]
                    if set_github_email(email):
                        print(_("github_email_set", email))
                    else:
                        print(_("github_email_failed"))
                elif cmd == "github-email" and len(actual_args) == 0:
                    # 查看GitHub邮箱
                    email = get_github_email()
                    if email:
                        print(_("github_email_show", email))
                    else:
                        print(_("github_email_not_set"))
                elif cmd == "github-token" and actual_args:
                    # 设置GitHub令牌
                    token = actual_args[0]
                    token_display = f"{token[:5]}...{token[-5:]}"
                    if set_github_token(token):
                        print(_("github_token_set", token_display))
                        print(_("token_saved_warning"))
                    else:
                        print(_("github_token_failed"))
                elif cmd == "github-token" and len(actual_args) == 0:
                    # 查看GitHub令牌状态
                    token = get_github_token()
                    if token:
                        token_display = f"{token[:5]}...{token[-5:]}"
                        print(_("github_token_show", token_display))
                    else:
                        print(_("github_token_not_set"))
                elif cmd == "github-token-clear":
                    # 清除GitHub令牌
                    if clear_github_token():
                        print(_("github_token_cleared"))
                    else:
                        print(_("github_token_clear_failed"))
                elif cmd == "github-info" and len(actual_args) == 0:
                    # 查看所有GitHub账号信息
                    print(_("github_info_title"))
                    username = get_github_username()
                    email = get_github_email()
                    token = get_github_token()
                    print(_("github_info_username", username or _("github_info_token_not_set")))
                    print(_("github_info_email", email or _("github_info_token_not_set")))
                    token_status = _("github_info_token_set") if token else _("github_info_token_not_set")
                    if token:
                        token_display = f"{token[:5]}...{token[-5:]}"
                        token_status = f"{token_status} ({token_display})"
                    print(_("github_info_token", token_status))
                # 新功能：模式切换命令
                elif cmd == "mode" and actual_args:
                    # 设置模式
                    mode = actual_args[0].lower()
                    
                    # 切换到开发者模式需要验证码验证
                    if mode == "developer":
                        # 检查是否锁定
                        if get_developer_locked():
                            print(_("developer_locked"))
                            print(_("mode_failed"))
                            continue
                        
                        # 检查登录锁定状态
                        current_time = time.time()
                        login_lockout_until = get_config("login_lockout_until", 0)
                        
                        if current_time < login_lockout_until:
                            remaining_time = int(login_lockout_until - current_time)
                            minutes, seconds = divmod(remaining_time, 60)
                            print(_("login_too_many_attempts"))
                            print(_("login_lockout_time", minutes, seconds))
                            print(_("mode_failed"))
                            continue
                        
                        # 导入邮箱验证码模块
                        from github_shell.utils.email_verification import generate_and_send_verification, verify_code
                        
                        # 生成并发送验证码
                        print(_("developer_verification_request"))
                        code, expiry_time = generate_and_send_verification()
                        
                        if code:
                            # 保存验证码到配置
                            set_config("verification_code", code)
                            set_config("verification_expiry", expiry_time)
                            
                            # 提示用户输入验证码
                            entered_code = input("🔐 请输入收到的验证码: ").strip().upper()
                            
                            # 验证验证码
                            stored_code = get_config("verification_code")
                            stored_expiry = get_config("verification_expiry")
                            
                            if verify_code(entered_code, stored_code, stored_expiry):
                                # 验证码验证成功
                                print(_("verification_code_valid"))
                                # 清空验证码
                                set_config("verification_code", "")
                                set_config("verification_expiry", 0)
                                # 重置登录失败次数
                                set_config("login_failures", 0)
                            else:
                                # 验证码验证失败
                                print(_("verification_code_invalid"))
                                
                                # 增加登录失败次数
                                login_failures = get_config("login_failures", 0) + 1
                                max_failures = get_config("max_login_failures", 5)
                                
                                if login_failures >= max_failures:
                                    # 达到最大失败次数，锁定账户
                                    lockout_duration = get_config("lockout_duration", 300)
                                    lockout_until = current_time + lockout_duration
                                    set_config("login_lockout_until", lockout_until)
                                    minutes, seconds = divmod(lockout_duration, 60)
                                    print(_("verification_failure_lockout", login_failures))
                                    print(_("verification_lockout_duration", minutes))
                                else:
                                    # 未达到最大失败次数，继续尝试
                                    set_config("login_failures", login_failures)
                                    remaining_attempts = max_failures - login_failures
                                    print(_("verification_remaining_attempts", remaining_attempts))
                                
                                print(_("mode_failed"))
                                # 清空验证码
                                set_config("verification_code", "")
                                set_config("verification_expiry", 0)
                                continue
                        else:
                            print(_("verification_send_failed"))
                            print(_("mode_failed"))
                            continue
                    
                    if set_mode(mode):
                        # 根据模式类型获取显示名称
                        mode_display = _("mode_developer") if mode == "developer" else _("mode_user")
                        print(_("mode_set", mode_display))
                        # 重新显示欢迎信息以反映新模式
                        current_mode = get_mode()
                        if current_mode == "developer":
                            print(_("welcome_developer_mode"))
                        else:
                            print(_("welcome_user_mode"))
                    else:
                        print(_("mode_invalid"))
                        print(_("mode_failed"))
                elif cmd == "mode" and len(actual_args) == 0:
                    # 查看当前模式
                    current_mode = get_mode()
                    mode_display = _("mode_developer") if current_mode == "developer" else _("mode_user")
                    print(_("mode_show", mode_display))
                # 新功能：开发者模式锁定管理
                elif cmd == "developer-lock" and len(actual_args) == 1:
                    # 开发者模式锁定命令只能在开发者模式下使用
                    if get_mode() != "developer":
                        print(_("developer_commands_restricted"))
                        continue
                    
                    subcmd = actual_args[0].lower()
                    
                    if subcmd == "on":
                        # 锁定开发者模式
                        if set_developer_locked(True):
                            print(_("developer_locked"))
                        else:
                            print(_("developer_lock_failed"))
                    elif subcmd == "off":
                        # 解锁开发者模式
                        if set_developer_locked(False):
                            print(_("developer_unlocked"))
                        else:
                            print(_("developer_lock_failed"))
                    elif subcmd == "status":
                        # 查看锁定状态
                        locked = get_developer_locked()
                        lock_status = _("lock_status_locked") if locked else _("lock_status_unlocked")
                        print(_("lock_status_show", lock_status))
                    else:
                        print(_("unknown_cmd", f"developer-lock {subcmd}"))
                        print(_("help_cmd"))
                # 新功能：验证码配置管理
                elif cmd == "verification-config" and len(actual_args) >= 2:
                    # 验证码配置命令只能在开发者模式下使用
                    if get_mode() != "developer":
                        print(_("developer_commands_restricted"))
                        continue
                    
                    key = actual_args[0]
                    value = actual_args[1]
                    
                    # 验证码配置项
                    verification_configs = [
                        "smtp_server",
                        "smtp_port",
                        "sender_email",
                        "sender_password",
                        "recipient_email"
                    ]
                    
                    if key in verification_configs:
                        if set_config(key, value):
                            print(_("verification_config_set", key, value))
                        else:
                            print(_("verification_config_failed", key))
                    else:
                        print(_("verification_invalid_config", key))
                        print(_("verification_supported_configs", ', '.join(verification_configs)))
                # 新功能：停止命令（开发者模式专用）
                elif cmd == "stop" or cmd == "shutdown":
                    # 停止命令只能在开发者模式下使用
                    if get_mode() != "developer":
                        print(_("developer_commands_restricted"))
                        continue
                    print(_("stop_msg"))
                    sys.exit(0)
                # 紧急停止功能（无需开发者模式）
                elif cmd == "emergency-stop" or cmd == "kill" or cmd == "force-exit":
                    print(_("emergency_stop_warning"))
                    print(_("emergency_stop_confirm"))
                    sys.exit(1)
                else:
                    print(_("unknown_cmd", cmd))
                    print(_("help_cmd"))
            
            except KeyboardInterrupt:
                print("\n👋 退出 GitHub 仿真 Shell")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")

from github_shell.utils.path_utils import (
    is_script_in_path, add_scripts_dir_to_path,
    is_scripts_dir_in_path, get_python_scripts_path, get_path_help
)

def main():
    """主入口函数"""
    # 执行完整的安全性检查
    from github_shell.utils.tamper_proof import full_security_check
    if not full_security_check():
        print(_("security_check_failed"))
        print(_("security_check_contact_dev"))
        sys.exit(1)
    
    # 处理命令行参数
    if len(sys.argv) > 1:
        # 检查是否在开发者模式下执行管理命令
        if sys.argv[1] in ["--add-path", "--check-path", "--path-help"]:
            pass  # 这些命令可以在任何模式下执行
        else:
            # 其他命令行参数只能在开发者模式下使用
            from github_shell.utils.config import get_mode
            if get_mode() != "developer":
                print(_("developer_cmd_restricted"))
                print(_("developer_cmd_requires_mode"))
                sys.exit(1)
    
    # 检查并安装缺失的依赖
    if not check_and_install_dependencies():
        print(_("dependency_install_failed"))
        sys.exit(1)
    
    # 检查是否在PATH中，首次运行时提示
    if not is_script_in_path():
        print(_("path_not_in_path"))
        print(_("path_add_suggestion"))
        print(_("path_add_command"))
        print(_("path_help_suggestion"))
        print(_("path_help_command"))
        print()
    
    shell = GitHubShell()
    shell.run()

if __name__ == "__main__":
    main()
