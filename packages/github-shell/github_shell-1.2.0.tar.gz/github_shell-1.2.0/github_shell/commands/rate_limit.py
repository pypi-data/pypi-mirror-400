#!/usr/bin/env python3
"""
速率限制命令模块
用于显示GitHub API的速率限制信息
"""

from github_shell.utils.request_utils import GitHubRequest
from github_shell.utils.language import _

class RateLimitCommand:
    """速率限制命令处理类"""
    
    def __init__(self):
        self.request = GitHubRequest()
    
    def show_rate_limit(self, output_format="print"):
        """显示GitHub API速率限制信息
        
        Args:
            output_format: 输出格式，"print"或"return"
            
        Returns:
            dict: 速率限制信息
        """
        # 调用GitHub API获取速率限制信息
        rate_limit = self.request.send_request("/rate_limit")
        result = {}
        
        if rate_limit:
            # 提取核心API的速率限制信息
            core = rate_limit.get("resources", {}).get("core", {})
            search = rate_limit.get("resources", {}).get("search", {})
            graphql = rate_limit.get("resources", {}).get("graphql", {})
            
            result = {
                "core": {
                    "limit": core.get("limit", 0),
                    "remaining": core.get("remaining", 0),
                    "reset": core.get("reset", 0)
                },
                "search": {
                    "limit": search.get("limit", 0),
                    "remaining": search.get("remaining", 0),
                    "reset": search.get("reset", 0)
                },
                "graphql": {
                    "limit": graphql.get("limit", 0),
                    "remaining": graphql.get("remaining", 0),
                    "reset": graphql.get("reset", 0)
                }
            }
        
        if output_format == "print":
            print("\n📊 GitHub API 速率限制：")
            print(f"  核心API: {result['core']['remaining']}/{result['core']['limit']} 剩余")
            print(f"  搜索API: {result['search']['remaining']}/{result['search']['limit']} 剩余")
            print(f"  GraphQL: {result['graphql']['remaining']}/{result['graphql']['limit']} 剩余")
            print("\n💡 提示：速率限制每小时重置一次")
        
        return result
