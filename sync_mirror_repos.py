import yaml
import logging
import subprocess

from src.gitcode_app import GitcodeApp

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s: %(message)s")


class SyncMirrorRepos:

    def __init__(self):
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
        self.organizations = config.get("organizations")
        self.gitcode_token = config.get("gitcode_token")

        self.gitcode_app = GitcodeApp(access_token=self.gitcode_token)

    @staticmethod
    def sync_mirror(origin: str, dis: str, route: str, repo: str):
        """
        实施镜像
        :param origin: 源仓组织名
        :param dis: 镜像仓组织名
        :param route: 迁移路径（gitcode-to-gitee、 gitcode-to-github）
        :param repo: 代码仓名称
        :return:
        """
        dis_platform = route.split("-")[-1]

        gitcode_url = f"git@gitcode.com:{origin}/{repo}.git"
        gitee_url = f"git@gitee.com:{dis}/{repo}.git"
        github_url = f"git@github.com:{dis}/{repo}.git"

        if dis_platform == "gitee":
            cmd = [f"./tools/sync.sh", gitcode_url, gitee_url, origin, repo]
        else:
            cmd = [f"./tools/sync.sh", gitcode_url, github_url, origin, repo]

        code = subprocess.call(cmd)
        if code != 0:
            logging.info(f"sync {gitcode_url} fail...")
            return

        # 对镜像仓进行锁仓操作
        logging.info(f"lock mirror repo: {dis}/{repo}")
        if dis_platform == "gitee":
            pass
        else:
            pass

    def run(self):
        for org in self.organizations:
            _from = org.get("from").strip(" ")
            to = org.get("to").strip(" ")
            route = org.get("route").strip(" ")
            repos = [x.strip(" ").replace(f"{_from}/", "") for x in org.get("repos")]
            exclude_repos = [x.strip(" ").replace(f"{_from}/", "") for x in org.get("exclude_repos") or []]

            # 获取组织所有代码仓
            if _from in repos:
                repos = self.gitcode_app.get_org_repo(_from)

            # 排除exclude_repos字段中的代码仓
            if exclude_repos:
                repos = list(set(repos) - set(exclude_repos))

            for repo in repos:
                self.sync_mirror(_from, to, route, repo)


if __name__ == '__main__':
    SyncMirrorRepos().run()
