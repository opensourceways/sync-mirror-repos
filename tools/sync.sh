#!/bin/bash

gitcode_url=$1
mirror_url=$2
owner=$3
repo=$4

work_dir="./data/${owner}"

mkdir -p "${work_dir}" && cd "${work_dir}" || exit

# 下载更新代码
echo "git clone/pull --mirror ${gitcode_url}"
if [ -d "${repo}.git" ]; then
  cd "${repo}.git" || exit
  git remote set-url origin "${gitcode_url}"    # 将代码仓远程地址设置成gitcode地址
  git pull --mirror "${gitcode_url}"
else
  git clone --mirror "${gitcode_url}"
fi


# 推送代码
echo "git push --mirror ${mirror_url}"
if [ -d "${repo}.git" ]; then
  cd "${repo}.git" || exit
  git remote set-url origin "${mirror_url}"    # 将代码仓远程地址设置成gitcode地址
  git push "${mirror_url} --prune --force '+refs/heads/*:refs/heads/*' '+refs/tags/*:refs/tags/*"
fi
