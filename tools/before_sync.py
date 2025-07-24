import requests
import logging
from src.gitee_app import GiteeApp

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s: %(message)s")

ACCESS_TOKEN = "***"
OWNER = "opengauss"


def main():
    app = GiteeApp(access_token=ACCESS_TOKEN)
    repos = [x.split("/")[1] for x in app.get_repos(OWNER) if x.startswith(f"{OWNER}/")]
    for repo in repos:
        branches = app.get_branches(OWNER, repo)
        for branch in branches:
            app.delete_branch_rule(OWNER, repo, branch)


if __name__ == '__main__':
    main()
