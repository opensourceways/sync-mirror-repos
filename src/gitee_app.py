import requests
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s: %(message)s")


class GiteeApp:

    def __init__(self,
                 access_token: str,
                 ):
        self.access_token = access_token
        self.v5_url = "https://gitee.com/api/v5"

    def get_repos(self, owner: str) -> list[str]:
        """
        获取 owner 所有代码仓
        :return:
        """
        logging.info(f"Get {owner} repos...")
        url = f"{self.v5_url}/orgs/{owner}/repos?access_token={self.access_token}"
        page, per_page = 1, 100
        params = dict(per_page=per_page, page=page)
        repos = []
        while True:
            response = requests.get(url, params=params)
            cnt = response.headers.get("total_count")
            _repos = response.json()
            for _repo in _repos:
                repos.append(_repo.get("full_name"))

            if page * per_page > int(cnt):
                break
            page += 1
            params.update(page=page)

        return list(set(repos))

    def create_repo(self, owner: str, repo: str):
        """
        创建代码仓
        :param owner:
        :param repo:
        :return:
        """
        logging.info(f"Create {owner}/{repo} ...")
        url = f"{self.v5_url}/orgs/{owner}/repos?access_token={self.access_token}"
        data = {
            "name": repo,
        }
        response = requests.post(url, json=data)
        if response.status_code not in [200, 201, 204]:
            logging.error(f"create {owner}/{repo} fail...")
            logging.error(response.text)

    def get_branches(self, owner: str, repo: str):
        """
        获取代码仓所有分支
        :param repo:
        :param owner:
        :return:
        """
        url = f"{self.v5_url}/repos/{owner}/{repo}/branches?access_token={self.access_token}&per_page=100"
        page = 1
        branches = []
        while True:
            _url = url + f"&page={page}"
            response = requests.get(url)
            total_page = response.headers.get("total_page")
            data = response.json()
            branches.extend([x.get("name") for x in data])
            page += 1
            if int(total_page) < page:
                break
        return branches

    def delete_branch_rule(self, owner: str, repo: str, branch: str):
        """
        删除分支规则
        :param repo:
        :param branch:
        :param owner:
        :return:
        """
        url = f"{self.v5_url}/repos/{owner}/{repo}/branches/{branch}/setting?access_token={self.access_token}"
        response = requests.delete(url)
        logging.info(f"delete {repo}/{branch}...")
        if response.status_code not in [200, 201, 204]:
            logging.info(f"delete {repo}/{branch} rule fail...")
