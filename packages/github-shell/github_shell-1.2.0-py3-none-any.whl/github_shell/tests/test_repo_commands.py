#!/usr/bin/env python3
"""
仓库命令测试
使用pytest框架
"""

from unittest.mock import patch, MagicMock
from github_shell.commands.repo_commands import RepoCommands

def test_list_repos():
    """测试列出仓库功能"""
    # 在实例化之前mock GitHubRequest类
    with patch('github_shell.commands.repo_commands.GitHubRequest') as mock_request_class:
        # 创建mock实例
        mock_request_instance = MagicMock()
        mock_request_class.return_value = mock_request_instance
        
        # 模拟API响应
        mock_response = [
            {"name": "test-repo-1", "stargazers_count": 10},
            {"name": "test-repo-2", "stargazers_count": 20}
        ]
        mock_request_instance.send_request.return_value = mock_response
        
        # 实例化RepoCommands
        repo_cmds = RepoCommands()
        
        # 测试返回值
        result = repo_cmds.list_repos(output_format="return")
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["name"] == "test-repo-1"
        assert result[0]["stars"] == 10

def test_show_repo():
    """测试查看仓库信息功能"""
    # 在实例化之前mock GitHubRequest类
    with patch('github_shell.commands.repo_commands.GitHubRequest') as mock_request_class:
        # 创建mock实例
        mock_request_instance = MagicMock()
        mock_request_class.return_value = mock_request_instance
        
        # 模拟API响应
        mock_response = {
            "name": "test-repo",
            "owner": {"login": "test-owner"},
            "description": "Test repository",
            "stargazers_count": 15,
            "forks_count": 5,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-02-01T00:00:00Z"
        }
        mock_request_instance.send_request.return_value = mock_response
        
        # 实例化RepoCommands
        repo_cmds = RepoCommands()
        
        # 测试返回值
        result = repo_cmds.show_repo("test-owner/test-repo", output_format="return")
        assert isinstance(result, dict)
        assert result["name"] == "test-repo"
        assert result["owner"] == "test-owner"
        assert result["stars"] == 15


