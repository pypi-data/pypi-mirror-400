"""
Git 操作服务

提供 Git 相关的业务逻辑，供 CLI 和 TUI 共同使用。
"""

import subprocess
from pathlib import Path


class GitRepo:
    """Git 仓库信息"""
    
    def __init__(self, path: Path):
        self.path = path
        self.name = path.name
        self._branch = None
        self._status = None
    
    @property
    def branch(self) -> str:
        """获取当前分支"""
        if self._branch is None:
            try:
                result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    cwd=self.path,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                self._branch = result.stdout.strip() or "unknown"
            except Exception:
                self._branch = "error"
        return self._branch
    
    @property
    def status(self) -> str:
        """获取仓库状态"""
        if self._status is None:
            try:
                result = subprocess.run(
                    ["git", "status", "--short"],
                    cwd=self.path,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                output = result.stdout.strip()
                if not output:
                    self._status = "clean"
                else:
                    self._status = "modified"
            except Exception:
                self._status = "error"
        return self._status


def find_git_repos(base_path: Path) -> list[GitRepo]:
    """
    查找指定目录下的所有一级 Git 仓库。
    
    Args:
        base_path: 要搜索的基础目录
        
    Returns:
        Git 仓库列表
    """
    git_repos = []
    
    if not base_path.is_dir():
        return git_repos
    
    for item in base_path.iterdir():
        if item.is_dir() and (item / ".git").exists():
            git_repos.append(GitRepo(item))
    
    return sorted(git_repos, key=lambda r: r.name.lower())


def run_git_command(repo: GitRepo, args: tuple[str, ...]) -> tuple[bool, str]:
    """
    在指定仓库目录执行 git 命令。
    
    Args:
        repo: Git 仓库对象
        args: git 命令参数
        
    Returns:
        (成功与否, 输出/错误信息)
    """
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo.path,
            capture_output=True,
            text=True,
            timeout=60,
        )
        
        output = result.stdout.strip() or result.stderr.strip()
        return result.returncode == 0, output
        
    except subprocess.TimeoutExpired:
        return False, "命令执行超时"
    except Exception as e:
        return False, str(e)
