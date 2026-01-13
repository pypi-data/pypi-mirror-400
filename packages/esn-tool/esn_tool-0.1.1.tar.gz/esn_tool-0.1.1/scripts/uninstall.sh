#!/bin/bash
#
# ESN Tool 卸载脚本
# 用法: sudo /usr/local/share/esn/uninstall.sh

set -e

echo ""
echo "════════════════════════════════════════════════════════"
echo "  ESN Tool 卸载工具"
echo "════════════════════════════════════════════════════════"
echo ""

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 错误: 请使用 sudo 运行此脚本"
    echo "命令: sudo $0"
    exit 1
fi

# 删除可执行文件
if [ -f "/usr/local/bin/esn" ]; then
    echo "🗑️  删除: /usr/local/bin/esn"
    rm -f /usr/local/bin/esn
else
    echo "⚠️  未找到: /usr/local/bin/esn"
fi

# 删除共享文件
if [ -d "/usr/local/share/esn" ]; then
    echo "🗑️  删除: /usr/local/share/esn"
    rm -rf /usr/local/share/esn
fi

echo ""
echo "✅ ESN Tool 已卸载"
echo ""

# 询问是否删除配置文件
read -p "是否同时删除配置文件? (~/.esn) [y/N]: " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 获取实际用户的 HOME 目录（即使用 sudo 运行）
    REAL_USER=$(logname 2>/dev/null || echo $SUDO_USER)
    if [ -n "$REAL_USER" ]; then
        USER_HOME=$(eval echo ~$REAL_USER)
        CONFIG_DIR="$USER_HOME/.esn"
        
        if [ -d "$CONFIG_DIR" ]; then
            echo "🗑️  删除: $CONFIG_DIR"
            rm -rf "$CONFIG_DIR"
            echo "✅ 配置文件已删除"
        else
            echo "⚠️  未找到配置目录: $CONFIG_DIR"
        fi
    fi
else
    echo "ℹ️  保留配置文件"
fi

echo ""
echo "════════════════════════════════════════════════════════"
echo "  卸载完成"
echo "════════════════════════════════════════════════════════"
echo ""

exit 0
