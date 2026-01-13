"""
工具集合 TUI 应用

主应用界面，管理左右分栏布局和工具切换。
"""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Footer
from textual.css.query import NoMatches

from esn_tool.ui.widgets.tool_content import ToolContent
from esn_tool.ui.widgets.tool_list import ToolList
from esn_tool.ui.widgets.tools.tool_registry import registry
from esn_tool.ui.widgets.tools.system_info_tool import SystemInfoTool
from esn_tool.ui.widgets.tools.config_tool import ConfigTool
from esn_tool.ui.widgets.tools.git_tool import GitTool


class ToolsApp(App):
    """ESN 工具集合应用"""

    CSS = """
    Screen {
        background: $surface;
    }

    #main-container {
        width: 100%;
        height: 100%;
    }

    ToolList {
        width: 35;
        height: 100%;
        border: solid $primary;
        background: $panel;
        padding: 0;
    }

    .tool-list-header {
        width: 100%;
        height: auto;
        padding: 1;
        text-align: center;
        background: $primary;
        color: $text;
        text-style: bold;
        margin: 0;
    }

    #tool-list-view {
        width: 100%;
        height: 1fr;
        border: none;
        padding: 0;
        margin: 0;
        overflow-y: auto;
        scrollbar-size-vertical: 0;
    }

    ListView {
        width: 100%;
        background: $panel;
        border: none !important;
        padding: 0;
        margin: 0;
        overflow-y: auto;
        scrollbar-size-vertical: 0;
    }

    ListView:focus {
        border: none !important;
    }

    ListItem {
        width: 100%;
        padding: 1 2;
        height: auto;
    }

    ListItem > Static {
        width: 100%;
        height: auto;
    }

    ListItem:hover {
        background: $primary-darken-1;
    }

    #login-button {
        width: 1fr;
        margin: 1 2 1 2;
        min-height: 3;
    }

    ToolContent {
        width: 1fr;
        height: 100%;
        border: solid $primary;
        background: $surface;
    }

    #tool-content-scroll {
        width: 100%;
        height: 100%;
        padding: 1 2;
    }

    #tool-content-main {
        width: 100%;
        height: auto;
        padding: 2;
    }
    
    /* 配置工具样式 */
    .widget-title {
        width: 100%;
        padding: 1 0;
        text-align: left;
        margin-bottom: 1;
    }
    
    .config-form {
        width: 100%;
        max-width: 100%;
        height: 100%;
        padding: 2;
    }
    
    .config-form Label {
        margin-top: 1;
        margin-bottom: 0;
    }
    
    .config-form Input {
        width: 100%;
        max-width: 100%;
        margin-bottom: 1;
    }
    
    .config-form Button {
        margin-top: 2;
        width: 20;
    }
    
    #config-status {
        margin-top: 1;
        min-height: 1;
    }
    
    .section-title {
        margin-top: 2;
        margin-bottom: 1;
    }
    
    #project-info {
        padding: 1;
        border: solid $primary-darken-1;
        background: $panel-darken-1;
        margin-bottom: 1;
    }
    
    #project-table {
        height: 15;
        margin-bottom: 1;
    }
    
    #project-status {
        margin-top: 1;
        min-height: 1;
    }
    
    /* Git 工具样式 */
    .git-container {
        width: 100%;
        height: 100%;
        padding: 2;
    }
    
    .git-container Label {
        margin-top: 1;
        margin-bottom: 0;
    }
    
    #repo-table {
        height: 15;
        margin-bottom: 1;
    }
    
    .command-bar {
        height: auto;
        width: 100%;
        align: left middle;
        margin-bottom: 1;
    }
    
    .command-bar Label {
        width: auto;
        margin-right: 1;
    }
    
    .command-bar Input {
        width: 1fr;
        margin-right: 1;
    }
    
    .command-bar Button {
        width: auto;
    }
    
    #result-table {
        height: 1fr;
    }
    """

    TITLE = "ESN 工具集合"
    BINDINGS = [
        Binding("q", "quit", "退出", priority=True),
        Binding("left", "focus_list", "列表", priority=True),
        Binding("right", "focus_content", "内容", priority=True),
    ]

    def __init__(self):
        super().__init__()
        self._register_builtin_tools()

    def _register_builtin_tools(self) -> None:
        """注册内置工具"""
        # 注册系统信息工具
        registry.register(SystemInfoTool())
        
        # 注册配置管理工具
        registry.register(ConfigTool())
        
        # 注册 Git 批量操作工具
        registry.register(GitTool())

        # 这里可以继续注册其他内置工具
        # registry.register(OtherTool())

    def compose(self) -> ComposeResult:
        """组合应用界面"""
        tools = registry.get_all()

        if not tools:
            # 如果没有工具，显示提示信息
            from textual.widgets import Static

            yield Static(
                "[bold red]错误：没有可用的工具[/]\n\n"
                "请检查工具注册是否正确。",
                id="error-message",
            )
            return

        # 左右分栏布局
        with Horizontal(id="main-container"):
            yield ToolList(tools)
            yield ToolContent()
        
        # 页脚显示快捷键
        yield Footer()

    def on_tool_list_tool_selected(self, message: ToolList.ToolSelected) -> None:
        """处理工具选择事件
        
        Args:
            message: 工具选择消息
        """
        try:
            content_area = self.query_one(ToolContent)
            self.call_later(content_area.load_tool, message.tool)
        except NoMatches:
            pass

    def action_quit(self) -> None:
        """退出应用"""
        self.exit()

    def action_focus_list(self) -> None:
        """聚焦到工具列表"""
        try:
            list_view = self.query_one("#tool-list-view")
            list_view.focus()
        except NoMatches:
            pass

    def action_focus_content(self) -> None:
        """聚焦到内容区域"""
        try:
            content_scroll = self.query_one("#tool-content-scroll")
            # 如果内容区域有可聚焦的子组件，优先聚焦第一个
            focusable = content_scroll.query("Input, Button, DataTable").first(None)
            if focusable:
                focusable.focus()
            else:
                content_scroll.focus()
        except NoMatches:
            pass
    
    def on_key(self, event) -> None:
        """处理全局按键事件"""
        # 获取当前焦点的 widget
        focused = self.focused
        
        if focused and event.key == "left":
            # 如果当前焦点在右侧内容区域
            try:
                content_scroll = self.query_one("#tool-content-scroll")
                # 检查焦点是否在内容区域内
                if focused == content_scroll or content_scroll in focused.ancestors:
                    # 如果是 Input 等可编辑组件，检查光标位置
                    if hasattr(focused, 'cursor_position') and hasattr(focused, 'value'):
                        # 如果光标不在最左边，让组件自己处理左键
                        if focused.cursor_position > 0:
                            return
                    
                    # 否则切换到工具列表
                    self.action_focus_list()
                    event.prevent_default()
                    event.stop()
            except NoMatches:
                pass
