"""
配置管理工具

提供 TUI 界面管理 esn-tool 配置和项目选择。
"""

from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Button, DataTable, Input, Label, Static

from esn_tool.ui.widgets.tools.tool_base import ToolBase
from esn_tool.utils.config import get_config_value, set_config_value


class ConfigWidget(Container):
    """配置管理界面组件"""
    
    can_focus = True

    def compose(self) -> ComposeResult:
        """组合 UI 元素"""
        yield Static("[bold cyan]配置管理[/]", classes="widget-title")
        
        with VerticalScroll(classes="config-form"):
            # AI 配置部分
            yield Static("[bold]AI 接口配置[/]", classes="section-title")
            
            # API Key
            yield Label("API Key:")
            yield Input(
                value=get_config_value("ai.api_key", ""),
                password=True,
                placeholder="请输入 API Key",
                id="api-key-input",
            )
            
            # Base URL
            yield Label("Base URL:")
            yield Input(
                value=get_config_value("ai.base_url", "https://api.siliconflow.cn/v1"),
                placeholder="API 接口地址",
                id="base-url-input",
            )
            
            # Model
            yield Label("Model:")
            yield Input(
                value=get_config_value("ai.model", "Qwen/Qwen2.5-7B-Instruct"),
                placeholder="AI 模型名称",
                id="model-input",
            )
            
            # 保存按钮
            yield Button("保存 AI 配置", variant="primary", id="save-config-btn")
            
            # 状态信息
            yield Static("", id="config-status")
            
            # 项目管理部分
            yield Static("[bold]项目管理[/]", classes="section-title")
            yield Label("选择要管理的 Git 项目 (点击行切换选择):")
            yield DataTable(id="project-table", cursor_type="row")
            yield Button("保存项目选择", variant="success", id="save-projects-btn")
            yield Static("", id="project-status")
    
    def on_mount(self) -> None:
        """组件挂载时初始化"""
        self._load_projects()
    
    def _load_projects(self) -> None:
        """加载 Git 项目列表"""
        from esn_tool.services.git_service import find_git_repos, GitRepo
        from esn_tool.utils.project_config import load_project_config, find_project_config_dir
        
        # 获取当前目录下的所有 Git 仓库
        base_path = Path.cwd()
        repos = find_git_repos(base_path)
        
        # 检查当前目录是否也是 Git 仓库
        if (base_path / ".git").exists():
            repos.insert(0, GitRepo(base_path))
        
        table = self.query_one("#project-table", DataTable)
        
        if not repos:
            table.add_column("提示")
            table.add_row("未找到任何 Git 仓库")
            return
        
        # 加载已选中的项目
        config_dir = find_project_config_dir()
        selected_projects = set()
        if config_dir:
            config = load_project_config(config_dir)
            selected_projects = set(config.get("projects", []))
        
        # 初始化表格
        table.add_columns("选择", "项目名称", "路径")
        table.zebra_stripes = True
        
        # 存储仓库列表和行键映射
        self.repos = repos
        self.selected_rows = set()
        self.row_keys = {}  # 存储行索引到 row_key 的映射
        
        # 添加数据行
        for idx, repo in enumerate(repos):
            rel_path = "." if repo.path == base_path else repo.name
            is_selected = rel_path in selected_projects
            
            if is_selected:
                self.selected_rows.add(idx)
            
            check_mark = "[✓]" if is_selected else "[ ]"
            row_key = table.add_row(check_mark, repo.name, str(repo.path))
            self.row_keys[idx] = row_key  # 保存行键
    
    def _refresh_project_table(self) -> None:
        """刷新项目表格显示"""
        table = self.query_one("#project-table", DataTable)
        
        # 保存当前光标位置
        current_row = table.cursor_row
        
        # 清空表格
        table.clear()
        
        # 重新添加行
        self.row_keys = {}
        for idx, repo in enumerate(self.repos):
            check_mark = "[✓]" if idx in self.selected_rows else "[ ]"
            row_key = table.add_row(check_mark, repo.name, str(repo.path))
            self.row_keys[idx] = row_key
        
        # 恢复光标位置
        if current_row < len(self.repos):
            table.move_cursor(row=current_row)
    
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """处理表格行选择，切换选中状态"""
        row_index = event.cursor_row
        
        # 切换选中状态
        if row_index in self.selected_rows:
            self.selected_rows.remove(row_index)
        else:
            self.selected_rows.add(row_index)
        
        # 重新加载表格以反映更改
        self._refresh_project_table()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击事件"""
        if event.button.id == "save-config-btn":
            self._save_config()
        elif event.button.id == "save-projects-btn":
            self._save_projects()

    def _save_config(self) -> None:
        """保存 AI 配置"""
        api_key = self.query_one("#api-key-input", Input).value
        base_url = self.query_one("#base-url-input", Input).value
        model = self.query_one("#model-input", Input).value
        
        set_config_value("ai.api_key", api_key)
        set_config_value("ai.base_url", base_url)
        set_config_value("ai.model", model)
        
        status = self.query_one("#config-status", Static)
        status.update("[green]✓ AI 配置已保存[/green]")
    
    def _save_projects(self) -> None:
        """保存项目选择"""
        from esn_tool.utils.project_config import save_project_config
        
        if not hasattr(self, 'repos') or not self.repos:
            return
        
        base_path = Path.cwd()
        selected_projects = []
        
        for idx in sorted(self.selected_rows):
            if idx < len(self.repos):
                repo = self.repos[idx]
                rel_path = "." if repo.path == base_path else repo.name
                selected_projects.append(rel_path)
        
        if not selected_projects:
            status = self.query_one("#project-status", Static)
            status.update("[yellow]⚠ 请至少选择一个项目[/yellow]")
            return
        
        config = {"projects": selected_projects}
        save_project_config(config, base_path)
        
        status = self.query_one("#project-status", Static)
        status.update(f"[green]✓ 已保存 {len(selected_projects)} 个项目[/green]")
    
    
    def on_key(self, event) -> None:
        """处理键盘事件"""
        current_focused = self.app.focused
        
        # 如果焦点在 DataTable 上，让表格自己处理上下键
        if isinstance(current_focused, DataTable):
            return
        
        focusables = list(self.query("Input, Button, DataTable").results())
        
        if not focusables:
            return
        
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


class ConfigTool(ToolBase):
    """配置管理工具"""

    @property
    def name(self) -> str:
        return "配置管理"

    @property
    def description(self) -> str:
        return "管理 AI 接口配置和项目选择"

    @property
    def icon(self) -> str:
        return ""

    @property
    def category(self) -> str:
        return "系统"

    def create_widget(self) -> ConfigWidget:
        """创建配置管理界面"""
        return ConfigWidget()
