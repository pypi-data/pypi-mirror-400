"""
工具内容区域组件

右侧内容区，显示当前选中工具的界面。
"""

from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Static

from esn_tool.ui.widgets.tools.tool_base import ToolBase


class ToolContent(Container):
    """工具内容显示区域"""

    def __init__(self) -> None:
        super().__init__()
        self.current_tool: ToolBase | None = None

    def compose(self) -> ComposeResult:
        """组合 UI 元素"""
        # 使用 VerticalScroll 容器支持滚动
        with VerticalScroll(id="tool-content-scroll"):
            yield Static(self._get_welcome_text(), id="tool-content-main")

    def _get_welcome_text(self) -> str:
        """获取欢迎文本"""
        return """
[bold cyan]欢迎使用 ESN 工具集合[/]

👈 请从左侧选择一个工具开始使用

[dim]提示：
  • 使用 ↑/↓ 键导航工具列表
  • 使用 Enter 键选择工具
  • 按 Q 或 Esc 退出应用[/]
        """

    async def load_tool(self, tool: ToolBase) -> None:
        """加载并显示工具界面
        
        Args:
            tool: 要加载的工具实例
        """
        self.current_tool = tool

        # 获取内容容器
        content_scroll = self.query_one("#tool-content-scroll", VerticalScroll)
        
        # 移除所有现有的子组件
        await content_scroll.remove_children()

        # 创建新的工具 widget
        tool_widget = tool.create_widget()
        tool_widget.border_title = f"{tool.icon} {tool.name}"

        # 添加到容器
        await content_scroll.mount(tool_widget)
        content_scroll.scroll_home(animate=False)
