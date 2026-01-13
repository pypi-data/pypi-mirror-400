"""
GitLab 配置管理命令模块

配置 GitLab 项目信息，保存在当前目录的 .esn-tool 目录中。
每个 Git 项目可以有独立的 Project ID 配置。
"""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from esn_tool.utils.project_config import (
    load_project_config,
    save_project_config,
    find_project_config_dir,
    get_project_config_dir,
)

console = Console()


# GitLab 配置文件名
GITLAB_CONFIG_FILE = ".gitlab.json"


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


def load_gitlab_config(base_path: Path) -> dict:
    """
    加载 GitLab 配置。
    
    Args:
        base_path: 基础目录路径
        
    Returns:
        GitLab 配置字典
    """
    import json
    
    config_dir = find_project_config_dir(base_path)
    if not config_dir:
        config_dir = get_project_config_dir(base_path)
    
    config_file = config_dir / GITLAB_CONFIG_FILE
    
    if config_file.exists():
        try:
            return json.loads(config_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    
    return {}


def save_gitlab_config(config: dict, base_path: Path) -> Path:
    """
    保存 GitLab 配置。
    
    Args:
        config: 配置字典
        base_path: 基础目录路径
        
    Returns:
        配置文件路径
    """
    import json
    
    config_dir = get_project_config_dir(base_path)
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config_file = config_dir / GITLAB_CONFIG_FILE
    config_file.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
    
    return config_file


def get_project_id(config: dict, project_name: str) -> str:
    """获取项目的 Project ID"""
    projects = config.get("projects", {})
    return projects.get(project_name, {}).get("project_id", "")


def set_project_id(config: dict, project_name: str, project_id: str | int) -> dict:
    """设置项目的 Project ID"""
    if "projects" not in config:
        config["projects"] = {}
    if project_name not in config["projects"]:
        config["projects"][project_name] = {}
    config["projects"][project_name]["project_id"] = project_id
    return config


# ============================================================
# GitLab 命令组
# ============================================================

@click.group(short_help="GitLab 相关操作")
def gitlab() -> None:
    """GitLab 相关操作
    
    \b
    管理 GitLab 项目配置和 Merge Request 操作。
    
    \b
    示例:
        esntool gitlab config          # 配置 GitLab 信息
        esntool gitlab mr              # 列出所有待审核的 MR
        esntool gitlab mr --cr         # 交互式选择 MR 进行 AI 审查
        esntool gitlab mr --acr        # 自动对所有 MR 进行 AI 审查
        esntool gitlab mr --acr -y     # 自动审查并直接发布评论
    """
    pass


@gitlab.command(name="config", short_help="配置 GitLab 项目信息")
@click.option(
    "-d", "--directory",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    default=".",
    help="指定配置保存的目录，默认为当前目录",
)
def gitlab_config(directory: str) -> None:
    """配置 GitLab 项目信息
    
    \b
    交互式配置 GitLab 的通用设置（URL、Token）和每个项目的 Project ID。
    配置保存在当前目录的 .esn-tool/.gitlab.json 文件中。
    
    \b
    示例:
        esntool gitlab config
        esntool gitlab config -d /path/to/project
    """
    import questionary
    from esn_tool.utils.style import get_style
    
    base_path = Path(directory)
    # 使用统一样式
    custom_style = get_style()
    
    console.print("\n[bold cyan]🦊 GitLab 配置[/bold cyan]")
    console.print("[dim]使用 ↑↓ 选择配置项，回车编辑，Ctrl+C 退出[/dim]\n")
    
    while True:
        # 加载当前配置
        current_config = load_gitlab_config(base_path)
        current_private_token = current_config.get("private_token", "")
        default_gitlab_url = "https://git.yyrd.com"
        current_gitlab_url = current_config.get("gitlab_url", default_gitlab_url)
        
        # 确保 gitlab_url 始终存在于配置中
        if "gitlab_url" not in current_config:
            current_config["gitlab_url"] = default_gitlab_url
            save_gitlab_config(current_config, base_path)
        
        # Private Token 脱敏显示
        if current_private_token:
            masked_token = current_private_token[:6] + "..." + current_private_token[-4:] if len(current_private_token) > 10 else "***"
        else:
            masked_token = "(未设置)"
        
        # 获取 Git 仓库列表（包括当前目录）
        git_repos = find_git_repos(base_path)
        current_is_git = (base_path / ".git").exists()
        
        # 计算已配置数量
        projects_config = current_config.get("projects", {})
        configured_count = sum(1 for repo in git_repos if get_project_id(current_config, repo.name))
        if current_is_git and get_project_id(current_config, "."):
            configured_count += 1
        total_repos = len(git_repos) + (1 if current_is_git else 0)
        
        # 构建选项列表
        choices = [
            f"GitLab URL     : {current_gitlab_url}",
            f"Private Token  : {masked_token}",
            questionary.Separator("─" * 45),
            f"📁 配置项目 ID  : ({configured_count}/{total_repos} 已配置)",
            questionary.Separator("─" * 45),
            "✓ 保存并退出",
        ]
        
        try:
            selected = questionary.select(
                "选择要编辑的配置项:",
                choices=choices,
                style=custom_style,
                instruction="(↑↓ 选择, Enter 编辑)",
            ).ask()
        except KeyboardInterrupt:
            console.print("\n[yellow]已取消[/yellow]")
            return
        
        if selected is None:
            console.print("\n[yellow]已取消[/yellow]")
            return
        
        if "保存并退出" in selected:
            config_file = save_gitlab_config(current_config, base_path)
            
            console.print(Panel(
                f"配置已保存到 [cyan]{config_file}[/cyan]",
                title="✅ 保存成功",
                title_align="left",
                border_style="green",
            ))
            return
        
        # 根据选择编辑对应配置
        if selected.startswith("GitLab URL"):
            try:
                new_value = questionary.text(
                    "请输入 GitLab URL:",
                    default=current_gitlab_url,
                    style=custom_style,
                ).ask()
                if new_value is not None and new_value != current_gitlab_url:
                    current_config["gitlab_url"] = new_value.rstrip("/")
                    save_gitlab_config(current_config, base_path)
                    console.print("[green]✓ GitLab URL 已更新[/green]\n")
            except KeyboardInterrupt:
                pass
                
        elif selected.startswith("Private Token"):
            try:
                new_value = questionary.password(
                    "请输入 Private Token:",
                    style=custom_style,
                ).ask()
                if new_value is not None and new_value != current_private_token:
                    current_config["private_token"] = new_value
                    save_gitlab_config(current_config, base_path)
                    console.print("[green]✓ Private Token 已更新[/green]\n")
            except KeyboardInterrupt:
                pass
        
        elif "配置项目 ID" in selected:
            _configure_project_ids(base_path, current_config, git_repos, custom_style, current_is_git)


def _configure_project_ids(base_path: Path, config: dict, git_repos: list[Path], custom_style, current_is_git: bool = False) -> None:
    """配置各个项目的 Project ID"""
    import questionary
    
    total_repos = len(git_repos) + (1 if current_is_git else 0)
    
    if total_repos == 0:
        console.print(Panel(
            f"在 [cyan]{base_path}[/cyan] 下未找到任何 Git 仓库",
            title="😕 无可用项目",
            title_align="left",
            border_style="yellow",
        ))
        return
    
    console.print(f"\n[bold cyan]📁 配置项目 Project ID[/bold cyan]")
    console.print(f"[dim]发现 {total_repos} 个 Git 项目[/dim]\n")
    
    while True:
        # 构建项目选项列表
        choices = []
        
        # 添加当前目录选项
        if current_is_git:
            project_id = get_project_id(config, ".")
            if project_id:
                choices.append(f". (当前目录)  → {project_id}")
            else:
                choices.append(". (当前目录)  (未设置)")
        
        for repo in git_repos:
            project_id = get_project_id(config, repo.name)
            if project_id:
                choices.append(f"{repo.name}  → {project_id}")
            else:
                choices.append(f"{repo.name}  (未设置)")
        
        choices.append(questionary.Separator("─" * 45))
        choices.append("← 返回上级菜单")
        
        try:
            selected = questionary.select(
                "选择要配置的项目:",
                choices=choices,
                style=custom_style,
                instruction="(↑↓ 选择, Enter 编辑)",
            ).ask()
        except KeyboardInterrupt:
            return
        
        if selected is None or "返回上级菜单" in selected:
            return
        
        # 解析选中的项目名称
        project_name = selected.split("  ")[0].strip()
        # 处理当前目录的特殊情况
        if project_name.startswith(". ("):
            project_name = "."
        current_project_id = get_project_id(config, project_name)
        
        try:
            new_value = questionary.text(
                f"请输入 [{project_name}] 的 Project ID:",
                default=str(current_project_id) if current_project_id else "",
                style=custom_style,
            ).ask()
            
            if new_value is not None:
                # 尝试转换为整数
                try:
                    project_id = int(new_value) if new_value else ""
                except ValueError:
                    project_id = new_value
                
                if project_id != current_project_id:
                    config = set_project_id(config, project_name, project_id)
                    save_gitlab_config(config, base_path)
                    console.print(f"[green]✓ {project_name} 的 Project ID 已更新[/green]\n")
        except KeyboardInterrupt:
            pass


# ============================================================
# GitLab API 调用
# ============================================================

def fetch_merge_requests(gitlab_url: str, private_token: str, project_id: int | str, state: str = "opened") -> list[dict]:
    """
    获取项目的 Merge Request 列表。
    
    Args:
        gitlab_url: GitLab 服务器地址
        private_token: GitLab 私有访问令牌
        project_id: GitLab 项目 ID
        state: MR 状态 (opened, closed, merged, all)
        
    Returns:
        MR 列表
    """
    import httpx
    
    url = f"{gitlab_url}/api/v4/projects/{project_id}/merge_requests"
    headers = {"PRIVATE-TOKEN": private_token}
    params = {
        "state": state,
        "per_page": 100,
    }
    
    try:
        with httpx.Client(timeout=30) as client:
            response = client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError:
        return []


def fetch_mr_details(gitlab_url: str, private_token: str, project_id: int | str, mr_iid: int) -> dict:
    """获取 MR 详细信息，包含 diff_refs"""
    import httpx
    
    url = f"{gitlab_url}/api/v4/projects/{project_id}/merge_requests/{mr_iid}"
    headers = {"PRIVATE-TOKEN": private_token}
    
    try:
        with httpx.Client(timeout=30) as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError:
        return {}


def fetch_mr_diffs(gitlab_url: str, private_token: str, project_id: int | str, mr_iid: int) -> list[dict]:
    """获取 MR 的文件变更列表"""
    import httpx
    
    headers = {"PRIVATE-TOKEN": private_token}
    # 备选方案：使用 changes endpoint
    url = f"{gitlab_url}/api/v4/projects/{project_id}/merge_requests/{mr_iid}/changes"
    
    try:
        with httpx.Client(timeout=60) as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            # changes endpoint 返回 { "changes": [...] }
            if isinstance(data, dict) and "changes" in data:
                return data["changes"]
    except httpx.HTTPError as e:
        console.print(f"[dim]changes API 失败: {e}[/dim]")
    
    return []


def create_mr_discussion(
    gitlab_url: str, 
    private_token: str, 
    project_id: int | str, 
    mr_iid: int,
    body: str,
    position: dict | None = None
) -> dict:
    """
    在 MR 中创建讨论评论。
    
    Args:
        gitlab_url: GitLab 服务器地址
        private_token: GitLab 私有访问令牌
        project_id: GitLab 项目 ID
        mr_iid: MR 的 IID
        body: 评论内容
        position: 可选的位置信息（用于行级评论）
        
    Returns:
        创建的讨论信息
    """
    import httpx
    
    url = f"{gitlab_url}/api/v4/projects/{project_id}/merge_requests/{mr_iid}/discussions"
    headers = {"PRIVATE-TOKEN": private_token}
    data = {"body": body}
    
    if position:
        data["position"] = position
    
    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        console.print(f"[red]创建评论失败: {e}[/red]")
        return {}


def create_mr_note(
    gitlab_url: str, 
    private_token: str, 
    project_id: int | str, 
    mr_iid: int,
    body: str
) -> dict:
    """在 MR 中创建普通评论"""
    import httpx
    
    url = f"{gitlab_url}/api/v4/projects/{project_id}/merge_requests/{mr_iid}/notes"
    headers = {"PRIVATE-TOKEN": private_token}
    data = {"body": body}
    
    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        console.print(f"[red]创建评论失败: {e}[/red]")
        return {}


# 从 services.ai 导入 MR 审核相关函数
from esn_tool.services.ai import (
    parse_diff_with_line_numbers,
    generate_mr_review,
)


def review_single_mr(
    gitlab_url: str,
    private_token: str,
    project_id: int | str,
    mr_iid: int,
    project_name: str,
    mr_title: str,
    auto_publish: bool = False,
) -> bool:
    """
    对单个 MR 执行 AI 代码审查。
    
    Args:
        gitlab_url: GitLab 服务器地址
        private_token: GitLab 私有访问令牌
        project_id: GitLab 项目 ID
        mr_iid: MR 的 IID
        project_name: 项目名称（仅用于显示）
        mr_title: MR 标题（仅用于显示）
        auto_publish: 是否自动发布评论（不询问确认）
        
    Returns:
        是否成功完成审查
    """
    import questionary
    
    console.print(f"\n[bold cyan]📋 {mr_title}[/bold cyan]")
    console.print(f"[dim]项目: {project_name} | MR: !{mr_iid}[/dim]\n")
    
    # 获取 MR 详情（包含 diff_refs）
    with console.status("[dim]正在获取 MR 信息...[/dim]"):
        mr_details = fetch_mr_details(gitlab_url, private_token, project_id, mr_iid)
    
    if not mr_details:
        console.print("[red]无法获取 MR 详情[/red]")
        return False
    
    diff_refs = mr_details.get("diff_refs", {})
    base_sha = diff_refs.get("base_sha", "")
    head_sha = diff_refs.get("head_sha", "")
    start_sha = diff_refs.get("start_sha", "")
    
    # 获取 MR diff
    with console.status("[dim]正在获取代码变更...[/dim]"):
        diffs = fetch_mr_diffs(gitlab_url, private_token, project_id, mr_iid)
    
    if not diffs:
        console.print("[yellow]无法获取 MR 的代码变更，跳过[/yellow]")
        return False
    
    # 构建文件路径映射
    file_paths = {}
    for diff in diffs:
        old_path = diff.get("old_path", "")
        new_path = diff.get("new_path", "")
        file_paths[new_path] = {"old_path": old_path, "new_path": new_path}
    
    # 构建带行号注释的 diff 内容
    diff_content = ""
    for diff in diffs:
        file_path = diff.get("new_path", diff.get("old_path", ""))
        diff_text = diff.get("diff", "")
        if diff_text:
            annotated_diff = parse_diff_with_line_numbers(diff_text, file_path)
            diff_content += annotated_diff + "\n\n"
    
    console.print(f"[dim]📄 共 {len(diffs)} 个文件变更[/dim]\n")
    
    # 调用 AI 进行审查
    with console.status("[bold cyan]🤖 AI 正在审查代码...[/bold cyan]"):
        review_comments = generate_mr_review(diff_content)
    
    if not review_comments:
        # 发布审查通过的评论
        pass_comment = "✅ **代码审查完成，未发现需要关注的问题！**\n\n---\n*🤖 AI 代码审查*"
        with console.status("[dim]正在发布审查结果...[/dim]"):
            create_mr_note(gitlab_url, private_token, project_id, mr_iid, pass_comment)
        
        console.print(Panel(
            "✅ 代码审查完成，未发现需要关注的问题！",
            title="🎉 审查通过",
            title_align="left",
            border_style="green",
        ))
        return True
    
    # 显示审查结果
    console.print(f"[bold yellow]📝 发现 {len(review_comments)} 个建议[/bold yellow]\n")
    
    for i, comment in enumerate(review_comments, 1):
        file_path = comment.get("file", "")
        content = comment.get("content", "")
        old_line = comment.get("old_line")
        new_line = comment.get("new_line")
        
        line_info = ""
        if new_line:
            line_info = f":L{new_line}"
        elif old_line:
            line_info = f":L{old_line}(旧)"
        
        console.print(f"[bold cyan]#{i}[/bold cyan] [dim]{file_path}{line_info}[/dim]")
        console.print(f"   {content}")
        console.print()
    
    # 确认是否发布评论
    if not auto_publish:
        try:
            confirm = questionary.confirm(
                "是否将以上审查建议发布到 GitLab？",
                default=False,
            ).ask()
            
            if not confirm:
                console.print("[dim]👋 已取消发布[/dim]\n")
                return True
        except KeyboardInterrupt:
            console.print("\n[dim]👋 已取消[/dim]")
            return False
    
    # 发布评论到 GitLab
    console.print()
    success_count = 0
    
    for comment in review_comments:
        file_path = comment.get("file", "")
        content = comment.get("content", "")
        old_line = comment.get("old_line")
        new_line = comment.get("new_line")
        
        file_info = file_paths.get(file_path, {"old_path": file_path, "new_path": file_path})
        full_comment = f"{content}\n\n---\n*🤖 AI 代码审查*"
        
        result = None
        
        # 尝试创建行级评论
        if (old_line or new_line) and base_sha and head_sha and start_sha:
            position = {
                "base_sha": base_sha,
                "start_sha": start_sha,
                "head_sha": head_sha,
                "position_type": "text",
                "old_path": file_info["old_path"],
                "new_path": file_info["new_path"],
            }
            
            if new_line:
                position["new_line"] = new_line
            if old_line:
                position["old_line"] = old_line
            
            with console.status(f"[dim]正在发布行级评论...[/dim]"):
                result = create_mr_discussion(
                    gitlab_url, private_token, project_id, mr_iid,
                    full_comment, position
                )
        
        # Fallback: 普通评论
        if not result:
            fallback_comment = f"**📁 {file_path}**"
            if new_line:
                fallback_comment += f" (行 {new_line})"
            elif old_line:
                fallback_comment += f" (旧行 {old_line})"
            fallback_comment += f"\n\n{content}\n\n---\n*🤖 AI 代码审查*"
            
            with console.status(f"[dim]正在发布评论...[/dim]"):
                result = create_mr_note(gitlab_url, private_token, project_id, mr_iid, fallback_comment)
        
        if result:
            success_count += 1
            line_info = f" @ 行 {new_line or old_line}" if (new_line or old_line) else ""
            console.print(f"[green]✓[/green] 已发布: {file_path}{line_info}")
        else:
            console.print(f"[red]✗[/red] 发布失败: {file_path}")
    
    console.print()
    if success_count == len(review_comments):
        console.print(f"[green]✓[/green] MR !{mr_iid} 审查完成，发布 {success_count} 条建议")
    else:
        console.print(f"[yellow]⚠[/yellow] MR !{mr_iid} 部分发布: {success_count}/{len(review_comments)}")
    
    return True


@gitlab.command(name="mr", short_help="列出待审核的 Merge Request")
@click.option(
    "-d", "--directory",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    default=".",
    help="指定项目目录，默认为当前目录",
)
@click.option(
    "-s", "--state",
    type=click.Choice(["opened", "closed", "merged", "all"]),
    default="opened",
    help="MR 状态筛选，默认为 opened（待审核）",
)
@click.option(
    "--cr",
    is_flag=True,
    help="Code Review，交互式选择 MR 进行 AI 审查",
)
@click.option(
    "--acr",
    is_flag=True,
    help="Auto Code Review，自动对所有 MR 进行 AI 审查",
)
@click.option(
    "-y", "--yes",
    is_flag=True,
    help="跳过确认直接发布评论",
)
def gitlab_mr(directory: str, state: str, cr: bool, acr: bool, yes: bool) -> None:
    """列出待审核的 Merge Request
    
    \b
    查询所有已配置项目的 Merge Request 并以表格形式展示。
    
    \b
    示例:
        esntool gitlab mr              # 列出所有待审核的 MR
        esntool gitlab mr -s merged    # 列出已合并的 MR
        esntool gitlab mr --cr         # 交互式选择 MR 进行 AI 审查
        esntool gitlab mr --acr        # 自动对所有 MR 进行 AI 审查
        esntool gitlab mr --acr -y     # 自动审查并直接发布评论
    """
    base_path = Path(directory)
    
    # 加载配置
    config = load_gitlab_config(base_path)
    gitlab_url = config.get("gitlab_url", "")
    private_token = config.get("private_token", "")
    projects_config = config.get("projects", {})
    
    # 验证配置
    if not gitlab_url or not private_token:
        console.print(Panel(
            "请先运行 [cyan]esntool gitlab config[/cyan] 配置 GitLab URL 和 Private Token",
            title="⚠️ 配置缺失",
            title_align="left",
            border_style="yellow",
        ))
        return
    
    # 获取已配置 Project ID 的项目
    configured_projects = {
        name: info.get("project_id")
        for name, info in projects_config.items()
        if info.get("project_id")
    }
    
    if not configured_projects:
        console.print(Panel(
            "请先运行 [cyan]esntool gitlab config[/cyan] 配置项目的 Project ID",
            title="⚠️ 未配置项目",
            title_align="left",
            border_style="yellow",
        ))
        return
    
    # --cr 模式：交互式代码审查
    if cr:
        run_gitlab_review(base_path, gitlab_url, private_token, configured_projects, yes)
        return
    
    # 普通模式（可能带 --acr）
    run_gitlab_mr_impl(base_path, gitlab_url, private_token, configured_projects, state, acr, yes)


def run_gitlab_mr_impl(
    base_path: Path,
    gitlab_url: str,
    private_token: str,
    configured_projects: dict,
    state: str,
    acr: bool,
    yes: bool,
) -> None:
    """列出待审核的 Merge Request 或执行批量 AI 审查"""
    
    state_labels = {
        "opened": "待审核",
        "closed": "已关闭",
        "merged": "已合并",
        "all": "全部",
    }
    
    console.print(f"\n[bold cyan]🦊 GitLab Merge Requests ({state_labels.get(state, state)})[/bold cyan]")
    console.print(f"[dim]正在查询 {len(configured_projects)} 个项目...[/dim]\n")
    
    # 收集所有 MR
    all_mrs = []
    
    for project_name, project_id in configured_projects.items():
        with console.status(f"[dim]正在获取 {project_name} 的 MR...[/dim]"):
            mrs = fetch_merge_requests(gitlab_url, private_token, project_id, state)
        
        if not mrs:
            continue
        
        for mr in mrs:
            all_mrs.append({
                "project_name": project_name,
                "project_id": project_id,
                "iid": mr.get("iid"),
                "title": mr.get("title", ""),
                "author": mr.get("author", {}).get("name", ""),
                "source_branch": mr.get("source_branch", ""),
                "target_branch": mr.get("target_branch", ""),
                "state": mr.get("state", ""),
                "web_url": mr.get("web_url", ""),
            })
    
    if not all_mrs:
        console.print(f"[dim]😊 没有找到{state_labels.get(state, state)}的 Merge Request[/dim]\n")
        return
    
    # 如果没有 --acr 选项，显示 MR 列表
    if not acr:
        # 按项目分组显示
        from itertools import groupby
        
        all_mrs_sorted = sorted(all_mrs, key=lambda x: x["project_name"])
        
        for project_name, mrs_group in groupby(all_mrs_sorted, key=lambda x: x["project_name"]):
            mrs_list = list(mrs_group)
            
            table = Table(
                title=f"📁 {project_name}",
                title_style="bold cyan",
                show_header=True,
                header_style="bold",
            )
            table.add_column("IID", style="cyan", justify="right", width=6)
            table.add_column("标题", style="white", max_width=45)
            table.add_column("作者", style="green", width=12)
            table.add_column("分支", style="yellow", max_width=25)
            table.add_column("状态", justify="center", width=8)
            table.add_column("链接", style="dim", no_wrap=True)
            
            for mr in mrs_list:
                iid = str(mr["iid"])
                title = mr["title"][:43] + "..." if len(mr["title"]) > 43 else mr["title"]
                author = mr["author"][:10]
                branch_info = f"{mr['source_branch']} → {mr['target_branch']}"
                if len(branch_info) > 23:
                    branch_info = branch_info[:23] + "..."
                
                mr_state = mr["state"]
                if mr_state == "opened":
                    state_display = "[green]待审核[/green]"
                elif mr_state == "merged":
                    state_display = "[blue]已合并[/blue]"
                elif mr_state == "closed":
                    state_display = "[red]已关闭[/red]"
                else:
                    state_display = mr_state
                
                table.add_row(iid, title, author, branch_info, state_display, mr["web_url"])
            
            console.print(table)
            console.print()
        
        console.print(f"[bold]共计:[/bold] [cyan]{len(all_mrs)}[/cyan] 个 Merge Request\n")
        return
    
    # --acr 模式：对所有 MR 进行自动代码审查
    console.print(Panel(
        f"即将对 [cyan]{len(all_mrs)}[/cyan] 个 MR 进行 AI 代码审查",
        title="🤖 自动代码审查",
        title_align="left",
        border_style="cyan",
    ))
    
    reviewed_count = 0
    
    for i, mr in enumerate(all_mrs, 1):
        console.print(f"\n[bold]━━━ [{i}/{len(all_mrs)}] ━━━[/bold]")
        
        try:
            success = review_single_mr(
                gitlab_url=gitlab_url,
                private_token=private_token,
                project_id=mr["project_id"],
                mr_iid=mr["iid"],
                project_name=mr["project_name"],
                mr_title=mr["title"],
                auto_publish=yes,
            )
            if success:
                reviewed_count += 1
        except KeyboardInterrupt:
            console.print("\n[dim]👋 用户中断，停止审查[/dim]")
            break
        except Exception as e:
            console.print(f"[red]审查失败: {e}[/red]")
    
    console.print(f"\n[bold]🎉 自动代码审查完成: [green]{reviewed_count}[/green]/{len(all_mrs)} 个 MR[/bold]\n")


def run_gitlab_review(
    base_path: Path,
    gitlab_url: str,
    private_token: str,
    configured_projects: dict,
    yes: bool,
) -> None:
    """交互式 AI 代码审查"""
    import questionary
    from esn_tool.utils.style import get_style
    from rich.markdown import Markdown
    
    # 使用统一样式
    custom_style = get_style()
    
    console.print(f"\n[bold cyan]🤖 AI 代码审查[/bold cyan]")
    console.print(f"[dim]正在获取待审核的 MR...[/dim]\n")
    
    # 收集所有项目的 opened MR
    all_mrs = []
    
    for project_name, project_id in configured_projects.items():
        with console.status(f"[dim]正在获取 {project_name} 的 MR...[/dim]"):
            mrs = fetch_merge_requests(gitlab_url, private_token, project_id, "opened")
        
        for mr in mrs:
            all_mrs.append({
                "project_name": project_name,
                "project_id": project_id,
                "iid": mr.get("iid"),
                "title": mr.get("title", ""),
                "author": mr.get("author", {}).get("name", ""),
                "web_url": mr.get("web_url", ""),
            })
    
    if not all_mrs:
        console.print(Panel(
            "没有找到待审核的 Merge Request",
            title="😊 暂无 MR",
            title_align="left",
            border_style="green",
        ))
        return
    
    console.print(f"[dim]发现 {len(all_mrs)} 个待审核的 MR[/dim]\n")
    
    # 构建选择列表
    choices = []
    for mr in all_mrs:
        title = mr["title"][:40] + "..." if len(mr["title"]) > 40 else mr["title"]
        label = f"!{mr['iid']} {title}  [{mr['project_name']}] @{mr['author']}"
        choices.append(questionary.Choice(title=label, value=mr))
    
    # 让用户选择 MR
    try:
        selected_mr = questionary.select(
            "选择要审查的 MR:",
            choices=choices,
            style=custom_style,
            instruction="(↑↓ 选择, Enter 确认)",
        ).ask()
    except KeyboardInterrupt:
        console.print("\n[dim]👋 已取消[/dim]")
        return
    
    if selected_mr is None:
        console.print("[dim]👋 已取消[/dim]")
        return
    
    project_name = selected_mr["project_name"]
    project_id = selected_mr["project_id"]
    mr_iid = selected_mr["iid"]
    
    console.print(f"\n[bold cyan]📋 {selected_mr['title']}[/bold cyan]")
    console.print(f"[dim]{selected_mr['web_url']}[/dim]\n")
    
    # 获取 MR 详情（包含 diff_refs）
    with console.status("[dim]正在获取 MR 信息...[/dim]"):
        mr_details = fetch_mr_details(gitlab_url, private_token, project_id, mr_iid)
    
    diff_refs = mr_details.get("diff_refs", {})
    base_sha = diff_refs.get("base_sha", "")
    head_sha = diff_refs.get("head_sha", "")
    start_sha = diff_refs.get("start_sha", "")
    
    # 获取 MR diff
    with console.status("[dim]正在获取代码变更...[/dim]"):
        diffs = fetch_mr_diffs(gitlab_url, private_token, project_id, mr_iid)
    
    if not diffs:
        console.print(Panel(
            "无法获取 MR 的代码变更",
            title="❌ 获取失败",
            title_align="left",
            border_style="red",
        ))
        return
    
    # 构建文件路径映射（用于后续创建行级评论）
    file_paths = {}
    for diff in diffs:
        old_path = diff.get("old_path", "")
        new_path = diff.get("new_path", "")
        file_paths[new_path] = {
            "old_path": old_path,
            "new_path": new_path,
        }
    
    # 构建完整的 diff 内容（使用带行号注释的格式）
    diff_content = ""
    for diff in diffs:
        file_path = diff.get("new_path", diff.get("old_path", ""))
        diff_text = diff.get("diff", "")
        if diff_text:
            # 使用带行号注释的解析函数
            annotated_diff = parse_diff_with_line_numbers(diff_text, file_path)
            diff_content += annotated_diff + "\n\n"
    
    console.print(f"[dim]📄 共 {len(diffs)} 个文件变更[/dim]\n")
    
    # 调用 AI 进行审查
    with console.status("[bold cyan]🤖 AI 正在审查代码...[/bold cyan]"):
        review_comments = generate_mr_review(diff_content)
    
    if not review_comments:
        console.print(Panel(
            "✅ 代码审查完成，未发现需要关注的问题！",
            title="🎉 审查通过",
            title_align="left",
            border_style="green",
        ))
        return
    
    # 显示审查结果
    console.print(f"[bold yellow]📝 发现 {len(review_comments)} 个建议[/bold yellow]\n")
    
    for i, comment in enumerate(review_comments, 1):
        file_path = comment.get("file", "")
        content = comment.get("content", "")
        old_line = comment.get("old_line")
        new_line = comment.get("new_line")
        
        # 构建行号显示
        line_info = ""
        if new_line:
            line_info = f":L{new_line}"
        elif old_line:
            line_info = f":L{old_line}(旧)"
        
        console.print(f"[bold cyan]#{i}[/bold cyan] [dim]{file_path}{line_info}[/dim]")
        console.print(f"   {content}")
        console.print()
    
    # 确认是否发布评论
    if not yes:
        try:
            confirm = questionary.confirm(
                "是否将以上审查建议发布到 GitLab？",
                default=False,
            ).ask()
            
            if not confirm:
                console.print("[dim]👋 已取消发布[/dim]\n")
                return
        except KeyboardInterrupt:
            console.print("\n[dim]👋 已取消[/dim]")
            return
    
    # 发布评论到 GitLab
    console.print()
    success_count = 0
    
    for comment in review_comments:
        file_path = comment.get("file", "")
        content = comment.get("content", "")
        old_line = comment.get("old_line")
        new_line = comment.get("new_line")
        
        # 获取文件路径信息
        file_info = file_paths.get(file_path, {"old_path": file_path, "new_path": file_path})
        
        # 构建评论内容
        full_comment = f"{content}\n\n---\n*🤖 AI 代码审查*"
        
        result = None
        
        # 如果有行号信息且有 diff_refs，尝试创建行级评论
        if (old_line or new_line) and base_sha and head_sha and start_sha:
            position = {
                "base_sha": base_sha,
                "start_sha": start_sha,
                "head_sha": head_sha,
                "position_type": "text",
                "old_path": file_info["old_path"],
                "new_path": file_info["new_path"],
            }
            
            # 设置行号
            if new_line:
                position["new_line"] = new_line
            if old_line:
                position["old_line"] = old_line
            
            with console.status(f"[dim]正在发布行级评论...[/dim]"):
                result = create_mr_discussion(
                    gitlab_url, private_token, project_id, mr_iid, 
                    full_comment, position
                )
        
        # Fallback: 如果行级评论失败或没有行号，创建普通评论
        if not result:
            fallback_comment = f"**📁 {file_path}**"
            if new_line:
                fallback_comment += f" (行 {new_line})"
            elif old_line:
                fallback_comment += f" (旧行 {old_line})"
            fallback_comment += f"\n\n{content}\n\n---\n*🤖 AI 代码审查*"
            
            with console.status(f"[dim]正在发布评论...[/dim]"):
                result = create_mr_note(gitlab_url, private_token, project_id, mr_iid, fallback_comment)
        
        if result:
            success_count += 1
            line_info = f" @ 行 {new_line or old_line}" if (new_line or old_line) else ""
            console.print(f"[green]✓[/green] 已发布: {file_path}{line_info}")
        else:
            console.print(f"[red]✗[/red] 发布失败: {file_path}")
    
    console.print()
    if success_count == len(review_comments):
        console.print(Panel(
            f"成功发布 [green]{success_count}[/green] 条审查建议到 MR !{mr_iid}",
            title="✅ 发布完成",
            title_align="left",
            border_style="green",
        ))
    else:
        console.print(Panel(
            f"发布完成: [green]{success_count}[/green] 成功, [red]{len(review_comments) - success_count}[/red] 失败",
            title="⚠️ 部分发布",
            title_align="left",
            border_style="yellow",
        ))
