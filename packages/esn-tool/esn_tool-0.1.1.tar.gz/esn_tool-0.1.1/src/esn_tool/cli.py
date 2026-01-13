"""
ESN Tool CLI 入口模块

定义主命令组和子命令的注册。
"""

import click
from rich.console import Console

from esn_tool import __version__
from esn_tool.commands import acm, config, git, gitlab, init, run, tools

console = Console()


CONTEXT_SETTINGS = dict(
    max_content_width=200,  # 帮助信息最大宽度
    help_option_names=["-h", "--help"],
)


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__, prog_name="esn-tool")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """ESN Tool - 项目管理 CLI 工具
    
    一个用于管理生产项目的命令行工具。
    """
    ctx.ensure_object(dict)


# 注册子命令
cli.add_command(init.init)
cli.add_command(git.git)
cli.add_command(acm.acm)
cli.add_command(config.config)
cli.add_command(run.run)
cli.add_command(gitlab.gitlab)
cli.add_command(tools.tools)


if __name__ == "__main__":
    cli()
