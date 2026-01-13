"""
Tools 命令

启动工具集合页面的命令入口。
"""

import click

from esn_tool.ui.tools_app import ToolsApp


@click.command()
def tools() -> None:
    """🛠️  启动工具集合页面
    
    打开一个交互式的工具集合界面，提供各种实用工具。
    
    快捷键：
      ↑/↓    - 导航工具列表
      Enter  - 选择工具
      Q/Esc  - 退出应用
    """
    app = ToolsApp()
    app.run()
