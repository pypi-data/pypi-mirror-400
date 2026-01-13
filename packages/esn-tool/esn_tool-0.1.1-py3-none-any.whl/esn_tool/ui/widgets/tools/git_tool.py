"""
Git 批量操作工具

提供 TUI 界面批量执行 Git 命令。
"""

from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, DataTable, Input, Label, Static

from esn_tool.services.git_service import GitRepo, find_git_repos, run_git_command
from esn_tool.ui.widgets.tools.tool_base import ToolBase


class GitWidget(Container):
    """Git 批量操作界面组件"""
    
    can_focus = True

    def __init__(self):
        super().__init__()
        self.repos: list[GitRepo] = []
        self.selected_repos: set[int] = set()

    def compose(self) -> ComposeResult:
        """组合 UI 元素"""
        yield Static("[bold cyan]Git 批量操作[/]", classes="widget-title")
        
        with Vertical(classes="git-container"):
            # 仓库列表
            yield Label("仓库列表:")
            yield DataTable(id="repo-table", cursor_type="row")
            
            # 命令输入区
            with Horizontal(classes="command-bar"):
                yield Label("命令:")
                yield Input(
                    placeholder="例如: pull, status, checkout main",
                    id="git-command-input",
                )
                yield Button("执行", variant="primary", id="exec-git-btn")
            
            # 结果显示区
            yield Label("执行结果:")
            yield DataTable(id="result-table")

    def on_mount(self) -> None:
        """组件挂载时初始化"""
        # 初始化仓库表格
        repo_table = self.query_one("#repo-table", DataTable)
        repo_table.add_columns("仓库", "分支", "状态")
        repo_table.zebra_stripes = True
        
        # 初始化结果表格
        result_table = self.query_one("#result-table", DataTable)
        result_table.add_columns("仓库", "状态", "输出")
        result_table.zebra_stripes = True
        
        # 加载仓库
        self._load_repos()

    def _load_repos(self) -> None:
        """加载 Git 仓库"""
        base_path = Path.cwd()
        self.repos = find_git_repos(base_path)
        
        repo_table = self.query_one("#repo-table", DataTable)
        repo_table.clear()
        
        for repo in self.repos:
            repo_table.add_row(
                repo.name,
                repo.branch,
                repo.status,
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击事件"""
        if event.button.id == "exec-git-btn":
            self._execute_git_command()

    def _execute_git_command(self) -> None:
        """执行 Git 命令"""
        command_input = self.query_one("#git-command-input", Input)
        command = command_input.value.strip()
        
        if not command:
            return
        
        # 解析命令参数
        args = tuple(command.split())
        
        # 清空结果表格
        result_table = self.query_one("#result-table", DataTable)
        result_table.clear()
        
        # 执行命令
        for repo in self.repos:
            success, output = run_git_command(repo, args)
            
            status = "✓" if success else "✗"
            # 截断输出
            short_output = output[:60] + "..." if len(output) > 60 else output
            
            result_table.add_row(
                repo.name,
                status,
                short_output,
            )

    def on_key(self, event) -> None:
        """处理键盘事件"""
        focusables = list(self.query("Input, Button").results())
        
        if not focusables:
            return
        
        current_focused = self.app.focused
        
        if event.key == "down":
            try:
                current_index = focusables.index(current_focused)
                next_index = (current_index + 1) % len(focusables)
                focusables[next_index].focus()
                event.prevent_default()
            except ValueError:
                focusables[0].focus()
                event.prevent_default()
        
        elif event.key == "up":
            try:
                current_index = focusables.index(current_focused)
                prev_index = (current_index - 1) % len(focusables)
                focusables[prev_index].focus()
                event.prevent_default()
            except ValueError:
                focusables[-1].focus()
                event.prevent_default()


class GitTool(ToolBase):
    """Git 批量操作工具"""

    @property
    def name(self) -> str:
        return "Git 操作"

    @property
    def description(self) -> str:
        return "批量执行 Git 命令"

    @property
    def icon(self) -> str:
        return ""

    @property
    def category(self) -> str:
        return "开发"

    def create_widget(self) -> GitWidget:
        """创建 Git 操作界面"""
        return GitWidget()
