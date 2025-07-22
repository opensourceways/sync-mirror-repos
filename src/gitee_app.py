import base64
import requests
import logging

from src.config import StrReadmeAddContent, DirName

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s: %(message)s")

SUC_StatusCode = [200, 201, 204]
ReadmeAddContent = bytes(StrReadmeAddContent, encoding="utf8")


class GiteeApp:

    def __init__(self,
                 access_token: str,
                 owner: str,
                 enterprise: str,
                 password: str,
                 v8_token: str
                 ):
        self.access_token = access_token
        self.owner = owner
        self.enterprise = enterprise
        self.base_v5_url = "https://gitee.com/api/v5/"
        self.password = password
        self.v8_token = v8_token

        self.enterprise_id = self.get_enterprise_id(self.base_v5_url, enterprise, access_token)

    @classmethod
    def get_enterprise_id(cls, base_url, enterprise, token) -> int:
        """
        获取企业id, 注意 enterprise 和 owner 并不等价
        :param base_url:
        :param enterprise:
        :param token:
        :return:
        """
        logging.info(f"get {enterprise} id...")
        url = f"{base_url}enterprises/{enterprise}?access_token={token}"
        response = requests.get(url)
        return response.json().get("id")

    def get_repo_id(self, repo):
        """
        获取代码仓id
        :param repo:
        :return:
        """
        url = f"{self.base_v5_url}repos/{self.owner}/{repo}?access_token={self.access_token}"
        response = requests.get(url)
        return response.json().get("id")

    def lock_repo(self, repo: str):
        logging.info(f"lock repo: {repo}")
        repo_id = self.get_repo_id(repo)
        url = f"https://api.gitee.com/enterprises/{self.enterprise_id}/projects/{repo_id}/status"
        params = dict(access_token=self.v8_token,
                      status=1,  # 0：开始，1：暂停，2：关闭
                      password=self.password,
                      validate_type='password'
                      )
        response = requests.put(url, params=params)
        if response.status_code not in SUC_StatusCode:
            logging.error(f"lock {repo} failure, {response.text}")

    def get_readme_content(self, repo):
        """
        获取readme 内容
        :param repo:
        :return:
        """
        url = f"{self.base_v5_url}repos/{self.owner}/{repo}/raw/README.md?access_token={self.access_token}"
        response = requests.get(url)
        if response.status_code not in SUC_StatusCode:
            logging.error(f"get repo {repo} readme fail, {response.text}")
        content = response.content
        return content

    def get_readme_sha(self, repo):
        """获取readme sha 值"""
        url = f"{self.base_v5_url}repos/{self.owner}/{repo}/readme?access_token={self.access_token}"
        response = requests.get(url)
        if response.status_code not in SUC_StatusCode:
            logging.error(f"get repo {repo} sha fail: {response.text}")
        return response.json().get("sha")

    def update_readme(self, repo):
        """
        在 readme 上新增迁移公告
        :param repo:
        :return:
        """
        content = self.get_readme_content(repo)
        sha = self.get_readme_sha(repo)

        content = ReadmeAddContent + content

        url = f"{self.base_v5_url}repos/{self.owner}/{repo}/contents/README.md"
        params = {
            "access_token": self.access_token,
            "content": base64.b64encode(content),
            "sha": sha,
            "message": "update README.md"
        }

        response = requests.put(url, params=params)
        if response.status_code not in SUC_StatusCode:
            logging.error(f"modify {repo} readme fail, {response.text}")

    def new_file_tips(self, repo):
        """
        新建文件夹, 显示迁移公告
        :param repo:
        :return:
        """
        url = f"{self.base_v5_url}repos/{self.owner}/{repo}/contents/{DirName}"
        params = {
            "access_token": self.access_token,
            "content": base64.b64encode(ReadmeAddContent),
            "message": "update README.md"
        }
        response = requests.post(url, params=params)
        if response.status_code not in SUC_StatusCode:
            logging.error(f"new {repo} dir fail, {response.text}")
