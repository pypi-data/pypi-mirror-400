#!/usr/bin/env python3
"""
语言支持模块
用于处理多语言切换功能
"""

# 语言定义
LANGUAGES = {
    "english": {
        "welcome": "🎉 GitHub Simulation Shell",
        "current_version": "Current version: {}",
        "welcome_user": "Welcome, current user: {}",
        "help_tip": "Type 'help' for command list, 'exit' to quit\n",
        "prompt": "github-shell:{}$",
        "exit_msg": "\n👋 Exiting GitHub Simulation Shell",
        "unknown_cmd": "❌ Unknown command: {}",
        "help_cmd": "Type 'help' to see available commands",
        "list_repos": "\n📦 Listing repos for {}:",
        "repo_info": "\n📋 Repository info: {}",
        "repo_name": "  Name: {}",
        "repo_owner": "  Owner: {}",
        "repo_desc": "  Description: {}",
        "repo_stars": "  Stars: {}",
        "repo_forks": "  Forks: {}",
        "repo_created": "  Created at: {}",
        "repo_updated": "  Updated at: {}",
        "repo_issues": "\n📝 Issues for {}:",
        "issue_format": "  #{number}: {title} (by: {author})",
        "repo_branches": "\n🌿 Branches for {}:",
        "branch_format": "  - {}",
        "repo_commits": "\n📜 Recent commits for {}:",
        "commit_format": "  [{sha}] {author} {date}: {message}",
        "repo_contributors": "\n👥 Contributors for {}:",
        "contributor_format": "  - {login} (💻 {contributions} commits)",
        "repo_prs": "\n🔀 Pull Requests for {}:",
        "pr_format": "  #{number}: {title} (by: {author})",
        "user_gists": "\n📝 Gists for {}:",
        "gist_format": "  - {description} ({created_at}) Files: {files}",
        "search_repos": "\n🔍 Searching repos: {}",
        "search_result": "  - {full_name} (⭐ {stars})\n    {description}",
        "org_info": "\n🏢 Organization info: {}",
        "org_name": "  Name: {}",
        "org_desc": "  Description: {}",
        "org_repos": "  Public repos: {}",
        "org_members": "  Members: {}",
        "user_info": "\n👤 User info: {}",
        "user_company": "  Company: {}",
        "user_location": "  Location: {}",
        "user_followers": "  Followers: {}",
        "user_following": "  Following: {}",
        "user_repos": "  Public repos: {}",
        "user_followers_list": "\n👥 Followers of {}:",
        "user_following_list": "\n👥 Following of {}:",
        "checking_updates": "\n🔄 Checking for updates...",
        "current_ver": "Current version: {}",
        "new_version_found": "Found new version: {}",
        "updating": "Updating...",
        "backup_created": "Backup created: {}",
        "update_success": "✅ Update successful! Please restart the script to use the new version.",
        "already_latest": "✅ Already the latest version",
        "update_failed": "❌ Update failed: {}",
        "show_version": "\n📋 GitHub Simulation Shell version: {}",
        "language_changed": "✅ Language changed to: {}",
        "checking_dependencies": "🔍 Checking dependencies...",
        "dependency_installed": "✅ {} is installed",
        "dependency_not_installed": "❌ {} is not installed",
        "missing_dependencies_found": "\n📦 Found {} missing dependencies, trying to install...",
        "dependencies_installed_success": "✅ All dependencies installed successfully!",
        "dependencies_installed_failed": "❌ Failed to install dependencies, please install manually:",
        "all_dependencies_installed": "✅ All dependencies are already installed",
        "github_username_set": "✅ GitHub username set to: {}",
        "github_username_failed": "❌ Failed to set GitHub username",
        "github_username_show": "Current GitHub username: {}",
        "github_username_not_set": "Current GitHub username: Not set",
        "github_email_set": "✅ GitHub email set to: {}",
        "github_email_failed": "❌ Failed to set GitHub email",
        "github_email_show": "Current GitHub email: {}",
        "github_email_not_set": "Current GitHub email: Not set",
        "github_token_set": "✅ GitHub token set: {}",
        "github_token_failed": "❌ Failed to set GitHub token",
        "github_token_show": "Current GitHub token: {}",
        "github_token_not_set": "Current GitHub token: Not set",
        "github_token_cleared": "✅ GitHub token cleared",
        "github_token_clear_failed": "❌ Failed to clear GitHub token",
        "github_info_title": "📋 GitHub Account Information:",
        "github_info_username": "  Username: {}",
        "github_info_email": "  Email: {}",
        "github_info_token": "  Token: {}",
        "github_info_token_set": "Set",
        "github_info_token_not_set": "Not set",
        "mode_set": "✅ Mode changed to: {}",
        "mode_failed": "❌ Failed to change mode",
        "mode_show": "Current mode: {}",
        "mode_user": "User Mode",
        "mode_developer": "Developer Mode",
        "mode_invalid": "Invalid mode. Supported modes: user, developer",
        "welcome_user_mode": "🎉 GitHub Simulation Shell (User Mode)",
        "welcome_developer_mode": "🔧 GitHub Simulation Shell (Developer Mode)",
        "developer_password_set": "✅ Developer password set successfully",
        "developer_password_cleared": "✅ Developer password cleared",
        "developer_password_failed": "❌ Failed to set developer password",
        "developer_locked": "🔒 Developer mode is locked",
        "developer_unlocked": "🔓 Developer mode is unlocked",
        "developer_lock_failed": "❌ Failed to change lock status",
        "enter_developer_password": "🔑 Enter developer password: ",
        "password_incorrect": "❌ Incorrect password",
        "developer_mode_restricted": "❌ Developer mode is restricted",
        "developer_commands_restricted": "❌ This command is only available in developer mode",
        "password_not_set": "⚠️  Developer password is not set",
        "lock_status_show": "Current lock status: {}",
        "lock_status_locked": "Locked",
        "lock_status_unlocked": "Unlocked",
        "stop_msg": "\n🔒 Stopping GitHub Simulation Shell",
        # 测试功能相关
        "testing_command": "Testing command: {}",
        "testing_language_switch": "Testing language switching...",
        "current_language": "Current language: {}",
        "switched_to": "Switched to: {}",
        "switched_back_to": "Switched back to: {}",
        "invalid_test_command": "Invalid test command",
        "unsupported_test_command": "Unsupported test command: {}",
        "test_completed": "Test completed",
        "separator": "=" * 50,
        # 配置相关
        "config_set": "✅ 配置已设置：{} = {}",
        "config_value": "  {}: {}",
        "config_not_found": "❌ 配置项不存在：{}",
        "config_current": "\n⚙️ 当前配置：",
        "config_reset": "✅ 配置已重置为默认值",
        # 令牌相关
        "token_saved": "⚠️  令牌已保存到配置文件",
        # 系统相关
        "exit_message": "\n👋 退出 GitHub 仿真 Shell",
        "error_occurred": "❌ 发生错误: {}",
        # PATH相关
        "adding_path": "正在将Python Scripts目录添加到系统PATH...",
        "target_path": "目标路径: {}",
        "path_added_success": "✅ 成功添加到PATH！",
        "path_added_restart": "⚠️  请重启命令行窗口或终端以生效",
        "path_added_failed": "❌ 添加失败，请手动添加",
        "emergency_stop_warning": "⚠️ 紧急停止！程序将立即终止",
        "emergency_stop_confirm": "🔴 紧急停止已执行，程序正在终止...",
        "separator_line": "=" * 50,
        "testing_switched_back": "Switched back to: {}",
        "testing_invalid_command": "Invalid test command",
        "testing_unsupported_command": "Unsupported test command: {}",
        "testing_completed": "Test completed",
        "invalid_language": "❌ Invalid language: {}. Supported: en, zh",
        "config_set_success": "✅ Config set: {} = {}",
        "config_set_failed": "❌ Failed to set config: {}",
        "config_value": "  {}: {}",
        "config_not_found": "❌ Config not found: {}",
        "config_current": "\n⚙️ Current configuration:",
        "config_reset_success": "✅ Config reset to default values",
        "token_saved_warning": "⚠️ Token saved to config file",
        "login_too_many_attempts": "❌ Too many login attempts, account locked",
        "login_lockout_time": "⏰ Please try again in {} minutes and {} seconds",
        "developer_verification_request": "📧 Sending verification request to developer admin wjr",
        "verification_code_valid": "✅ Verification code valid",
        "verification_code_invalid": "❌ Invalid or expired verification code",
        "verification_failure_lockout": "❌ {} consecutive verification failures",
        "verification_lockout_duration": "⏰ Account locked for {} minutes, please try later",
        "verification_remaining_attempts": "⚠️ {} attempts remaining",
        "verification_send_failed": "❌ Failed to send verification code",
        "verification_config_set": "✅ Verification config set: {} = {}",
        "verification_config_failed": "❌ Failed to set verification config: {}",
        "verification_invalid_config": "❌ Invalid verification config: {}",
        "verification_supported_configs": "Supported configs: {}",
        "security_check_failed": "\n❌ Project security check failed, potential tampering risk",
        "security_check_contact_dev": "Please contact developer or reinstall the program",
        "developer_cmd_restricted": "❌ This command is only available in developer mode",
        "developer_cmd_requires_mode": "Please switch to developer mode first: mode developer",
        "dependency_install_failed": "\n❌ Dependency installation failed, unable to start program",
        "path_not_in_path": "\n⚠️ Tip: github-shell command is not in system PATH",
        "path_add_suggestion": "You can add it to PATH using:",
        "path_add_command": "  github-shell --add-path",
        "path_help_suggestion": "Or view help:",
        "path_help_command": "  github-shell --path-help",
        "tamper_saving_checksum_failed": "❌ Failed to save checksums: {}",
        "tamper_invalid_signature": "❌ Invalid checksum file signature, possibly tampered with",
        "tamper_loading_checksum_failed": "❌ Failed to load checksums: {}",
        "tamper_no_valid_checksum": "⚠️  No valid checksum file found, generating...",
        "tamper_checksum_generated": "✅ Checksums generated and saved successfully",
        "tamper_checksum_generation_failed": "❌ Failed to generate checksums",
        "tamper_verifying_files": "🔐 Verifying file integrity using {} algorithm...",
        "tamper_new_file_detected": "⚠️ {} - New file detected, need to update checksums",
        "tamper_file_verified": "✅ {} - Verification passed",
        "tamper_file_tampered": "❌ {} - Verification failed! File may have been tampered with",
        "tamper_expected_hash": "   Expected: {}",
        "tamper_actual_hash": "   Actual: {}",
        "tamper_file_missing": "❌ {} - File missing",
        "tamper_verifying_integrity": "🔍 Performing project integrity verification...",
        "tamper_verifying_dependencies": "📦 Verifying dependency integrity...",
        "tamper_dependency_verified": "✅ Dependency {} - Verification passed",
        "tamper_dependency_missing": "❌ Dependency {} - Missing",
        "tamper_full_security_check": "🔒 Performing full security check...",
        "tamper_file_integrity_check": "File Integrity Verification",
        "tamper_dependency_integrity_check": "Dependency Integrity Verification",
        "tamper_all_checks_passed": "🎉 All security checks passed!",
        "tamper_security_check_failed": "❌ Security check failed!",
        "email_send_failed": "❌ Failed to send verification code: {}",
        "security_check_failed_exit": "❌ Security check failed, program will exit to protect system security",
        "testing_command": "Testing command: {}",
        "testing_language_switching": "Testing language switching...",
        "testing_current_language": "Current language: {}",
        "testing_switched_to": "Switched to: {}",
        "help_text": """GitHub Simulation Shell Command List:

Repository Operations:
  repos                 - List current user's repositories
  repo <owner>/<repo>   - View specified repository information
  issues <repo>         - View repository issues
  branches <repo>       - View repository branches
  commits <repo>        - View recent commits
  contributors <repo>   - View repository contributors
  prs <repo>            - View Pull Requests
  gists <username>      - View user's Gists

Search Operations:
  search <query>        - Search GitHub repositories

Organization Operations:
  org <orgname>         - View specified organization information

User Operations:
  user <username>       - View specified user information
  followers             - View current user's followers
  following             - View users current user is following

System Commands:
  help                  - Show this help message
  clear                 - Clear the screen
  exit                  - Exit the simulation shell
  stop/shutdown         - Stop GitHub Shell (developer mode only)
  update                - Check and update to latest version
  version               - Show current version
  language <lang>       - Change language (en/zh)
"""
    },
    "chinese": {
        "welcome": "🎉 GitHub 仿真 Shell",
        "current_version": "当前版本: {}",
        "welcome_user": "欢迎使用，当前用户：{}",
        "help_tip": "输入 'help' 查看命令列表，输入 'exit' 退出\n",
        "prompt": "github-shell:{}$",
        "exit_msg": "\n👋 退出 GitHub 仿真 Shell",
        "unknown_cmd": "❌ 未知命令: {}",
        "help_cmd": "输入 'help' 查看可用命令",
        "list_repos": "\n📦 列出 {} 的仓库：",
        "repo_info": "\n📋 仓库信息：{}",
        "repo_name": "  名称: {}",
        "repo_owner": "  所有者: {}",
        "repo_desc": "  描述: {}",
        "repo_stars": "  星级: {}",
        "repo_forks": "  Forks: {}",
        "repo_created": "  创建时间: {}",
        "repo_updated": "  更新时间: {}",
        "repo_issues": "\n📝 {} 的Issues：",
        "issue_format": "  #{number}: {title} (创建者: {author})",
        "repo_branches": "\n🌿 {} 的分支：",
        "branch_format": "  - {}",
        "repo_commits": "\n📜 {} 的最近提交：",
        "commit_format": "  [{sha}] {author} {date}: {message}",
        "repo_contributors": "\n👥 {} 的贡献者：",
        "contributor_format": "  - {login} (💻 {contributions} 次提交)",
        "repo_prs": "\n🔀 {} 的Pull Requests：",
        "pr_format": "  #{number}: {title} (创建者: {author})",
        "user_gists": "\n📝 {} 的Gists：",
        "gist_format": "  - {description} ({created_at}) 文件: {files}",
        "search_repos": "\n🔍 搜索仓库: {}",
        "search_result": "  - {full_name} (⭐ {stars})\n    {description}",
        "org_info": "\n🏢 组织信息：{}",
        "org_name": "  名称: {}",
        "org_desc": "  描述: {}",
        "org_repos": "  公开仓库: {}",
        "org_members": "  成员数量: {}",
        "user_info": "\n👤 用户信息：{}",
        "user_company": "  公司: {}",
        "user_location": "  位置: {}",
        "user_followers": "  关注者: {}",
        "user_following": "  关注的人: {}",
        "user_repos": "  仓库数量: {}",
        "user_followers_list": "\n👥 {} 的关注者：",
        "user_following_list": "\n👥 {} 关注的人：",
        "checking_updates": "\n🔄 检查更新...",
        "current_ver": "当前版本: {}",
        "new_version_found": "发现新版本: {}",
        "updating": "正在更新...",
        "backup_created": "已备份当前版本到: {}",
        "update_success": "✅ 更新成功！请重新运行脚本以使用新版本。",
        "already_latest": "✅ 当前已是最新版本",
        "update_failed": "❌ 更新失败: {}",
        "show_version": "\n📋 GitHub 仿真 Shell 版本: {}",
        "language_changed": "✅ 语言已更改为: {}",
        "checking_dependencies": "🔍 检查依赖库...",
        "dependency_installed": "✅ {} 已安装",
        "dependency_not_installed": "❌ {} 未安装",
        "missing_dependencies_found": "\n📦 发现 {} 个缺失依赖，尝试安装...",
        "dependencies_installed_success": "✅ 所有依赖安装成功！",
        "dependencies_installed_failed": "❌ 依赖安装失败，请手动安装:",
        "all_dependencies_installed": "✅ 所有依赖已安装",
        "github_username_set": "✅ GitHub用户名已设置：{}",
        "github_username_failed": "❌ 用户名设置失败",
        "github_username_show": "当前GitHub用户名：{}",
        "github_username_not_set": "当前GitHub用户名：未设置",
        "github_email_set": "✅ GitHub邮箱已设置：{}",
        "github_email_failed": "❌ 邮箱设置失败",
        "github_email_show": "当前GitHub邮箱：{}",
        "github_email_not_set": "当前GitHub邮箱：未设置",
        "github_token_set": "✅ GitHub令牌已设置：{}",
        "github_token_failed": "❌ 令牌设置失败",
        "github_token_show": "当前GitHub令牌：{}",
        "github_token_not_set": "当前GitHub令牌：未设置",
        "github_token_cleared": "✅ GitHub令牌已清除",
        "github_token_clear_failed": "❌ 令牌清除失败",
        "github_info_title": "📋 GitHub账号信息：",
        "github_info_username": "  用户名：{}",
        "github_info_email": "  邮箱：{}",
        "github_info_token": "  令牌：{}",
        "github_info_token_set": "已设置",
        "github_info_token_not_set": "未设置",
        "mode_set": "✅ 模式已更改为：{}",
        "mode_failed": "❌ 模式更改失败",
        "mode_show": "当前模式：{}",
        "mode_user": "用户模式",
        "mode_developer": "开发者模式",
        "mode_invalid": "无效模式。支持的模式：user, developer",
        "welcome_user_mode": "🎉 GitHub 仿真 Shell (用户模式)",
        "welcome_developer_mode": "🔧 GitHub 仿真 Shell (开发者模式)",
        "developer_password_set": "✅ 开发者密码设置成功",
        "developer_password_cleared": "✅ 开发者密码已清除",
        "developer_password_failed": "❌ 设置开发者密码失败",
        "developer_locked": "🔒 开发者模式已锁定",
        "developer_unlocked": "🔓 开发者模式已解锁",
        "developer_lock_failed": "❌ 更改锁定状态失败",
        "enter_developer_password": "🔑 输入开发者密码: ",
        "password_incorrect": "❌ 密码错误",
        "developer_mode_restricted": "❌ 开发者模式已被限制",
        "developer_commands_restricted": "❌ 此命令仅在开发者模式下可用",
        "password_not_set": "⚠️  开发者密码未设置",
        "lock_status_show": "当前锁定状态: {}",
        "lock_status_locked": "已锁定",
        "lock_status_unlocked": "未锁定",
        "stop_msg": "\n🔒 停止 GitHub 仿真 Shell",
        # 测试功能相关
        "testing_command": "测试命令: {}",
        "testing_language_switch": "测试语言切换...",
        "current_language": "当前语言: {}",
        "switched_to": "已切换到: {}",
        "switched_back_to": "已切换回: {}",
        "invalid_test_command": "无效的测试命令",
        "unsupported_test_command": "不支持的测试命令: {}",
        "test_completed": "测试完成",
        "separator": "=" * 50,
        # 配置相关
        "config_set": "✅ 配置已设置：{} = {}",
        "config_value": "  {}: {}",
        "config_not_found": "❌ 配置项不存在：{}",
        "config_current": "\n⚙️ 当前配置：",
        "config_reset": "✅ 配置已重置为默认值",
        # 令牌相关
        "token_saved": "⚠️  令牌已保存到配置文件",
        # 系统相关
        "exit_message": "\n👋 退出 GitHub 仿真 Shell",
        "error_occurred": "❌ 发生错误: {}",
        # PATH相关
        "adding_path": "正在将Python Scripts目录添加到系统PATH...",
        "target_path": "目标路径: {}",
        "path_added_success": "✅ 成功添加到PATH！",
        "path_added_restart": "⚠️  请重启命令行窗口或终端以生效",
        "path_added_failed": "❌ 添加失败，请手动添加",
        "emergency_stop_warning": "⚠️ 紧急停止！程序将立即终止",
        "emergency_stop_confirm": "🔴 紧急停止已执行，程序正在终止...",
        "separator_line": "=" * 50,
        "testing_switched_back": "已切换回: {}",
        "testing_invalid_command": "无效的测试命令",
        "testing_unsupported_command": "不支持的测试命令: {}",
        "testing_completed": "测试完成",
        "invalid_language": "❌ 无效的语言: {}. 支持: en, zh",
        "config_set_success": "✅ 配置已设置：{} = {}",
        "config_set_failed": "❌ 配置设置失败：{}",
        "config_value": "  {}: {}",
        "config_not_found": "❌ 配置项不存在：{}",
        "config_current": "\n⚙️ 当前配置：",
        "config_reset_success": "✅ 配置已重置为默认值",
        "token_saved_warning": "⚠️  令牌已保存到配置文件",
        "login_too_many_attempts": "❌ 登录尝试次数过多，账户已锁定",
        "login_lockout_time": "⏰ 请在 {}分{}秒后再尝试",
        "developer_verification_request": "📧 正在发送请求给开发者管理员wjr",
        "verification_code_valid": "✅ 验证码验证成功",
        "verification_code_invalid": "❌ 验证码错误或已过期",
        "verification_failure_lockout": "❌ 连续{}次验证失败",
        "verification_lockout_duration": "⏰ 账户已锁定{}分钟，请稍后再试",
        "verification_remaining_attempts": "⚠️  还有 {} 次尝试机会",
        "verification_send_failed": "❌ 验证码发送失败",
        "verification_config_set": "✅ 验证码配置已设置：{} = {}",
        "verification_config_failed": "❌ 验证码配置设置失败：{}",
        "verification_invalid_config": "❌ 无效的验证码配置项：{}",
        "verification_supported_configs": "支持的配置项：{}",
        "security_check_failed": "\n❌ 项目安全性检查失败，可能存在篡改风险",
        "security_check_contact_dev": "请联系开发者或重新安装程序",
        "developer_cmd_restricted": "❌ 此命令仅在开发者模式下可用",
        "developer_cmd_requires_mode": "请先切换到开发者模式: mode developer",
        "dependency_install_failed": "\n❌ 依赖安装失败，无法启动程序",
        "path_not_in_path": "\n⚠️  提示：github-shell 命令不在系统PATH中",
        "path_add_suggestion": "您可以使用以下命令将其添加到PATH：",
        "path_add_command": "  github-shell --add-path",
        "path_help_suggestion": "或查看帮助：",
        "path_help_command": "  github-shell --path-help",
        "tamper_saving_checksum_failed": "❌ 保存校验和失败: {}",
        "tamper_invalid_signature": "❌ 校验和文件签名无效，可能被篡改",
        "tamper_loading_checksum_failed": "❌ 加载校验和失败: {}",
        "tamper_no_valid_checksum": "⚠️  未找到有效校验和文件，正在生成...",
        "tamper_checksum_generated": "✅ 校验和生成并保存成功",
        "tamper_checksum_generation_failed": "❌ 校验和生成失败",
        "tamper_verifying_files": "🔐 使用{}算法验证文件完整性...",
        "tamper_new_file_detected": "⚠️ {} - 新增文件，需要更新校验和",
        "tamper_file_verified": "✅ {} - 验证通过",
        "tamper_file_tampered": "❌ {} - 验证失败！文件可能被篡改",
        "tamper_expected_hash": "   预期: {}",
        "tamper_actual_hash": "   实际: {}",
        "tamper_file_missing": "❌ {} - 文件缺失",
        "tamper_verifying_integrity": "🔍 正在进行项目完整性验证...",
        "tamper_verifying_dependencies": "📦 正在验证依赖完整性...",
        "tamper_dependency_verified": "✅ 依赖 {} - 验证通过",
        "tamper_dependency_missing": "❌ 依赖 {} - 缺失",
        "tamper_full_security_check": "🔒 正在进行完整安全性检查...",
        "tamper_file_integrity_check": "文件完整性验证",
        "tamper_dependency_integrity_check": "依赖完整性验证",
        "tamper_all_checks_passed": "🎉 所有安全检查通过！",
        "tamper_security_check_failed": "❌ 安全检查失败！",
        "email_send_failed": "❌ 发送验证码失败: {}",
        "security_check_failed_exit": "❌ 安全检查失败，程序将退出以保护系统安全",
        "testing_command": "测试命令: {}",
        "testing_language_switching": "测试语言切换...",
        "testing_current_language": "当前语言: {}",
        "testing_switched_to": "已切换到: {}",
        "help_text": """GitHub 仿真 Shell 命令列表：

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
  language <lang>       - 切换语言 (en/zh)
"""
    }
}

# 当前语言
_current_language = "english"

def get_language():
    """获取当前语言"""
    return _current_language

def set_language(lang):
    """设置当前语言
    
    Args:
        lang: 语言代码，支持 "english"（英语）和 "chinese"（中文）
        
    Returns:
        bool: 是否成功设置
    """
    global _current_language
    if lang in LANGUAGES:
        _current_language = lang
        return True
    return False

def _(key, *args, **kwargs):
    """获取翻译文本
    
    Args:
        key: 文本键名
        *args: 位置参数
        **kwargs: 关键字参数
        
    Returns:
        str: 翻译后的文本
    """
    lang_dict = LANGUAGES.get(_current_language, LANGUAGES["english"])
    return lang_dict.get(key, key).format(*args, **kwargs)
