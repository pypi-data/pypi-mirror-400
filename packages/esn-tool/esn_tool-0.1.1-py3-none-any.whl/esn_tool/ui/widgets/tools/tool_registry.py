"""
工具注册表

管理所有可用的工具实例。
"""

from typing import Dict, List

from esn_tool.ui.widgets.tools.tool_base import ToolBase


class ToolRegistry:
    """工具注册表，使用单例模式管理所有工具"""

    _instance = None
    _tools: Dict[str, ToolBase] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tools = {}
        return cls._instance

    def register(self, tool: ToolBase) -> None:
        """注册一个工具
        
        Args:
            tool: 工具实例
        """
        self._tools[tool.name] = tool

    def unregister(self, name: str) -> None:
        """注销一个工具
        
        Args:
            name: 工具名称
        """
        if name in self._tools:
            del self._tools[name]

    def get(self, name: str) -> ToolBase | None:
        """获取工具实例
        
        Args:
            name: 工具名称
            
        Returns:
            工具实例，如果不存在返回 None
        """
        return self._tools.get(name)

    def get_all(self) -> List[ToolBase]:
        """获取所有已注册的工具
        
        Returns:
            工具列表
        """
        return list(self._tools.values())

    def clear(self) -> None:
        """清空所有已注册的工具"""
        self._tools.clear()


# 创建全局注册表实例
registry = ToolRegistry()
