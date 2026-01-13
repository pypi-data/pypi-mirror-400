from github_shell.utils.request_utils import GitHubRequest
from github_shell.utils.config import get_github_username
from github_shell.utils.language import _

class UserCommands:
    """用户命令处理类"""
    
    def __init__(self):
        self.request = GitHubRequest()
    
    def show_user(self, username, output_format="print"):
        """查看指定用户信息"""
        user = self.request.send_request(f"/users/{username}")
        result = {
            "name": "N/A",
            "company": "N/A",
            "location": "N/A",
            "followers": 0,
            "following": 0,
            "public_repos": 0
        }
        
        if user:
            result = {
                "name": user.get('name') or user.get('login', 'N/A'),
                "company": user.get('company') or '无',
                "location": user.get('location') or '无',
                "followers": user.get('followers', 0),
                "following": user.get('following', 0),
                "public_repos": user.get('public_repos', 0)
            }
        
        if output_format == "print":      
            print(_("user_info", username))
            print(_("repo_name", result['name']))
            print(_("user_company", result['company']))
            print(_("user_location", result['location']))
            print(_("user_followers", result['followers']))
            print(_("user_following", result['following']))
            print(_("user_repos", result['public_repos']))
        
        return result
    
    def list_followers(self, output_format="print"):
        """查看当前用户的关注者"""
        username = get_github_username() or "wjr-2015"  # 默认值作为后备
        followers = self.request.send_request(f"/users/{username}/followers")
        result = [follower['login'] for follower in followers[:10]] if followers else []  # 只显示前10个
        
        if output_format == "print":
            print(_("user_followers_list", username))
            for follower in result:
                print(_("branch_format", follower))
        
        return result
    
    def list_following(self, output_format="print"):
        """查看当前用户关注的人"""
        username = get_github_username() or "wjr-2015"  # 默认值作为后备
        following = self.request.send_request(f"/users/{username}/following")
        result = [user['login'] for user in following[:10]] if following else []  # 只显示前10个
        
        if output_format == "print":
            print(_("user_following_list", username))
            for user in result:
                print(_("branch_format", user))
        
        return result
