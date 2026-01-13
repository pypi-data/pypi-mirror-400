from datetime import datetime
from github_shell.utils.request_utils import GitHubRequest
from github_shell.utils.config import get_github_username
from github_shell.utils.language import _

class RepoCommands:
    """仓库命令处理类"""
    
    def __init__(self):
        self.request = GitHubRequest()
    
    def list_repos(self, output_format="print"):
        """列出当前用户的仓库"""
        username = get_github_username() or "wjr-2015"  # 默认值作为后备
        repos = self.request.send_request(f"/users/{username}/repos")
        result = []
        
        if repos:
            for repo in repos[:10]:  # 只显示前10个
                repo_info = {
                    "name": repo['name'],
                    "stars": repo['stargazers_count']
                }
                result.append(repo_info)
                
        if output_format == "print":
            print(_("list_repos", username))
            for repo in result:
                print(f"  - {repo['name']} (⭐ {repo['stars']})")
        
        return result
    
    def show_repo(self, repo_fullname, output_format="print"):
        """查看指定仓库信息"""
        repo = self.request.send_request(f"/repos/{repo_fullname}")
        result = {}
        
        if repo:
            result = {
                "name": repo['name'],
                "owner": repo['owner']['login'],
                "description": repo['description'] or '无',
                "stars": repo['stargazers_count'],
                "forks": repo['forks_count'],
                "created_at": datetime.strptime(repo['created_at'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S'),
                "updated_at": datetime.strptime(repo['updated_at'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S')
            }
        
        if output_format == "print":
            print(_("repo_info", repo_fullname))
            print(_("repo_name", result['name']))
            print(_("repo_owner", result['owner']))
            print(_("repo_desc", result['description']))
            print(_("repo_stars", result['stars']))
            print(_("repo_forks", result['forks']))
            print(_("repo_created", result['created_at']))
            print(_("repo_updated", result['updated_at']))
        
        return result
    
    def show_issues(self, repo_fullname, output_format="print"):
        """查看仓库的Issues"""
        issues = self.request.send_request(f"/repos/{repo_fullname}/issues", params={"state": "open", "per_page": 5})
        result = []
        
        if issues:
            for issue in issues:
                issue_info = {
                    "number": issue['number'],
                    "title": issue['title'],
                    "author": issue['user']['login']
                }
                result.append(issue_info)
        
        if output_format == "print":
            print(_("repo_issues", repo_fullname))
            for issue in result:
                print(_("issue_format", number=issue['number'], title=issue['title'], author=issue['author']))
        
        return result
    
    def show_branches(self, repo_fullname, output_format="print"):
        """查看仓库的分支"""
        branches = self.request.send_request(f"/repos/{repo_fullname}/branches")
        result = [branch['name'] for branch in branches[:10]]  # 只显示前10个
        
        if output_format == "print":
            print(_("repo_branches", repo_fullname))
            for branch in result:
                print(_("branch_format", branch))
        
        return result
    
    def show_commits(self, repo_fullname, output_format="print"):
        """查看仓库的最近提交"""
        commits = self.request.send_request(f"/repos/{repo_fullname}/commits", params={"per_page": 5})
        result = []
        
        if commits:
            for commit in commits:
                sha = commit['sha'][:7]
                author = commit['commit']['author']['name']
                date = datetime.strptime(commit['commit']['author']['date'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d')
                message = commit['commit']['message']
                
                commit_info = {
                    "sha": sha,
                    "author": author,
                    "date": date,
                    "message": message
                }
                result.append(commit_info)
        
        if output_format == "print":
            print(_("repo_commits", repo_fullname))
            for commit in result:
                print(_("commit_format", sha=commit['sha'], author=commit['author'], date=commit['date'], message=commit['message']))
        
        return result
    
    def show_contributors(self, repo_fullname, output_format="print"):
        """查看仓库的贡献者"""
        contributors = self.request.send_request(f"/repos/{repo_fullname}/contributors")
        result = []
        
        if contributors:
            for contributor in contributors[:10]:  # 只显示前10个
                contributor_info = {
                    "login": contributor['login'],
                    "contributions": contributor['contributions']
                }
                result.append(contributor_info)
        
        if output_format == "print":
            print(_("repo_contributors", repo_fullname))
            for contributor in result:
                print(_("contributor_format", login=contributor['login'], contributions=contributor['contributions']))
        
        return result
    
    def show_prs(self, repo_fullname, output_format="print"):
        """查看仓库的Pull Requests"""
        prs = self.request.send_request(f"/repos/{repo_fullname}/pulls", params={"state": "open", "per_page": 5})
        result = []
        
        if prs:
            for pr in prs:
                pr_info = {
                    "number": pr['number'],
                    "title": pr['title'],
                    "author": pr['user']['login']
                }
                result.append(pr_info)
        
        if output_format == "print":
            print(_("repo_prs", repo_fullname))
            for pr in result:
                print(_("pr_format", number=pr['number'], title=pr['title'], author=pr['author']))
        
        return result
    
    def show_gists(self, username, output_format="print"):
        """查看用户的Gists"""
        gists = self.request.send_request(f"/users/{username}/gists")
        result = []
        
        if gists:
            for gist in gists[:5]:  # 只显示前5个
                description = gist['description'] or '无描述'
                created_at = datetime.strptime(gist['created_at'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d')
                files = list(gist['files'].keys())
                
                gist_info = {
                    "description": description,
                    "created_at": created_at,
                    "files": files
                }
                result.append(gist_info)
        
        if output_format == "print":
            print(_("user_gists", username))
            for gist in result:
                files_str = ', '.join(gist['files'][:3])
                if len(gist['files']) > 3:
                    files_str += '...'
                print(_("gist_format", description=gist['description'], created_at=gist['created_at'], files=files_str))
        
        return result
