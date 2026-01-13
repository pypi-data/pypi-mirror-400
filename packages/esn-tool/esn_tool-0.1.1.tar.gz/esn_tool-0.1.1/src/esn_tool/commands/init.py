"""
Init 命令模块

扫描当前目录下的 Git 仓库，让用户选择要管理的项目。
"""

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

from esn_tool.utils.project_config import (
    get_project_config_dir,
    load_project_config,
    save_project_config,
    find_project_config_dir,
)

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


@click.command(short_help="选择要管理的 Git 项目")
@click.option(
    "-d", "--directory",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    default=".",
    help="指定要扫描的目录，默认为当前目录",
)
@click.option(
    "-s", "--single",
    is_flag=True,
    help="单项目模式，只初始化当前目录（当前目录必须是 Git 仓库）",
)
@click.option(
    "-m", "--multi",
    is_flag=True,
    help="多项目模式，可以选择当前目录和子文件夹中的 Git 仓库",
)
def init(directory: str, single: bool, multi: bool) -> None:
    """选择要管理的 Git 项目
    
    \b
    扫描并选择要管理的 Git 仓库，后续 acm/git 命令只操作选定的项目。
    
    \b
    示例:
        esn init              # 交互式选择模式
        esn init -s           # 单项目模式，直接初始化当前目录
        esn init -m           # 多项目模式，选择当前目录+子文件夹
        esn init -d /path     # 指定目录
    """
    import questionary
    from esn_tool.utils.style import get_style
    
    base_path = Path(directory)
    
    # 检查当前目录本身是否是 Git 仓库
    current_is_git = (base_path / ".git").exists()
    
    # -s 单项目模式：直接初始化当前目录
    if single:
        if not current_is_git:
            console.print(Panel(
                f"当前目录 [cyan]{base_path}[/cyan] 不是 Git 仓库",
                title="❌ 初始化失败",
                title_align="left",
                border_style="red",
            ))
            return
        
        # 直接保存配置
        config = {"projects": ["."]}
        config_file = save_project_config(config, base_path)
        
        console.print(Panel(
            f"已初始化单项目模式\n\n"
            f"[dim]项目目录: {base_path}[/dim]\n"
            f"[dim]配置文件: {config_file}[/dim]",
            title="✅ 初始化完成",
            title_align="left",
            border_style="green",
        ))
        return
    
    # 查找所有 Git 仓库
    git_repos = find_git_repos(base_path)
    
    # -m 多项目模式或默认模式
    if not git_repos and not current_is_git:
        console.print(Panel(
            f"在 [cyan]{base_path}[/cyan] 下未找到任何 Git 仓库",
            title="😕 无可用项目",
            title_align="left",
            border_style="yellow",
        ))
        return
    
    total_repos = len(git_repos) + (1 if current_is_git else 0)
    
    # 显示标题（与 config 统一风格）
    console.print("\n[bold cyan]📋 ESN Tool 项目初始化[/bold cyan]")
    console.print("[dim]使用 ↑↓ 选择项目，空格选中，Enter 确认[/dim]\n")
    
    console.print(f"发现 [bold cyan]{total_repos}[/bold cyan] 个 Git 仓库")
    
    # 检查是否已有配置
    existing_config_dir = find_project_config_dir(base_path)
    existing_projects: list[str] = []
    
    if existing_config_dir:
        existing_config = load_project_config(existing_config_dir)
        existing_projects = existing_config.get("projects", [])
        if existing_projects:
            console.print(f"当前已管理 [bold cyan]{len(existing_projects)}[/bold cyan] 个项目")
    
    console.print()
    
    # 构建选项列表
    choices = []
    
    # 如果当前目录是 Git 仓库，将其作为第一个选项
    if current_is_git:
        is_selected = "." in existing_projects
        choices.append(questionary.Choice(
            title="📁 . (当前目录)",
            value=".",
            checked=is_selected
        ))
    
    for repo in git_repos:
        rel_path = repo.name
        # 如果已在配置中，默认选中
        is_selected = rel_path in existing_projects
        choices.append(questionary.Choice(
            title=f"📁 {rel_path}",
            value=rel_path,
            checked=is_selected
        ))
    
    # 添加分隔符和退出选项
    choices.append(questionary.Separator("─" * 45))
    choices.append(questionary.Choice(
        title="❌ 取消并退出",
        value="__EXIT__",
        checked=False
    ))
    
    # 使用统一样式
    custom_style = get_style()
    
    try:
        selected = questionary.checkbox(
            "选择要管理的项目:",
            choices=choices,
            style=custom_style,
            instruction="(↑↓ 移动, 空格 选择, Enter 确认)",
            pointer="❯",
        ).ask()
    except KeyboardInterrupt:
        console.print("\n[dim]👋 操作已取消[/dim]")
        return
    
    if selected is None:
        console.print("\n[dim]👋 操作已取消[/dim]")
        return
    
    # 检查是否选择了退出
    if "__EXIT__" in selected:
        console.print("\n[dim]👋 操作已取消[/dim]")
        return
    
    if not selected:
        console.print(Panel(
            "请至少选择一个项目进行管理",
            title="⚠️ 未选择项目",
            title_align="left",
            border_style="yellow",
        ))
        return
    
    # 保存配置
    config = {
        "projects": selected,
    }
    
    config_file = save_project_config(config, base_path)
    
    # 成功提示
    success_content = f"已选择 [bold green]{len(selected)}[/bold green] 个项目进行管理\n\n"
    success_content += "[dim]选中的项目:[/dim]\n"
    for proj in selected:
        success_content += f"  [cyan]•[/cyan] {proj}\n"
    success_content += f"\n[dim]配置文件: {config_file}[/dim]"
    
    console.print(Panel(
        success_content,
        title="✅ 初始化完成",
        title_align="left",
        border_style="green",
    ))
    
    console.print("\n[dim]💡 提示: 后续 [cyan]esn acm[/cyan] 和 [cyan]esn git[/cyan] 命令将只操作这些项目[/dim]\n")
