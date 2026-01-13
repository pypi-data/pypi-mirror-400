"""
Run 命令模块

提供快捷运行项目的命令，如 Android 构建等。
"""

import subprocess
from pathlib import Path

import click
from rich.console import Console

console = Console()


@click.group(short_help="快捷运行项目 (如 Android 构建)")
def run() -> None:
    """快捷运行项目 (如 Android 构建)"""
    pass


@run.command()
@click.option(
    "-r", "--release",
    is_flag=True,
    help="构建并安装 Release 版本",
)
@click.option(
    "-d", "--debug",
    is_flag=True,
    help="构建并安装 Debug 版本",
)
def android(release: bool, debug: bool) -> None:
    """
    \b
    构建并安装 Android 应用
    
    \b
    示例:
        esntool run android -r     # installEsnRelease
        esntool run android -d     # installEsnDebug
        esntool run android -rd    # installEsnReleaseDebug
    """
    ckesn_path = Path("ckesn")
    if not ckesn_path.exists():
        console.print("[dim]😕 未找到 ckesn 目录[/dim]")
        console.print("[dim]   💡 请在包含 ckesn 目录的位置运行此命令[/dim]")
        return
    
    # 确定 Gradle 任务
    if release and debug:
        task = "installEsnReleaseDebug"
    elif release:
        task = "installEsnRelease"
    elif debug:
        task = "installEsnDebug"
    else:
        # 交互式选择构建类型
        import questionary
        from esn_tool.utils.style import get_style
        
        custom_style = get_style()
        
        try:
            choice = questionary.select(
                "请选择构建类型:",
                choices=[
                    "🚀 Release",
                    "🐛 Debug",
                    "🔧 ReleaseDebug",
                ],
                style=custom_style,
            ).ask()
        except KeyboardInterrupt:
            choice = None
        
        if choice is None:
            console.print("\n[dim]👋 操作已取消[/dim]")
            return
        
        if "Release" in choice and "Debug" not in choice:
            task = "installEsnRelease"
        elif "Debug" in choice and "Release" not in choice:
            task = "installEsnDebug"
        else:
            task = "installEsnReleaseDebug"
    
    console.print(f"\n[bold cyan]🚀 运行 Gradle 任务[/bold cyan]")
    console.print(f"[dim]   📦 {task}[/dim]\n")
    
    # 执行 Gradle 命令
    gradlew_path = ckesn_path / "gradlew"
    if not gradlew_path.exists():
        console.print("[red]❌ 未找到 gradlew 文件[/red]")
        return
    
    console.print(f"[dim]   💻 ./gradlew {task}[/dim]\n")
    
    try:
        result = subprocess.run(
            ["./gradlew", task],
            cwd=ckesn_path,
            check=False,
        )
        
        if result.returncode == 0:
            console.print(f"\n[green]✨ {task} 执行成功[/green]")
        else:
            console.print(f"\n[red]❌ {task} 执行失败[/red] [dim](退出码: {result.returncode})[/dim]")
    except KeyboardInterrupt:
        console.print("\n[dim]👋 操作已取消[/dim]")
