import requests
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s: %(message)s")


class GithubApp:

    def __init__(self,
                 access_token: str,
                 ):
        self.access_token = access_token
        self.base_url = "https://api.github.com"
        self.headers = dict(Authorization=f"Bearer {self.access_token}")

    def get_repos(self, owner: str) -> list[str]:
        """
        获取 owner 所有代码仓
        :param owner:
        :return:
        """
        url = f"{self.base_url}/orgs/{owner}/repos?per_page=30"
        repos = []
        page = 1

        while True:
            _url = f"{url}&page={page}"
            response = requests.get(_url, headers=self.headers)
            _repos = [x.get("name") for x in response.json()]
            if not _repos:
                break
            page += 1
            repos.extend(_repos)
        return list(set(repos))

    def create_repo(self, owner: str, repo: str):
        """
        创建代码仓
        :param owner:
        :param repo:
        :return:
        """
        url = f"{self.base_url}/orgs/{owner}/repos"
        body = {
            "name": repo,
        }
        response = requests.post(url, headers=self.headers, json=body)
        if response.status_code not in [200, 201, 204]:
            logging.error(f"create {owner}/{repo} fail...")


if __name__ == '__main__':
    app = GithubApp("")
    # app.get_repos("opengauss-mirror")
    app.create_repo("opengauss-mirror", "test001")
