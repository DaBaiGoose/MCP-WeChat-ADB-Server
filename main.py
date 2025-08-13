#!/usr/bin/env python3
"""
WeChat MCP Server for LDPlayer
用法：
    ① 设置环境变量：set LDPLAYER_DIR=D:\Program\leidian\LDPlayer9
    ② 或者直接运行：python wechat_mcp.py --ldplayer-dir D:\Program\leidian\LDPlayer9
"""
import os
import sys
import time
import argparse
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from wechat_example import WeChat        


# 模拟器目录位置
ldplayer_dir = "D:/Program/leidian/LDPlayer9"

# ---------- 配置读取 ----------
def resolve_ldplayer_dir() -> Path:
    """优先级：命令行参数 > 环境变量 > 默认路径"""
    parser = argparse.ArgumentParser(description="WeChat MCP Server")
    parser.add_argument("--ldplayer-dir", type=str,
                        help="雷电模拟器安装目录（包含 adb.exe）")
    args, _ = parser.parse_known_args()

    # 1. 命令行
    if args.ldplayer_dir:
        return Path(args.ldplayer_dir).expanduser().resolve()

    # 2. 环境变量
    env = os.getenv("LDPLAYER_DIR")
    if env:
        return Path(env).expanduser().resolve()

    # 3. 默认
    default = Path(ldplayer_dir)
    return default

# ---------- 路径与参数 ----------
LD_DIR   = resolve_ldplayer_dir()
ADB_PATH = LD_DIR / "adb.exe"
DEVICE   = "127.0.0.1:5555"           # 可在 模拟器 诊断信息里查看端口，默认是5555

# ---------- 启动检查 ----------
if not ADB_PATH.exists():
    sys.exit(f"adb.exe 未找到，请检查 LDPLAYER_DIR 设置：{ADB_PATH}")

mcp = FastMCP("WeChatSender")

# ---------- 初始化 WeChat ----------
we = WeChat(
    adb_path     = str(ADB_PATH),
    start_command= f"{ADB_PATH} connect {DEVICE}",
    adb_command  = str(ADB_PATH),
    device_address = DEVICE
)

# ---------- 工具 ----------
@mcp.tool()
def send_wechat_message(name: str, message: str) -> str:
    """
    给指定联系人发送微信消息。
    参数:
        name: 联系人昵称/备注
        message: 消息内容
    返回:
        成功/失败描述
    """
    try:
        we.send_message(name, message)
        return f"✅ 已发送给 {name}"
    except Exception as e:
        return f"❌ 发送失败: {e}"

# @mcp.tool()
# def send_wechat_messages_batch(messages: list) -> str:
#     """
#     批量发送微信消息。
#     每条格式: {"name": "张三", "message": "你好"}
#     返回:
#         成功/失败统计
#     """
#     ok = fail = 0
#     log = []
#     for item in messages:
#         try:
#             we.send_message(item["name"], item["message"])
#             ok += 1
#             log.append(f"✅ {item['name']}")
#         except Exception as e:
#             fail += 1
#             log.append(f"❌ {item['name']}: {e}")
#     return f"批量发送完成：{ok} 成功 / {fail} 失败\n" + "\n".join(log)

@mcp.tool()
def screen_save() -> str:
    """截图并返回本地路径"""
    try:
        return we.get_screenshot()
    except Exception as e:
        return f"截图失败: {e}"

# ---------- 入口 ----------
if __name__ == "__main__":
    # 首次连接
    we.run_adb_command([str(ADB_PATH), "connect", DEVICE])
    time.sleep(1)
    mcp.run(transport="sse")