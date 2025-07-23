#!/bin/bash

gitcode_url=$1
mirror_url=$2
owner=$3
repo=$4

echo "[${repo}] current dir: $(pwd)"
work_dir="$(pwd)/data/${owner}"

mkdir -p "${work_dir}" && cd "${work_dir}" || exit

# 下载更新代码
if [ -d "${repo}.git" ]; then
  cd "${repo}.git" || exit
  git remote set-url origin "${gitcode_url}"    # 将代码仓远程地址设置成gitcode地址
  echo "[${repo}] git pull --mirror ${gitcode_url}"
  git fetch --all --prune "${gitcode_url}"
else
  echo "[${repo}] git clone --mirror ${gitcode_url}"
  git clone --mirror "${gitcode_url}"
fi

cd "${work_dir}" || exit

# 推送代码
echo "[${repo}] git push ${mirror_url}"
if [ -d "${repo}.git" ]; then
  cd "${repo}.git" || exit
  git remote set-url origin "${mirror_url}"    # 将代码仓远程地址设置成gitcode地址
  git push "${mirror_url}" --prune --force '+refs/heads/*:refs/heads/*' '+refs/tags/*:refs/tags/*'
fi
