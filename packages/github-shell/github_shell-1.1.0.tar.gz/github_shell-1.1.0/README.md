# GitHub 仿真 Shell

一个功能丰富的GitHub仿真Shell，提供类似命令行界面的GitHub操作体验。

## 功能特性

### 仓库操作
- `repos` - 列出当前用户的仓库
- `repo <owner>/<repo>` - 查看指定仓库信息
- `issues <repo>` - 查看仓库的Issues
- `branches <repo>` - 查看仓库的分支
- `commits <repo>` - 查看仓库的最近提交
- `contributors <repo>` - 查看仓库的贡献者
- `prs <repo>` - 查看仓库的Pull Requests
- `gists <username>` - 查看用户的Gists

### 搜索功能
- `search <query>` - 搜索GitHub仓库

### 组织操作
- `org <orgname>` - 查看指定组织信息

### 用户操作
- `user <username>` - 查看指定用户信息
- `followers` - 查看当前用户的关注者
- `following` - 查看当前用户关注的人

### 系统命令
- `help` - 显示帮助信息
- `clear` - 清除屏幕
- `exit` - 退出仿真Shell
- `update` - 检查并更新到最新版本
- `version` - 显示当前版本

## 安装方法

### 从PyPI安装
```bash
pip install github-shell
```

### 从源码安装
```bash
git clone https://github.com/wjr-2015/github-shell.git
cd github-shell
pip install -e .
```

## 使用方法

### 基本使用
```bash
github-shell
```

### 命令示例
```bash
# 列出当前用户的仓库
github-shell:wjr-2015$ repos

# 查看指定仓库信息
github-shell:wjr-2015$ repo octocat/Hello-World

# 搜索仓库
github-shell:wjr-2015$ search python github

# 检查更新
github-shell:wjr-2015$ update
```

## 配置

### 设置GitHub令牌
为了访问私有仓库，您可以在脚本中设置GitHub令牌：

```python
# 在github_shell/config.py中设置
TOKEN = "your_github_token"
```

## 自动更新

该脚本包含自动更新功能，运行`update`命令即可检查并更新到最新版本。

## 版本历史

- v1.1.0 - 新增贡献者查看、PR查看、Gists查看、仓库搜索、组织信息查看等功能
- v1.0.0 - 初始版本，包含基本的仓库和用户操作

## 许可证

MIT License
