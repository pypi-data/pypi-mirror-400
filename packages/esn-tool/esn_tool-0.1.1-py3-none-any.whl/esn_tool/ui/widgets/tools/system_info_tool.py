"""
系统信息工具

显示系统和环境的基本信息。
"""

import platform
import sys
from pathlib import Path

from rich.table import Table
from textual.widgets import Static

from esn_tool.ui.widgets.tools.tool_base import ToolBase


class SystemInfoTool(ToolBase):
    """系统信息查看器"""

    @property
    def name(self) -> str:
        return "系统信息"

    @property
    def description(self) -> str:
        return "查看系统和 Python 环境信息"

    @property
    def icon(self) -> str:
        return ""

    @property
    def category(self) -> str:
        return "系统"

    def create_widget(self) -> Static:
        """创建显示系统信息的 Widget"""
        # 创建信息表格
        table = Table(title="系统信息", show_header=True, header_style="bold magenta")
        table.add_column("项目", style="cyan", width=20)
        table.add_column("值", style="green")

        # 添加系统信息
        table.add_row("操作系统", platform.system())
        table.add_row("系统版本", platform.version())
        table.add_row("架构", platform.machine())
        table.add_row("处理器", platform.processor() or "未知")
        table.add_row("Python 版本", sys.version.split()[0])
        table.add_row("Python 路径", sys.executable)
        table.add_row("工作目录", str(Path.cwd()))
        table.add_row("用户目录", str(Path.home()))

        # 返回 Static widget 包含 table
        return Static(table, id="system-info")
