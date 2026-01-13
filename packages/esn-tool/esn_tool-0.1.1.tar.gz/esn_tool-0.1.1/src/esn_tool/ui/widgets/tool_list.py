"""
工具列表组件

左侧边栏，显示所有可用工具的列表。
"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.message import Message
from textual.widgets import Button, ListItem, ListView, Rule, Static

from esn_tool.ui.widgets.tools.tool_base import ToolBase


class ToolListItem(ListItem):
    """工具列表项"""

    def __init__(self, tool: ToolBase) -> None:
        super().__init__()
        self.tool = tool

    def compose(self) -> ComposeResult:
        """组合工具列表项的内容"""
        yield Static(f"{self.tool.icon}  {self.tool.name}")


class ToolList(Vertical):
    """工具列表侧边栏"""

    class ToolSelected(Message):
        """工具被选中的消息"""

        def __init__(self, tool: ToolBase) -> None:
            super().__init__()
            self.tool = tool

    def __init__(self, tools: list[ToolBase]) -> None:
        super().__init__()
        self.tools = tools

    def compose(self) -> ComposeResult:
        """组合 UI 元素"""
        # 标题
        yield Static("工具列表", classes="tool-list-header")
        
        # 分割线
        yield Rule()

        # 工具列表
        with ListView(id="tool-list-view"):
            for tool in self.tools:
                yield ToolListItem(tool)
        
        # 登录按钮
        yield Button("登录", id="login-button")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """处理列表项选择事件"""
        if isinstance(event.item, ToolListItem):
            self.post_message(self.ToolSelected(event.item.tool))
    
    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        """处理列表项高亮事件（上下键导航时触发）"""
        if isinstance(event.item, ToolListItem):
            self.post_message(self.ToolSelected(event.item.tool))
