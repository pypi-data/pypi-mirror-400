import requests
import os
import shutil
from datetime import datetime
from github_shell.utils.config import UPDATE_CONFIG
from github_shell.utils.language import _

class UpdateCommands:
    """更新命令处理类"""
    
    def check_for_updates(self):
        """检查并更新到最新版本"""
        print(_("checking_updates"))
        try:
            # 获取远程版本信息
            print(_("current_ver", UPDATE_CONFIG['version']))
            
            # 下载远程脚本内容
            response = requests.get(UPDATE_CONFIG['remote_url'])
            response.raise_for_status()
            
            # 检查是否有更新
            remote_content = response.text
            
            # 从远程脚本中提取版本信息
            remote_version = UPDATE_CONFIG['version']
            for line in remote_content.split('\n'):
                if 'version' in line and 'UPDATE_CONFIG' in line:
                    try:
                        # 提取版本号
                        remote_version = line.split('"')[3]
                        break
                    except (IndexError, ValueError):
                        continue
            
            if remote_version > UPDATE_CONFIG['version']:
                print(_("new_version_found", remote_version))
                print(_("updating"))
                
                # 备份当前文件
                backup_path = f"{__file__}.backup.{datetime.now().strftime('%Y%m%d%H%M%S')}"
                shutil.copy2(__file__, backup_path)
                print(_("backup_created", backup_path))
                
                # 写入新版本
                with open(__file__, 'w', encoding='utf-8') as f:
                    f.write(remote_content)
                
                print(_("update_success"))
            else:
                print(_("already_latest"))
                
        except Exception as e:
            print(_("update_failed", e))
    
    def show_version(self):
        """显示当前版本"""
        print(_("show_version", UPDATE_CONFIG['version']))
