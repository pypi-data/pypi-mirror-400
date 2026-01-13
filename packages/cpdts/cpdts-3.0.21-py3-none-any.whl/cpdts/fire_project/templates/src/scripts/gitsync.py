"""
Git 同步脚本
============
自动同步本地仓库与远程仓库：
1. 检查远程是否有新提交，有则 pull
2. 检查是否有冲突，有则提示用户手动解决
3. 将工作区更改添加到暂存区
4. 使用当前日期时间作为 commit message 提交
5. 推送到远程仓库
"""

from datetime import datetime

from git import Repo
from git.exc import GitCommandError


def gitsync() -> None:
    """执行 git 同步操作"""
    repo = Repo(search_parent_directories=True)

    # region 检查是否有远程仓库
    if not repo.remotes:
        print("错误: 没有配置远程仓库")
        return

    origin = repo.remotes.origin
    # endregion

    # region 获取远程更新并检查是否需要 pull
    print("正在获取远程更新...")
    origin.fetch()

    local_branch = repo.active_branch
    tracking = local_branch.tracking_branch()

    if not tracking:
        print(f"警告: 分支 '{local_branch.name}' 没有设置追踪分支")
    else:
        behind_commits = list(repo.iter_commits(f"{local_branch.name}..{tracking.name}"))

        if behind_commits:
            print(f"远程领先 {len(behind_commits)} 个提交，正在执行 pull...")
            try:
                origin.pull()
                print("pull 完成")
            except GitCommandError as e:
                if "CONFLICT" in str(e) or "conflict" in str(e).lower():
                    print("错误: 存在合并冲突，请手动解决后再运行此脚本")
                    return
                raise

            # 检查是否有未解决的冲突
            if repo.index.unmerged_blobs():
                print("错误: 存在未解决的合并冲突，请手动解决后再运行此脚本")
                return
    # endregion

    # region 检查是否有需要提交的更改
    has_staged = bool(repo.index.diff("HEAD"))
    has_unstaged = bool(repo.index.diff(None))
    has_untracked = bool(repo.untracked_files)

    if not has_staged and not has_unstaged and not has_untracked:
        print("没有需要提交的更改")
        return
    # endregion

    # region 添加所有更改到暂存区并提交
    print("正在添加更改到暂存区...")
    repo.git.add(A=True)

    commit_message = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"正在提交: {commit_message}")
    repo.index.commit(commit_message)
    # endregion

    # region 推送到远程
    print("正在推送到远程...")
    try:
        origin.push()
        print("同步完成!")
    except GitCommandError as e:
        print(f"推送失败: {e}")
    # endregion


if __name__=="__main__":
    gitsync()