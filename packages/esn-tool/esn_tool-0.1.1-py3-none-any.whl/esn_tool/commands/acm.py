"""
ACM (Auto Commit Message) 命令模块

使用 AI 自动生成 Git 提交信息。
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme

# 自定义主题，让 markdown heading 左对齐
CUSTOM_THEME = Theme({
    "markdown.h1": "bold blue",
    "markdown.h2": "bold cyan",
    "markdown.h3": "bold",
    "markdown.h4": "bold dim",
})

console = Console(theme=CUSTOM_THEME)


def render_markdown(text: str) -> Markdown:
    """渲染 Markdown，使用左对齐的 heading"""
    return Markdown(text, justify="left")


def find_git_repos(base_path: Path) -> list[Path]:
    """查找指定目录下的所有一级 Git 仓库"""
    git_repos = []
    if not base_path.is_dir():
        return git_repos
    for item in base_path.iterdir():
        if item.is_dir() and (item / ".git").exists():
            git_repos.append(item)
    return sorted(git_repos, key=lambda p: p.name.lower())


def run_git_command(repo_path: Path, args: tuple[str, ...]) -> tuple[bool, str]:
    """在指定仓库目录执行 git 命令"""
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


def get_git_diff(repo_path: Path, staged: bool = True) -> str:
    """获取 Git diff 内容"""
    args = ["diff", "--cached"] if staged else ["diff"]
    success, output = run_git_command(repo_path, tuple(args))
    return output if success else ""


def get_file_diff(repo_path: Path, file_path: str) -> str:
    """获取单个文件的 diff 内容"""
    # 同时尝试 staged 和 unstaged 的 diff
    # 使用 HEAD 作为参考
    success, output = run_git_command(repo_path, ("diff", "HEAD", "--", file_path))
    if success and output:
        return output
    
    # 尝试获取 staged 的 diff
    success, output = run_git_command(repo_path, ("diff", "--cached", "--", file_path))
    if success and output:
        return output
    
    # 再尝试获取 unstaged 的 diff
    success, output = run_git_command(repo_path, ("diff", "--", file_path))
    if success and output:
        return output
    
    # 对于新文件（未跟踪），显示文件内容
    full_path = repo_path / file_path
    if full_path.exists():
        try:
            content = full_path.read_text(encoding="utf-8", errors="replace")
            lines = content.split("\n")
            # 格式化为类似 diff 的输出
            diff_lines = [f"+++ {file_path}", f"@@ -0,0 +1,{len(lines)} @@"]
            diff_lines.extend(f"+{line}" for line in lines[:100])
            if len(lines) > 100:
                diff_lines.append(f"... 还有 {len(lines) - 100} 行 ...")
            return "\n".join(diff_lines)
        except Exception:
            pass
    
    return f"无法获取 {file_path} 的 diff 内容"


def get_status_files_with_diff(repo_path: Path) -> list[tuple[str, str, str]]:
    """
    获取仓库中带状态标识的文件列表和 diff 内容。
    
    Returns:
        [(状态标识, 文件路径, diff内容), ...] 
        状态标识: +=新增, M=修改, -=删除, ?=未跟踪
    """
    files = []
    
    # 使用 git status --porcelain 获取状态
    success, output = run_git_command(repo_path, ("status", "--porcelain"))
    if success and output:
        for line in output.strip().split("\n"):
            if not line:
                continue
            
            # 直接使用 split 方式解析，更可靠
            parts = line.split(None, 1)  # 按空白分割，最多分割一次
            if len(parts) == 2:
                status_raw = parts[0]
                file_path = parts[1]
            elif len(parts) == 1:
                # 未跟踪文件等特殊情况
                status_raw = line[:2]
                file_path = line[3:] if len(line) > 3 else ""
            else:
                continue
            
            # 转换状态标识
            if "A" in status_raw:
                status_char = "+"  # 新增
            elif "M" in status_raw:
                status_char = "M"  # 修改
            elif "D" in status_raw:
                status_char = "-"  # 删除
            elif status_raw.strip() == "??":
                status_char = "?"  # 未跟踪
            elif "R" in status_raw:
                status_char = "R"  # 重命名
            else:
                status_char = status_raw.strip()[0] if status_raw.strip() else "?"
            
            # 获取该文件的 diff 内容
            diff_content = get_file_diff(repo_path, file_path)
            
            files.append((status_char, file_path, diff_content))
    
    return files


def get_status_files(repo_path: Path) -> list[tuple[str, str]]:
    """
    获取仓库中带状态标识的文件列表。
    
    Returns:
        [(状态标识, 文件路径), ...] 
        状态标识: +=新增, M=修改, -=删除, ?=未跟踪
    """
    files = []
    
    # 使用 git status --porcelain 获取状态
    success, output = run_git_command(repo_path, ("status", "--porcelain"))
    if success and output:
        for line in output.strip().split("\n"):
            if not line:
                continue
            
            if len(line) >= 3:
                # 使用 split 方式更可靠
                parts = line.split(None, 1)  # 按空白分割，最多分割一次
                if len(parts) == 2:
                    status_raw = parts[0]
                    file_path = parts[1]
                elif len(parts) == 1:
                    # 可能是未跟踪文件
                    status_raw = line[:2]
                    file_path = line[3:] if len(line) > 3 else ""
                else:
                    continue
                
                # 转换状态标识
                if "A" in status_raw:
                    status_char = "+"  # 新增
                elif "M" in status_raw:
                    status_char = "M"  # 修改
                elif "D" in status_raw:
                    status_char = "-"  # 删除
                elif status_raw.strip() == "??":
                    status_char = "?"  # 未跟踪
                elif "R" in status_raw:
                    status_char = "R"  # 重命名
                else:
                    status_char = status_raw.strip()[0] if status_raw.strip() else "?"
                
                files.append((status_char, file_path))
    
    return files


def has_changes(repo_path: Path) -> tuple[bool, bool, list[str]]:
    """检查仓库是否有更改"""
    staged_success, staged_output = run_git_command(repo_path, ("diff", "--cached", "--name-only"))
    has_staged = staged_success and bool(staged_output.strip())
    
    unstaged_success, unstaged_output = run_git_command(repo_path, ("diff", "--name-only"))
    has_unstaged = unstaged_success and bool(unstaged_output.strip())
    
    success, output = run_git_command(repo_path, ("ls-files", "--others", "--exclude-standard"))
    untracked = output.strip().split("\n") if success and output else []
    
    return has_staged, has_unstaged, untracked


@click.command(short_help="AI 生成 Git 提交信息")
@click.option(
    "-d", "--directory",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    default=".",
    help="指定要搜索的目录，默认为当前目录",
)
@click.option(
    "-m", "--model",
    default=None,
    help="指定 AI 模型",
)
@click.option(
    "-a", "--auto-stage",
    is_flag=True,
    help="自动暂存所有更改后再生成提交信息",
)
@click.option(
    "-y", "--yes",
    is_flag=True,
    help="跳过确认直接提交",
)
@click.option(
    "-r/-R", "--review/--no-review",
    default=True,
    help="启用/禁用 AI 代码审查（默认启用）",
)
@click.option(
    "-s", "--split",
    is_flag=True,
    help="分离模式：每个项目单独生成提交信息",
)
def acm(directory: str, model: str | None, auto_stage: bool, yes: bool, review: bool, split: bool) -> None:
    """AI 生成 Git 提交信息
    
    \b
    检测 Git 项目的待提交文件，调用 AI 生成符合 Conventional Commits 规范的提交信息。
    
    \b
    示例:
        esntool acm
        esntool acm -a    # 自动暂存
        esntool acm -y    # 跳过确认
        esntool acm -s    # 分离模式
    """
    from esn_tool.services.ai import AIClient, generate_commit_message, generate_code_review
    from esn_tool.utils.project_config import get_selected_repos
    
    base_path = Path(directory)
    
    # 优先使用项目配置中的仓库列表
    selected_repos = get_selected_repos(base_path)
    use_project_config = False
    
    if selected_repos is not None:
        git_repos = selected_repos
        use_project_config = True
    else:
        git_repos = find_git_repos(base_path)
    
    if not git_repos:
        console.print(Panel(
            f"在 [cyan]{base_path}[/cyan] 下未找到任何 Git 仓库",
            title="😕 无可用项目",
            title_align="left",
            border_style="yellow",
        ))
        return
    
    try:
        client = AIClient(model=model) if model else AIClient()
    except ValueError as e:
        console.print(Panel(
            f"{e}\n\n[dim]💡 运行 [cyan]esntool config[/cyan] 配置 API Key[/dim]",
            title="❌ 配置错误",
            title_align="left",
            border_style="red",
        ))
        return
    
    if use_project_config:
        console.print(f"\n[bold cyan]� 使用项目配置，共 {len(git_repos)} 个项目[/bold cyan]")
    else:
        console.print(f"\n[bold cyan]� 发现 {len(git_repos)} 个 Git 项目[/bold cyan]")
    console.print(f"[dim]   🤖 模型: {client.model}[/dim]\n")
    
    # 检查每个仓库的更改
    repos_with_changes: list[tuple[Path, str]] = []
    
    for repo in git_repos:
        has_staged, has_unstaged, untracked = has_changes(repo)
        
        if not has_staged and not has_unstaged and not untracked:
            continue
        
        # 如果需要自动暂存
        if auto_stage and (has_unstaged or untracked):
            run_git_command(repo, ("add", "-A"))
            has_staged = True
        
        # 获取 diff
        if has_staged:
            diff = get_git_diff(repo, staged=True)
        elif has_unstaged:
            diff = get_git_diff(repo, staged=False)
        else:
            continue
        
        if diff:
            repos_with_changes.append((repo, diff))
    
    if not repos_with_changes:
        console.print(Panel(
            "所有项目均无待提交的更改",
            title="✨ 工作区干净",
            title_align="left",
            border_style="green",
        ))
        return
    
    # 收集所有项目的文件到一个列表
    all_files: list[tuple[str, str, str, str, str]] = []  # (status, file_path, diff_content, repo_name, repo_path)
    
    for repo, diff in repos_with_changes:
        files_with_diff = get_status_files_with_diff(repo)
        for status, file_path, diff_content in files_with_diff:
            all_files.append((status, file_path, diff_content, repo.name, str(repo)))
    
    if not all_files:
        console.print("[dim]👋 没有可提交的文件[/dim]")
        return
    
    # 如果指定了 -y 选项，直接使用所有文件
    if yes:
        selected_files = all_files
    else:
        # 显示交互式文件选择器（统一选择所有项目的文件）
        try:
            from esn_tool.ui.file_selector import select_files_interactive
            title = f"选择要提交的文件 ({len(repos_with_changes)} 个项目)"
            selected_files = select_files_interactive(all_files, title)
        except Exception as e:
            console.print(f"[yellow]交互式选择器加载失败，使用全部文件: {e}[/yellow]")
            selected_files = all_files
    
    if not selected_files:
        console.print("\n[dim]👋 未选择任何文件，操作已取消[/dim]")
        return
    
    console.print(f"\n[bold]✅ 已选中 {len(selected_files)} 个文件[/bold]")
    
    # 按项目分组
    from collections import defaultdict
    files_by_repo: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for status, file_path, diff_content, repo_name, repo_path in selected_files:
        files_by_repo[repo_path].append((status, file_path, diff_content))
    
    # 构建所有选中文件的 diff 内容
    all_selected_diff = "\n\n".join(
        f"文件: {file_path}\n{diff_content}"
        for status, file_path, diff_content, repo_name, repo_path in selected_files
    )
    
    # 如果启用了代码审查，且是合并模式，先审查再确认生成提交信息
    if review and not split:
        # 第一步：代码审查
        with console.status("[dim]正在进行代码审查...[/dim]"):
            try:
                review_result = generate_code_review(all_selected_diff, client)
            except Exception as e:
                console.print(f"[yellow]⚠️ 代码审查失败: {e}[/yellow]")
                review_result = None
        
        # 显示代码审查结果
        while True:
            if review_result:
                review_lines = review_result.strip().split("\n")
                if len(review_lines) > 60:
                    console.print("\n[bold blue]📝 AI 代码审查建议[/bold blue] [dim](内容较长，按 q 退出查看)[/dim]")
                    with console.pager(styles=True):
                        console.print(Panel(render_markdown(review_result.strip()), title="📝 AI 代码审查建议", title_align="left", border_style="blue"))
                else:
                    console.print("\n[bold blue]📝 AI 代码审查建议:[/bold blue]")
                    console.print(Panel(render_markdown(review_result.strip()), title="📝 AI 代码审查建议", title_align="left", border_style="blue"))
            else:
                console.print("\n[dim]未发现需要关注的代码问题[/dim]")
            
            # 询问下一步操作
            if yes:
                break  # -y 模式直接继续
            
            import questionary
            from esn_tool.utils.style import get_style
            
            custom_style = get_style()
            
            try:
                action = questionary.select(
                    "请选择下一步操作:",
                    choices=[
                        "✅ 继续生成提交信息",
                        "🔄 重新审查 (修改代码后)",
                        "❌ 取消",
                    ],
                    style=custom_style,
                ).ask()
            except KeyboardInterrupt:
                action = None
            
            if action is None or "取消" in action:
                console.print("\n[dim]👋 操作已取消[/dim]")
                return
            
            if "重新审查" in action:
                # 提示用户修改代码
                console.print("\n[dim]💡 请修改代码后按 Enter 继续重新审查...[/dim]")
                input()
                
                # 重新获取选中文件的 diff
                console.print("[dim]正在重新扫描变更...[/dim]")
                new_diff_parts = []
                for status, file_path, _, repo_name, repo_path in selected_files:
                    repo = Path(repo_path)
                    # 重新获取该文件的 diff
                    new_diff = get_file_diff(repo, file_path)
                    if new_diff:
                        new_diff_parts.append(f"文件: {file_path}\n{new_diff}")
                
                if not new_diff_parts:
                    console.print("[yellow]⚠️ 没有发现变更，可能代码未修改[/yellow]")
                    continue
                
                all_selected_diff = "\n\n".join(new_diff_parts)
                
                with console.status("[dim]正在重新进行代码审查...[/dim]"):
                    try:
                        review_result = generate_code_review(all_selected_diff, client)
                    except Exception as e:
                        console.print(f"[yellow]⚠️ 代码审查失败: {e}[/yellow]")
                        review_result = None
                continue  # 循环回去显示新的审查结果
            
            # 继续生成提交信息
            break
        
        with console.status("[dim]🤖 正在生成提交信息...[/dim]"):
            try:
                commit_msg = generate_commit_message(all_selected_diff, client)
            except Exception as e:
                console.print(f"[red]❌ 生成提交信息失败: {e}[/red]")
                return
        
        console.print(f"\n[bold cyan]📦 合并提交到 {len(files_by_repo)} 个项目[/bold cyan]")
        console.print(Panel(commit_msg.strip(), title="📝 生成的提交信息", title_align="left", border_style="green"))
        
        # 显示将提交到的项目列表
        console.print("\n[dim]将提交到以下项目:[/dim]")
        for repo_path in files_by_repo.keys():
            repo = Path(repo_path)
            console.print(f"  [cyan]•[/cyan] {repo.name}")
        
        if yes or click.confirm("\n✅ 确认提交到所有项目?", default=True):
            for repo_path, repo_files in files_by_repo.items():
                repo = Path(repo_path)
                
                # 只暂存选中的文件
                for status, file_path, _ in repo_files:
                    run_git_command(repo, ("add", "--", file_path))
                
                # 提交
                success, output = run_git_command(repo, ("commit", "-m", commit_msg.strip()))
                
                if success:
                    console.print(f"   [green]✓[/green] {repo.name}")
                else:
                    console.print(f"   [red]✗[/red] {repo.name}: {output}")
        else:
            console.print("\n[dim]👋 操作已取消[/dim]")
    elif split:
        # 分离模式：每个项目分别生成代码审查和提交信息
        for repo_path, repo_files in files_by_repo.items():
            repo = Path(repo_path)
            repo_diff = "\n\n".join(
                f"文件: {file_path}\n{diff_content}"
                for status, file_path, diff_content in repo_files
            )
            
            console.print(f"\n[bold cyan]📦 {repo.name}[/bold cyan] ({len(repo_files)} 个文件)")
            
            # 分离模式：每个项目也先审查再确认生成
            if review:
                # 第一步：代码审查
                with console.status("[dim]正在进行代码审查...[/dim]"):
                    try:
                        review_result = generate_code_review(repo_diff, client)
                    except Exception as e:
                        console.print(f"[yellow]⚠ 代码审查失败: {e}[/yellow]")
                        review_result = None
                
                if review_result:
                    review_lines = review_result.strip().split("\n")
                    if len(review_lines) > 20:
                        console.print("[bold blue]📝 AI 代码审查建议[/bold blue] [dim](按 q 退出)[/dim]")
                        with console.pager(styles=True):
                            console.print(Panel(render_markdown(review_result.strip()), title="📝 AI 代码审查建议", title_align="left", border_style="blue"))
                    else:
                        console.print("[bold blue]📝 AI 代码审查建议:[/bold blue]")
                        console.print(Panel(render_markdown(review_result.strip()), title="📝 AI 代码审查建议", title_align="left", border_style="blue"))
                
                # 第二步：询问是否继续
                if not yes and not click.confirm("\n是否继续生成提交信息?", default=True):
                    console.print("[yellow]已跳过[/yellow]")
                    continue
            
            # 第三步：生成提交信息
            with console.status("[dim]正在生成提交信息...[/dim]"):
                try:
                    commit_msg = generate_commit_message(repo_diff, client)
                except Exception as e:
                    console.print(f"[red]✗ 生成失败: {e}[/red]")
                    continue
            
            # 显示生成的提交信息
            console.print("[bold green]生成的提交信息:[/bold green]")
            console.print(Panel(commit_msg.strip(), border_style="green"))
            
            # 确认并提交
            if yes or click.confirm("是否使用此提交信息提交?", default=True):
                # 只暂存选中的文件
                for status, file_path, _ in repo_files:
                    run_git_command(repo, ("add", "--", file_path))
                
                # 提交
                success, output = run_git_command(repo, ("commit", "-m", commit_msg.strip()))
                
                if success:
                    console.print(f"[green]✓ 提交成功[/green]")
                else:
                    console.print(f"[red]✗ 提交失败: {output}[/red]")
            else:
                console.print("[yellow]已跳过[/yellow]")
    else:
        # 合并模式但不需要代码审查
        console.print(f"\n[bold cyan]📦 合并提交到 {len(files_by_repo)} 个项目[/bold cyan]")
        
        with console.status("[dim]正在生成提交信息...[/dim]"):
            try:
                commit_msg = generate_commit_message(all_selected_diff, client)
            except Exception as e:
                console.print(f"[red]✗ 生成失败: {e}[/red]")
                return
        
        console.print("[bold green]生成的提交信息:[/bold green]")
        console.print(Panel(commit_msg.strip(), border_style="green"))
        
        console.print("\n[dim]将提交到以下项目:[/dim]")
        for repo_path in files_by_repo.keys():
            repo = Path(repo_path)
            console.print(f"  • {repo.name}")
        
        if yes or click.confirm("\n是否使用此提交信息提交到所有项目?", default=True):
            for repo_path, repo_files in files_by_repo.items():
                repo = Path(repo_path)
                
                for status, file_path, _ in repo_files:
                    run_git_command(repo, ("add", "--", file_path))
                
                success, output = run_git_command(repo, ("commit", "-m", commit_msg.strip()))
                
                if success:
                    console.print(f"[green]✓ {repo.name} 提交成功[/green]")
                else:
                    console.print(f"[red]✗ {repo.name} 提交失败: {output}[/red]")
        else:
            console.print("[yellow]已取消[/yellow]")
