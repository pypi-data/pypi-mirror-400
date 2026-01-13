"""
Git 批量操作命令模块

遍历当前目录的一级子文件夹，对所有 Git 项目执行指定的 git 命令。
"""

import subprocess
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

console = Console()


def find_git_repos(base_path: Path) -> list[Path]:
    """
    查找指定目录下的所有一级 Git 仓库。
    
    Args:
        base_path: 要搜索的基础目录
        
    Returns:
        包含 .git 目录的子文件夹路径列表
    """
    git_repos = []
    
    if not base_path.is_dir():
        return git_repos
    
    for item in base_path.iterdir():
        if item.is_dir() and (item / ".git").exists():
            git_repos.append(item)
    
    return sorted(git_repos, key=lambda p: p.name.lower())


def run_git_command(repo_path: Path, args: tuple[str, ...]) -> tuple[bool, str]:
    """
    在指定仓库目录执行 git 命令。
    
    Args:
        repo_path: Git 仓库路径
        args: git 命令参数
        
    Returns:
        (成功与否, 输出/错误信息)
    """
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_path,
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


# ============================================================
# Git 命令
# ============================================================

@click.command(
    short_help="批量执行 git 命令",
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
        allow_interspersed_args=False,
    )
)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
@click.option(
    "-d", "--directory",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    default=".",
    help="指定要搜索的目录，默认为当前目录",
)
@click.option(
    "-v", "--verbose",
    is_flag=True,
    help="显示详细输出",
)
def git(args: tuple[str, ...], directory: str, verbose: bool) -> None:
    """批量执行 git 命令
    
    \b
    遍历目录下所有 Git 仓库，执行相同的 git 命令。
    
    \b
    示例:
        esntool git status
        esntool git pull
        esntool git checkout main
    """
    base_path = Path(directory)
    
    # 优先使用项目配置中的仓库列表
    from esn_tool.utils.project_config import get_selected_repos
    selected_repos = get_selected_repos(base_path)
    use_project_config = False
    
    if selected_repos is not None:
        git_repos = selected_repos
        use_project_config = True
    else:
        git_repos = find_git_repos(base_path)
    
    if not git_repos:
        console.print(f"[dim]😕 在 {base_path} 下未找到任何 Git 项目[/dim]")
        return
    
    git_cmd = " ".join(["git", *args])
    
    if use_project_config:
        console.print(f"\n[bold cyan]📁 使用项目配置，共 {len(git_repos)} 个项目[/bold cyan]")
    else:
        console.print(f"\n[bold cyan]📁 发现 {len(git_repos)} 个 Git 项目[/bold cyan]")
    
    console.print(f"[dim]   💻 执行: {git_cmd}[/dim]\n")
    
    # 创建结果表格
    table = Table(show_header=True, header_style="bold")
    table.add_column("项目", style="cyan")
    table.add_column("状态", justify="center")
    table.add_column("信息", style="dim")
    
    success_count = 0
    fail_count = 0
    
    for repo in git_repos:
        repo_name = repo.name
        
        with console.status(f"[dim]正在处理 {repo_name}...[/dim]"):
            success, output = run_git_command(repo, args)
        
        if success:
            success_count += 1
            status = "[green]✓[/green]"
            info = output[:80] + "..." if len(output) > 80 else output
            if not info:
                info = "✓"
        else:
            fail_count += 1
            status = "[red]✗[/red]"
            info = output[:80] + "..." if len(output) > 80 else output
        
        table.add_row(repo_name, status, info)
        
        if verbose and output:
            console.print(f"\n[bold]{repo_name}:[/bold]")
            console.print(output)
            console.print()
    
    console.print(table)
    
    # 总结
    if fail_count == 0:
        console.print(f"\n[green]✨ 全部完成[/green] [dim]({success_count} 个项目)[/dim]\n")
    else:
        console.print(f"\n[bold]完成:[/bold] [green]{success_count} 成功[/green], [red]{fail_count} 失败[/red]\n")
