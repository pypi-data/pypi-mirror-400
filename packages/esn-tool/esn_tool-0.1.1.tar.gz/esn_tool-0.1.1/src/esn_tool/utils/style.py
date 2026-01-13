"""
统一的交互式 UI 样式配置

提供美观一致的 questionary 样式和常用选择器。
"""

from questionary import Style

# 统一的美化样式
CUSTOM_STYLE = Style([
    # 问号标记
    ("qmark", "fg:#ff9d00 bold"),           # 橙色问号
    # 问题文本
    ("question", "fg:#ffffff bold"),         # 白色粗体
    # 回答文本
    ("answer", "fg:#00d7ff"),                # 青色
    # 指针（箭头）
    ("pointer", "fg:#ff9d00 bold"),          # 橙色箭头
    # 高亮选项（当前光标所在）- 无背景
    ("highlighted", "fg:#ff9d00 noreverse"), # 橙色，禁用反色
    # 已选中的选项（checkbox 打勾的）
    ("selected", "fg:#00d7ff noreverse"),    # 青色，禁用反色
    # 分隔符
    ("separator", "fg:#6c6c6c"),             # 灰色
    # 指令文本
    ("instruction", "fg:#6c6c6c"),           # 灰色
    # 文本输入
    ("text", "fg:#ffffff"),                  # 白色
    # 禁用选项
    ("disabled", "fg:#6c6c6c"),              # 灰色
])


def get_style() -> Style:
    """获取统一的 questionary 样式"""
    return CUSTOM_STYLE
