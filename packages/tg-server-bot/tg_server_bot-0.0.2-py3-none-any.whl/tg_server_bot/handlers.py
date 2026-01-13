# -*- coding: utf-8 -*-
import asyncio
import re
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    BotCommand
)
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, Application
from .utils import (
    logger, reply_message_safely, send_doc_safely, fetch_ip_text,
    check_file_exist, escape_md
)
from .config import Config
from .decorators import authorized_only


def get_main_keyboard():
    """动态生成快捷键菜单"""
    config = Config()
    keyboard = [[KeyboardButton("/ip"),
                 KeyboardButton("/ipv6"),
                 KeyboardButton("/list")]]
    custom_btns = []
    for k in sorted(config.get_cmds.keys()):
        custom_btns.append(KeyboardButton(f"📂 /{k}"))
    for k in sorted(config.run_cmds.keys()):
        custom_btns.append(KeyboardButton(f"🚀 /{k}"))
    for i in range(0, len(custom_btns), 2):
        keyboard.append(custom_btns[i:i + 2])
    keyboard.append([KeyboardButton("/start"), KeyboardButton("/clear")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def update_bot_commands(application: Application):
    """更新机器人的菜单指令列表"""
    config = Config()
    valid_commands = [
        BotCommand("start", "🏠 唤起面板"),
        BotCommand("list", "📜 指令列表"),
        BotCommand("ip", "🌐 IPv4查询"),
        BotCommand("ipv6", "🌍 IPv6查询"),
        BotCommand("run", "💻 执行Shell"),
        BotCommand("clear", "🗑️ 清空临时指令"),
        BotCommand("add_get", "➕ 添加文件指令"),
        BotCommand("add_run", "🚀 添加Shell指令"),
    ]
    cmd_pattern = re.compile(r"^[a-z0-9_]{1,32}$")
    all_custom_cmds = list(config.get_cmds.keys()) + \
        list(config.run_cmds.keys())
    for k in sorted(all_custom_cmds):
        if any(c.command == k for c in valid_commands):
            continue
        if not cmd_pattern.match(k):
            logger.warning(f"⚠️ 跳过非法指令名 '{k}'")
            continue
        desc = f"📂 下载 {k}" if k in config.get_cmds else f"🚀 执行 {k}"
        valid_commands.append(BotCommand(k, desc))
    try:
        await application.bot.set_my_commands(valid_commands)
        logger.info(f"已设置 {len(valid_commands)} 个菜单指令")
    except Exception as e:
        logger.error(f"更新菜单指令失败: {e}")


@authorized_only
async def list_cmds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """列出所有可用指令"""
    config = Config()

    # 准备数据结构
    sections = []

    # 系统管理
    sys_cmds = [
        ("/start", "🏠 唤起面板"),
        ("/list", "📜 刷新列表"),
        ("/ip", "🌐 IPv4 查询"),
        ("/ipv6", "🌍 IPv6 查询"),
        ("/clear", "🗑️ 清空临时指令"),
    ]
    sections.append(("🔹 系统管理:", sys_cmds))

    # 文件下载
    if config.get_cmds:
        file_cmds = []
        for k in sorted(config.get_cmds.keys()):
            file_cmds.append((f"/{k}", config.get_cmds[k]))
        sections.append(("📂 文件下载指令:", file_cmds))

    # 快捷执行
    if config.run_cmds:
        run_cmds = []
        for k in sorted(config.run_cmds.keys()):
            run_cmds.append((f"/{k}", config.run_cmds[k]))
        sections.append(("🚀 快捷执行指令:", run_cmds))

    # 构造纯文本版本
    lines = []

    # 标题
    title = "🤖 机器人当前支持的指令列表:"
    lines.append(title)
    lines.append("")

    # 各个分类
    for category, items in sections:
        lines.append(category)

        for cmd, desc in items:
            lines.append(f"{cmd} - {desc}")
        lines.append("")

    # 底部提示
    lines.append("🔸 注册新指令用法:")
    lines.append("点击下方灰色文字即可复制模版：")
    lines.append("/add_get <指令名> <文件路径>")
    lines.append("/add_run <指令名> <Shell命令>")
    lines.append("示例：/add_run disk df -h")

    plain_text = "\n".join(lines)

    # 发送纯文本消息
    await reply_message_safely(
        update,
        plain_text,
        parse_mode=None,
        reply_markup=get_main_keyboard()
    )


@authorized_only
async def clear_cmds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """清除所有运行态指令"""
    count = Config().clear_runtime_cmds()
    await update_bot_commands(context.application)
    await reply_message_safely(
        update, f"🗑️ 已清空 {count} 条临时指令。",
        parse_mode=None, reply_markup=get_main_keyboard()
    )


@authorized_only
async def add_get_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """动态添加文件下载指令"""
    if not context.args or len(context.args) != 2:
        await reply_message_safely(update, "⚠️ 格式错误: /add_get <name> <path>", parse_mode=None)
        return
    name, path = context.args[0], context.args[1]
    reserved = [
        'start',
        'run',
        'ip',
        'ipv6',
        'add_get',
        'add_run',
        'list',
        'clear',
        'help']
    if name in reserved or Config().is_config_cmd(name):
        await reply_message_safely(update, "❌ 无法覆盖永久或保留指令！")
        return
    Config().add_runtime_cmd('get', name, path)
    await update_bot_commands(context.application)
    await reply_message_safely(
        update, f"✅ 已添加临时文件指令: /{name}",
        parse_mode=None, reply_markup=get_main_keyboard()
    )


@authorized_only
async def add_run_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """动态添加Shell执行指令"""
    if not context.args or len(context.args) < 2:
        await reply_message_safely(update, "⚠️ 格式错误: /add_run <name> <cmd>", parse_mode=None)
        return
    name, cmd = context.args[0], " ".join(context.args[1:])
    reserved = [
        'start',
        'run',
        'ip',
        'ipv6',
        'add_get',
        'add_run',
        'list',
        'clear',
        'help']
    if name in reserved or Config().is_config_cmd(name):
        await reply_message_safely(update, "❌ 无法覆盖永久或保留指令！")
        return
    Config().add_runtime_cmd('run_cmds', name, cmd)
    await update_bot_commands(context.application)
    await reply_message_safely(
        update, f"✅ 已添加临时执行指令: /{name}",
        parse_mode=None, reply_markup=get_main_keyboard()
    )


@authorized_only
async def run_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """手动执行任意 Shell 命令"""
    if not context.args:
        await reply_message_safely(update, '⚠️ 请输入指令', parse_mode=None)
        return
    command = ' '.join(context.args)
    # 反引号内的内容不需要转义
    await reply_message_safely(
        update, f"⏳ 正在执行: `{command}`",
        parse_mode=ParseMode.MARKDOWN_V2
    )
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        output = (
            stdout.decode().strip() +
            "\n" +
            stderr.decode().strip()).strip() or "执行成功，无输出。"

        safe_output = output[-4000:]
        # 代码块内的内容不需要转义
        # 但是命令名称在 * * 之间需要转义
        escaped_command = escape_md(command)
        final_text = f"🖥️ 命令 *{escaped_command}* 的结果:\n\n```\n{safe_output}\n```"
        fallback_text = f"🖥️ 命令 {command} 的结果:\n\n{safe_output}"

        # reply_message_safely 会自动验证和处理
        await reply_message_safely(
            update, final_text,
            parse_mode=ParseMode.MARKDOWN_V2,
            fallback_text=fallback_text
        )

    except Exception as e:
        logger.error(f"Run cmd error: {e}")
        # 反引号内的内容不需要转义
        await reply_message_safely(
            update,
            f"❌ 错误: 执行 `{command}` 出错:\n`{str(e)}`",
            parse_mode=ParseMode.MARKDOWN_V2
        )


@authorized_only
async def run_dynamic_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理动态注册的 Shell 命令"""
    raw_text = update.message.text
    cmd_name = raw_text.split(
        "🚀 /")[-1] if "🚀 /" in raw_text else raw_text.split()[0].lstrip('/')
    shell_cmd = Config().run_cmds.get(cmd_name)
    if not shell_cmd:
        return
    # 反引号内的内容不需要转义
    await reply_message_safely(
        update, f"⏳ 正在执行: `{shell_cmd}`",
        parse_mode=ParseMode.MARKDOWN_V2
    )
    try:
        proc = await asyncio.create_subprocess_shell(
            shell_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        out, err = await proc.communicate()
        res = (
            out.decode().strip() +
            "\n" +
            err.decode().strip()).strip() or "执行成功，无输出。"

        safe_output = res[-4000:]
        # 代码块内的内容不需要转义
        # 但是命令名称在 * * 之间需要转义
        escaped_shell_cmd = escape_md(shell_cmd)
        final_text = f"🖥️ 命令 *{escaped_shell_cmd}* 的结果:\n\n```\n{safe_output}\n```"
        fallback_text = f"🖥️ 命令 {shell_cmd} 的结果:\n\n{safe_output}"

        # reply_message_safely 会自动验证和处理
        await reply_message_safely(
            update, final_text,
            parse_mode=ParseMode.MARKDOWN_V2,
            fallback_text=fallback_text
        )

    except Exception as e:
        logger.error(f"Dynamic execution failed: {e}")
        # 反引号内的内容不需要转义
        await reply_message_safely(
            update,
            f"❌ 错误: 执行 `{shell_cmd}` 出错:\n`{str(e)}`",
            parse_mode=ParseMode.MARKDOWN_V2
        )


@authorized_only
async def get_cmd_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """读取文件内容"""
    if not update.message.text:
        return
    raw_text = update.message.text
    cmd_name = raw_text.split(
        "📂 /")[-1] if "📂 /" in raw_text else raw_text.split()[0].lstrip('/')
    path = Config().get_cmds.get(cmd_name)
    if path and check_file_exist(path):
        await send_doc_safely(update, path)
    else:
        await reply_message_safely(update, "❌ 失败: 文件不存在或指令失效")


@authorized_only
async def dynamic_command_dispatcher(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE):
    """统一分发动态指令和未知文本"""
    text = update.message.text.strip()
    cmd_candidate = text.lstrip('/')
    config = Config()
    if cmd_candidate in config.get_cmds:
        await get_cmd_file(update, context)
        return
    if cmd_candidate in config.run_cmds:
        await run_dynamic_cmd(update, context)
        return
    if check_file_exist(text):
        await send_doc_safely(update, text)
    else:
        await reply_message_safely(update, "❓ 未知指令或文件。输入 /start 唤起面板。")


@authorized_only
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """主面板入口"""
    inline_keyboard = [
        [
            InlineKeyboardButton(
                "🌐 IPv4 查询", callback_data='get_ipv4'), InlineKeyboardButton(
                "🌍 IPv6 查询", callback_data='get_ipv6')], [
                    InlineKeyboardButton(
                        "❓ 帮助 / 状态", callback_data='help_status')]]
    await reply_message_safely(update, "快捷查询:", reply_markup=InlineKeyboardMarkup(inline_keyboard))


@authorized_only
async def reply_menu_handler(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE):
    """处理带图标的快捷按键点击"""
    text = update.message.text
    if text.startswith("📂 /"):
        await get_cmd_file(update, context)
    elif text.startswith("🚀 /"):
        await run_dynamic_cmd(update, context)


@authorized_only
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 Inline 按钮点击事件"""
    query = update.callback_query
    await query.answer()
    if query.data == 'get_ipv4':
        await reply_message_safely(update, "⏳ 正在查询 IPv4", parse_mode=None)
        text = await fetch_ip_text(is_ipv6=False)
        await reply_message_safely(update, text, parse_mode=ParseMode.MARKDOWN_V2)
    elif query.data == 'get_ipv6':
        await reply_message_safely(update, "⏳ 正在查询 IPv6", parse_mode=None)
        text = await fetch_ip_text(is_ipv6=True)
        await reply_message_safely(update, text, parse_mode=ParseMode.MARKDOWN_V2)
    elif query.data == 'help_status':
        await list_cmds(update, context)


@authorized_only
async def get_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """获取服务器 IP 地址"""
    is_ipv6 = 'ipv6' in update.message.text.lower()
    text = await fetch_ip_text(is_ipv6)
    await reply_message_safely(update, text=text, parse_mode=ParseMode.MARKDOWN_V2)
