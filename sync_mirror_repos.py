import time

import yaml
import logging
import subprocess

from src.gitcode_app import GitcodeApp
from src.gitee_app import GiteeApp
from src.github_app import GithubApp

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s: %(message)s")


class SyncMirrorRepos:

    def __init__(self):
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
        self.organizations = config.get("organizations")
        self.gitcode_token = config.get("gitcode_token")
        self.gitee_token = config.get("gitee_token")

        self.gitcode_app = GitcodeApp(access_token=self.gitcode_token)
        self.gitee_app = GiteeApp(access_token=self.gitee_token)

    @staticmethod
    def sync_mirror(origin: str, dis: str, repo: str):
        """
        实施镜像
        :param origin: 源仓组织名
        :param dis: 镜像仓组织名
        :param repo: 代码仓名称
        :return:
        """
        logging.info("=" * 50)

        gitcode_url = f"git@gitcode.com:{origin}/{repo}.git"
        gitee_url = f"git@gitee.com:{dis}/{repo}.git"

        cmd = [f"./tools/sync.sh", gitee_url, gitcode_url, origin, repo]

        try:
            subprocess.run(cmd, timeout=60 * 60, check=True)
        except Exception as err:
            logging.info(f"sync {gitcode_url} fail...")
            logging.error(err)
            return

    def run(self):
        for org in self.organizations:
            _from = org.get("from").strip(" ")
            to = org.get("to").strip(" ")
            _route = org.get("route").strip(" ")
            repos = [x.strip(" ").replace(f"{_from}/", "") for x in org.get("repos")]

            for repo in repos:
                # 同步镜像
                self.sync_mirror(_from, to, repo)


if __name__ == '__main__':
    while True:
        SyncMirrorRepos().run()
        time.sleep(60 * 60 * 4)
