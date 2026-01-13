#!/usr/bin/env python3
"""
ESN Tool macOS PKG 打包脚本

此脚本将 esn-tool 打包成 macOS 安装包(.pkg)
支持多架构打包: ARM64 和 x86_64
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# 支持的架构
ARCHITECTURES = {
    'arm64': 'esn-arm64.spec',
    'x86_64': 'esn-x86_64.spec',
}


def get_system_arch():
    """获取当前系统架构"""
    machine = platform.machine().lower()
    if machine == 'arm64':
        return 'arm64'
    elif machine in ('x86_64', 'amd64'):
        return 'x86_64'
    else:
        return machine


def get_compatible_architectures():
    """获取当前系统可以构建的架构列表"""
    system_arch = get_system_arch()
    
    if system_arch == 'arm64':
        # M1/M2/M3 Mac 只能原生构建 arm64
        # 交叉编译 x86_64 需要 x86_64 版本的 Python 和依赖
        return ['arm64']
    elif system_arch == 'x86_64':
        # Intel Mac 可以构建两种架构
        return ['arm64', 'x86_64']
    else:
        # 未知架构,只构建当前架构
        return [system_arch]


# 从 pyproject.toml 读取版本
def get_version():
    """从 pyproject.toml 读取版本号"""
    pyproject_file = PROJECT_ROOT / "pyproject.toml"
    try:
        # Python 3.11+ 自带 tomllib
        import tomllib
        with open(pyproject_file, 'rb') as f:
            data = tomllib.load(f)
            return data.get('project', {}).get('version', '0.1.0')
    except ImportError:
        # Python 3.10 及以下，回退到简单解析
        with open(pyproject_file, 'r') as f:
            for line in f:
                if line.strip().startswith('version'):
                    # 支持双引号和单引号
                    import re
                    match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', line)
                    if match:
                        return match.group(1)
        return "0.1.0"


VERSION = get_version()


def run_command(cmd, description):
    """运行命令并打印输出"""
    print(f"\n{'=' * 60}")
    print(f"🔧 {description}")
    print(f"{'=' * 60}")
    print(f"执行命令: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    if result.returncode != 0:
        print(f"\n❌ 错误: {description} 失败")
        sys.exit(1)
    print(f"✅ {description} 完成")


def clean_build_dirs():
    """清理构建目录"""
    print("\n🧹 清理旧的构建文件...")
    dirs_to_clean = [BUILD_DIR, DIST_DIR]
    for d in dirs_to_clean:
        if d.exists():
            shutil.rmtree(d)
            print(f"  已删除: {d}")


def build_executable(arch):
    """使用 PyInstaller 构建特定架构的可执行文件"""
    spec_file = ARCHITECTURES[arch]
    run_command(
        ["uv", "run", "pyinstaller", "--clean", spec_file],
        f"构建 {arch} 可执行文件"
    )


def prepare_pkg_structure(arch):
    """准备特定架构 pkg 包的目录结构"""
    pkg_root = PROJECT_ROOT / f"pkg_root_{arch}"
    
    print(f"\n📦 准备 {arch} pkg 包目录结构...")
    
    # 清理旧的 pkg_root
    if pkg_root.exists():
        shutil.rmtree(pkg_root)
    
    # 创建安装目录结构
    bin_dir = pkg_root / "usr" / "local" / "bin"
    share_dir = pkg_root / "usr" / "local" / "share" / "esntool"
    
    bin_dir.mkdir(parents=True, exist_ok=True)
    share_dir.mkdir(parents=True, exist_ok=True)
    
    # 复制可执行文件
    exe_source = DIST_DIR / "esn"
    exe_dest = bin_dir / "esn"
    shutil.copy2(exe_source, exe_dest)
    print(f"  已复制: {exe_source} -> {exe_dest}")
    
    # 设置可执行权限
    exe_dest.chmod(0o755)
    
    # 复制卸载脚本
    uninstall_source = SCRIPTS_DIR / "uninstall.sh"
    uninstall_dest = share_dir / "uninstall.sh"
    shutil.copy2(uninstall_source, uninstall_dest)
    uninstall_dest.chmod(0o755)
    print(f"  已复制: {uninstall_source} -> {uninstall_dest}")
    
    return pkg_root


def build_pkg(arch, pkg_root):
    """构建特定架构的 macOS pkg 安装包"""
    pkg_name = f"esn-{VERSION}-{arch}.pkg"
    output_pkg = DIST_DIR / pkg_name
    
    # 确保 dist 目录存在
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    
    # 确保 scripts 目录中的 postinstall 有执行权限
    postinstall = SCRIPTS_DIR / "postinstall"
    if postinstall.exists():
        os.chmod(postinstall, 0o755)
    
    run_command(
        [
            "pkgbuild",
            "--root", str(pkg_root),
            "--identifier", f"com.esntool.cli.{arch}",
            "--version", VERSION,
            "--scripts", str(SCRIPTS_DIR),
            "--install-location", "/",
            str(output_pkg)
        ],
        f"构建 {arch} pkg 安装包"
    )
    
    return output_pkg


def build_architecture(arch):
    """构建特定架构的完整流程"""
    print(f"\n{'=' * 60}")
    print(f"🏗️  开始构建 {arch} 架构")
    print(f"{'=' * 60}")
    
    build_executable(arch)
    pkg_root = prepare_pkg_structure(arch)
    output_pkg = build_pkg(arch, pkg_root)
    
    # 清理临时 pkg_root
    if pkg_root.exists():
        shutil.rmtree(pkg_root)
    
    return output_pkg


def print_summary(packages):
    """打印构建摘要"""
    print(f"\n{'=' * 60}")
    print(f"✨ 所有架构打包完成!")
    print(f"{'=' * 60}")
    
    for pkg in packages:
        arch = 'arm64' if 'arm64' in pkg.name else 'x86_64'
        size_mb = pkg.stat().st_size / 1024 / 1024
        print(f"\n📦 {arch} 安装包:")
        print(f"  文件: {pkg}")
        print(f"  大小: {size_mb:.2f} MB")
    
    print(f"\n安装方式:")
    print(f"  双击安装包或运行: sudo installer -pkg <pkg文件> -target /")
    print(f"\n卸载方式:")
    print(f"  sudo /usr/local/share/esntool/uninstall.sh")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='ESN Tool PKG 打包工具')
    parser.add_argument(
        '--arch',
        choices=['arm64', 'x86_64', 'all'],
        default='all',
        help='指定要打包的架构 (默认: all)'
    )
    
    args = parser.parse_args()
    
    print(f"""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║              ESN Tool PKG 打包工具                         ║
║              版本: {VERSION:<44} ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # 检查是否在 macOS 上运行
    if sys.platform != "darwin":
        print("❌ 错误: 此脚本只能在 macOS 上运行")
        sys.exit(1)
    
    # 检查 uv 是否安装
    try:
        subprocess.run(["uv", "--version"], 
                      capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ 错误: 未找到 uv")
        print("请运行: brew install uv")
        sys.exit(1)
    
    # 获取系统信息
    system_arch = get_system_arch()
    compatible_archs = get_compatible_architectures()
    
    print(f"\n📱 系统架构: {system_arch}")
    
    # 确定要构建的架构
    if args.arch == 'all':
        architectures = compatible_archs
        print(f"✅ 将构建支持的架构: {', '.join(compatible_archs)}")
        
        if system_arch == 'arm64':
            print(f"\n💡 提示: 在 M1/M2/M3 Mac 上只能构建 ARM64 架构")
            print(f"   如需 x86_64 版本:")
            print(f"   - 在 Intel Mac 上运行此脚本")
            print(f"   - 或使用 GitHub Actions CI 自动构建")
    else:
        architectures = [args.arch]
        # 检查请求的架构是否兼容
        if args.arch not in compatible_archs:
            print(f"\n⚠️  警告: 当前系统 ({system_arch}) 无法构建 {args.arch} 架构")
            print(f"   支持的架构: {', '.join(compatible_archs)}")
            print(f"\n❌ 停止构建")
            sys.exit(1)
    
    # 清理构建目录
    clean_build_dirs()
    
    # 构建每个架构
    packages = []
    for arch in architectures:
        try:
            pkg = build_architecture(arch)
            packages.append(pkg)
        except Exception as e:
            print(f"\n⚠️  警告: {arch} 架构构建失败: {e}")
            if args.arch != 'all':
                # 如果只构建单个架构且失败，则退出
                sys.exit(1)
            # 如果构建所有架构，继续构建下一个
            continue
    
    # 打印摘要
    if packages:
        print_summary(packages)
    else:
        print("\n❌ 错误: 所有架构构建均失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
