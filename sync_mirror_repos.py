import yaml
import logging
import subprocess

from src.gitcode_app import GitcodeApp
from src.gitee_app import GiteeApp

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

    def sync_mirror(self, origin: str, dis: str, route: str, repo: str):
        """
        实施镜像
        :param origin: 源仓组织名
        :param dis: 镜像仓组织名
        :param route: 迁移路径（gitcode-to-gitee、 gitcode-to-github）
        :param repo: 代码仓名称
        :return:
        """
        logging.info("=" * 50)
        to_platform = route.split("-")[-1]

        gitcode_url = f"git@gitcode.com:{origin}/{repo}.git"
        gitee_url = f"git@gitee.com:{dis}/{repo}.git"
        github_url = f"git@github.com:{dis}/{repo}.git"

        if to_platform == "gitee":
            cmd = [f"./tools/sync.sh", gitcode_url, gitee_url, origin, repo]
        else:
            cmd = [f"./tools/sync.sh", gitcode_url, github_url, origin, repo]

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
            route = org.get("route").strip(" ")
            repos = [x.strip(" ").replace(f"{_from}/", "") for x in org.get("repos")]
            exclude_repos = [x.strip(" ").replace(f"{_from}/", "") for x in org.get("exclude_repos") or []]

            # 获取源组织所有代码仓
            if _from in repos:
                repos = self.gitcode_app.get_org_repo(_from)

            # 排除exclude_repos字段中的代码仓
            if exclude_repos:
                repos = list(set(repos) - set(exclude_repos))

            # 获取待同步组织代码仓
            to_platform = route.split("-")[-1]
            if to_platform == "gitee":
                to_repos = self.gitee_app.get_repos(to)
                to_repos = [x.split("/")[1] for x in to_repos if x.startswith(f"{to}/")]
            else:
                to_repos = []

            for repo in repos:

                # 待同步组织代码仓不存在就创建
                if repo not in to_repos and to_platform == "gitee":
                    logging.info(f"repo {to}/{repo} not exist, create it...")
                    self.gitee_app.create_repo(to, repo)
                elif repo not in to_repos and to_platform == "github":
                    pass

                # 同步镜像
                self.sync_mirror(_from, to, route, repo)

                # 对镜像仓进行锁仓操作
                # logging.info(f"lock mirror repo: {to}/{repo}")
                if to_platform == "gitee":
                    pass
                else:
                    pass


if __name__ == '__main__':
    SyncMirrorRepos().run()
