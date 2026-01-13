from github_shell.utils.request_utils import GitHubRequest
from github_shell.utils.language import _

class SearchCommands:
    """搜索命令处理类"""
    
    def __init__(self):
        self.request = GitHubRequest()
    
    def search_repos(self, query, output_format="print"):
        """搜索GitHub仓库"""
        results = self.request.send_request(f"/search/repositories", params={"q": query, "per_page": 5})
        result = []
        
        if results and 'items' in results:
            for repo in results['items']:
                repo_info = {
                    "full_name": repo['full_name'],
                    "stars": repo['stargazers_count'],
                    "description": repo['description'] or '无描述'
                }
                result.append(repo_info)
        
        if output_format == "print":
            print(_("search_repos", query))
            for repo in result:
                print(_("search_result", full_name=repo['full_name'], stars=repo['stars'], description=repo['description']))
        
        return result
