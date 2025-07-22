import logging
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s: %(message)s")
ROLE_CONFIG = {}


class GitcodeApp:

    def __init__(self, access_token: str):
        self.access_token = access_token

        self.base_url = "https://api.gitcode.com/api/v5"

    def get_org_repo(self, owner):
        url = f"{self.base_url}/orgs/{owner}/repos?access_token={self.access_token}&per_page=100"
        repos = []
        page = 1

        while True:
            _url = f"{url}&page={page}"

            response = requests.get(_url)
            total_page = response.headers.get("total_page")
            [repos.append(x.get("name")) for x in response.json()]

            page += 1
            if int(total_page) < page:
                break

        return list(set(repos))
