import requests
from github_shell.utils.config import GITHUB_API, get_github_token

class GitHubRequest:
    """GitHub API请求工具类"""
    
    def __init__(self):
        self.session = requests.Session()
        token = get_github_token()
        if token:
            self.session.headers.update({"Authorization": f"token {token}"})
    
    def send_request(self, endpoint, method="GET", params=None):
        """发送GitHub API请求"""
        url = f"{GITHUB_API}{endpoint}"
        try:
            if method == "GET":
                response = self.session.get(url, params=params)
            else:
                response = self.session.post(url, json=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None
