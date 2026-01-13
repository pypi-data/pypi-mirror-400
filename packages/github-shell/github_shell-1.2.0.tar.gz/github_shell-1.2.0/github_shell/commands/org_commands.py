from github_shell.utils.request_utils import GitHubRequest
from github_shell.utils.language import _

class OrgCommands:
    """组织命令处理类"""
    
    def __init__(self):
        self.request = GitHubRequest()
    
    def show_org(self, orgname, output_format="print"):
        """查看指定组织信息"""
        org = self.request.send_request(f"/orgs/{orgname}")
        result = {
            "name": "N/A",
            "description": "N/A",
            "public_repos": 0,
            "public_members_count": 0
        }
        
        if org:
            result = {
                "name": org.get('name') or org.get('login', 'N/A'),
                "description": org.get('description') or '无',
                "public_repos": org.get('public_repos', 0),
                "public_members_count": org.get('public_members_count', 0) or org.get('members_count', 0)
            }
        
        if output_format == "print":      
            print(_("org_info", orgname))
            print(_("repo_name", result['name']))
            print(_("repo_desc", result['description']))
            print(_("org_repos", result['public_repos']))
            print(_("org_members", result['public_members_count']))
        
        return result
