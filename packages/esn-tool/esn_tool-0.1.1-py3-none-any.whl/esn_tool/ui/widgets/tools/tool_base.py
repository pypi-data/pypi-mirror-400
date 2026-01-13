"""
工具基类

定义所有工具必须实现的接口。
"""

from abc import ABC, abstractmethod

from textual.widget import Widget


class ToolBase(ABC):
    """工具基类，所有工具都应该继承此类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """工具名称"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """工具描述"""
        pass

    @property
    def icon(self) -> str:
        """工具图标（emoji）"""
        return "🔧"

    @property
    def category(self) -> str:
        """工具分类"""
        return "通用"

    @abstractmethod
    def create_widget(self) -> Widget:
        """创建工具的 UI Widget
        
        Returns:
            Widget: Textual Widget 实例
        """
        pass
