"""
项目级配置管理模块

管理当前工作目录下的 .esntool 配置，存储项目选择等信息。
与全局配置 (~/.esntool) 分离，支持项目级别的配置管理。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# 项目配置目录名
PROJECT_CONFIG_DIR_NAME = ".esntool"
PROJECT_CONFIG_FILE_NAME = "config.json"


def find_project_config_dir(start_path: Path | None = None) -> Path | None:
    """
    从当前目录向上查找 .esntool 配置目录。
    
    Args:
        start_path: 起始搜索路径，默认为当前工作目录
        
    Returns:
        找到的 .esntool 目录路径，未找到返回 None
    """
    if start_path is None:
        start_path = Path.cwd()
    
    current = start_path.resolve()
    
    # 向上最多查找 10 层
    for _ in range(10):
        config_dir = current / PROJECT_CONFIG_DIR_NAME
        if config_dir.is_dir():
            return config_dir
        
        parent = current.parent
        if parent == current:  # 到达根目录
            break
        current = parent
    
    return None


def get_project_config_dir(base_path: Path | None = None) -> Path:
    """
    获取项目配置目录路径（用于初始化时创建）。
    
    Args:
        base_path: 基础目录，默认为当前工作目录
        
    Returns:
        .esntool 目录路径
    """
    if base_path is None:
        base_path = Path.cwd()
    return base_path / PROJECT_CONFIG_DIR_NAME


def load_project_config(config_dir: Path | None = None) -> dict[str, Any]:
    """
    加载项目配置。
    
    Args:
        config_dir: 配置目录路径，如果为 None 则自动查找
        
    Returns:
        配置字典
    """
    if config_dir is None:
        config_dir = find_project_config_dir()
    
    if config_dir is None:
        return {}
    
    config_file = config_dir / PROJECT_CONFIG_FILE_NAME
    
    if not config_file.exists():
        return {}
    
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_project_config(config: dict[str, Any], base_path: Path | None = None) -> Path:
    """
    保存项目配置。
    
    Args:
        config: 配置字典
        base_path: 基础目录，默认为当前工作目录
        
    Returns:
        配置文件路径
    """
    config_dir = get_project_config_dir(base_path)
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config_file = config_dir / PROJECT_CONFIG_FILE_NAME
    
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    return config_file


def get_selected_repos(base_path: Path | None = None) -> list[Path] | None:
    """
    获取已选择的仓库列表。
    
    Args:
        base_path: 基础目录，默认为当前工作目录
        
    Returns:
        仓库路径列表（绝对路径），如果未初始化返回 None
    """
    if base_path is None:
        base_path = Path.cwd()
    
    config_dir = find_project_config_dir(base_path)
    
    if config_dir is None:
        return None
    
    config = load_project_config(config_dir)
    projects = config.get("projects", [])
    
    if not projects:
        return None
    
    # 配置目录的父目录是项目根目录
    project_root = config_dir.parent
    
    # 将相对路径转换为绝对路径
    repos = []
    for rel_path in projects:
        abs_path = (project_root / rel_path).resolve()
        if abs_path.is_dir():
            repos.append(abs_path)
    
    return repos if repos else None


def is_initialized(base_path: Path | None = None) -> bool:
    """
    检查当前目录是否已初始化。
    
    Args:
        base_path: 基础目录，默认为当前工作目录
        
    Returns:
        是否已初始化
    """
    if base_path is None:
        base_path = Path.cwd()
    
    config_dir = find_project_config_dir(base_path)
    return config_dir is not None
