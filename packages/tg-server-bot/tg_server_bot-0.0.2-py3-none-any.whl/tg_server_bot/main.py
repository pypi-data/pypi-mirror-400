# -*- coding: utf-8 -*-
import argparse
import os
import sys
import shutil
import platform
import subprocess
import time
from importlib import metadata
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from .const import DEF_CONFIG_FILE_NAME, DEF_ALLOW_USER_FILE
from .utils import setup_logging, logger, get_package_file_path
from .config import Config, PermissionHelper
from .handlers import (
    start, run_cmd, get_ip, add_get_cmd, add_run_cmd, clear_cmds, list_cmds,
    button_handler, reply_menu_handler, dynamic_command_dispatcher,
    update_bot_commands
)

try:
    __version__ = metadata.version("tg-server-bot")
except metadata.PackageNotFoundError:
    __version__ = "unknown (not installed)"


async def post_init(application):
    """启动后自动设置菜单指令"""
    await update_bot_commands(application)


async def error_handler(update: object, context):
    """全局错误处理"""
    logger.error("Update Error:", exc_info=context.error)
    # 尝试通知用户发生了错误（使用简单的 reply_text 避免无限递归）
    if update and hasattr(update, 'effective_message') and \
            update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⚠️ 处理请求时发生错误，请稍后重试。"
            )
        except Exception:
            # 如果通知失败也不要崩溃
            pass


def get_default_config_path():
    """获取默认的配置文件路径"""
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(pkg_dir, DEF_CONFIG_FILE_NAME)


def ensure_config_exists(target_path):
    """确保配置文件存在，不存在则从模板复制"""
    if not os.path.exists(target_path):
        pkg_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(pkg_dir, 'config-ex.ini')
        if os.path.exists(template_path):
            try:
                target_dir = os.path.dirname(os.path.abspath(target_path))
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir, exist_ok=True)
                shutil.copy2(template_path, target_path)
                print(f"配置文件不存在，已自动从模板创建: {target_path}")
            except Exception as e:
                print(f"⚠️ 无法自动创建配置文件: {e}")
    return target_path


def get_default_auth_path():
    """获取默认的授权文件路径"""
    return get_package_file_path(DEF_ALLOW_USER_FILE)


def show_template(template_name):
    """打印模版文件内容"""
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(pkg_dir, template_name)
    if os.path.exists(template_path):
        print(f"\n--- Template: {template_name} ---")
        with open(template_path, 'r', encoding='utf-8') as f:
            print(f.read())
        print("-------------------------------\n")
    else:
        print(f"⚠️ Template file not found: {template_path}")


def _open_in_editor(file_path):
    """通用编辑器调用逻辑"""
    system = platform.system()
    try:
        if system == 'Windows':
            subprocess.run(['notepad', file_path])
        else:
            editors = ['vim', 'nano', 'vi']
            editor = os.environ.get('EDITOR')
            if editor:
                editors.insert(0, editor)
            found = False
            for ed in editors:
                if shutil.which(ed):
                    subprocess.run([ed, file_path])
                    found = True
                    break
            if not found:
                print("Error: No suitable text editor found (vim, nano, vi).")
    except Exception as e:
        print(f"Error opening editor: {e}")


def edit_config():
    """打开编辑器修改配置文件"""
    default_path = get_default_config_path()
    arg_p = argparse.ArgumentParser(
        description="Edit Telegram Bot configuration")
    arg_p.add_argument(
        '-c',
        '--config',
        default=default_path,
        help=f"Path to config file (default: {default_path})")
    arg_p.add_argument(
        '-e',
        '--example',
        action='store_true',
        help="Show config template content")
    args = arg_p.parse_args()
    if args.example:
        show_template('config-ex.ini')
        return
    target_file = ensure_config_exists(args.config)
    print(f"Opening config file: {target_file}")
    _open_in_editor(target_file)


def edit_auth():
    """打开编辑器修改授权用户列表"""
    arg_p = argparse.ArgumentParser(
        description="Edit Telegram Bot Authorized Users")
    arg_p.add_argument(
        '-e',
        '--example',
        action='store_true',
        help="Show auth template content")
    args = arg_p.parse_args()
    if args.example:
        show_template('verified_id-ex.txt')
        return
    auth_file = get_default_auth_path()
    if not os.path.exists(auth_file):
        pkg_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(pkg_dir, 'verified_id-ex.txt')
        if os.path.exists(template_path):
            try:
                auth_dir = os.path.dirname(os.path.abspath(auth_file))
                if not os.path.exists(auth_dir):
                    os.makedirs(auth_dir, exist_ok=True)
                shutil.copy2(template_path, auth_file)
                print(f"授权文件不存在，已自动从模板创建: {auth_file}")
            except Exception as e:
                print(f"⚠️ 无法自动创建授权文件: {e}")
    print(f"Opening auth file: {auth_file}")
    _open_in_editor(auth_file)


def main():
    """程序入口"""
    default_path = get_default_config_path()
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    arg_p = argparse.ArgumentParser()
    arg_p.add_argument(
        '-v',
        '--version',
        action='store_true',
        help="Print version and installation path")
    arg_p.add_argument(
        '-c',
        '--config',
        default=default_path,
        help=f"Path to config file (default: {default_path})")
    args = arg_p.parse_args()
    if args.version:
        print(f"tg-bot version: {__version__}")
        print(f"Installation path: {pkg_dir}")
        sys.exit(0)
    config_path = ensure_config_exists(args.config)
    cfg = Config()
    cfg.load(config_path)
    if cfg.pwd:
        try:
            if not os.path.exists(cfg.pwd):
                raise FileNotFoundError("目录不存在")
            os.chdir(cfg.pwd)
            logger.info(f"已成功切换工作目录到: {os.getcwd()}")
        except Exception as e:
            logger.error(f"❌ 关键错误: 无法切换到设定的工作目录 '{cfg.pwd}': {e}")
            sys.exit(1)
    setup_logging(
        log_file=cfg.log_file if cfg.log_file else None,
        enable_console=True)
    if not cfg.token:
        if config_path.endswith(
                'config-ex.ini') or config_path.endswith('config.ini'):
            logger.warning(f"检测到 Token 未配置。请编辑配置文件: {config_path}")
            logger.warning("提示: 可以使用 'tg-bot-cfg' 命令快速打开编辑器。")
        return
    perm = PermissionHelper()
    if not perm.allow_user_ids:
        logger.warning(f"⚠️ 警告: 白名单为空或文件不存在: {perm.allow_user_file}")
        logger.warning("请立即使用 'tg-bot-auth' 添加您的 Telegram User ID，否则无法使用机器人！")
    app = ApplicationBuilder().token(cfg.token).post_init(post_init)
    if cfg.proxy:
        app.get_updates_proxy(cfg.proxy).proxy(cfg.proxy)
    bot = app.build()
    bot.add_handler(CommandHandler('start', start, block=False))
    bot.add_handler(CommandHandler('run', run_cmd, block=False))
    bot.add_handler(CommandHandler(['ip', 'ipv6'], get_ip, block=False))
    bot.add_handler(CommandHandler('add_get', add_get_cmd, block=False))
    bot.add_handler(CommandHandler('add_run', add_run_cmd, block=False))
    bot.add_handler(CommandHandler('clear', clear_cmds, block=False))
    bot.add_handler(CommandHandler(['list', 'help'], list_cmds, block=False))
    bot.add_handler(CallbackQueryHandler(button_handler, block=False))
    bot.add_handler(
        MessageHandler(
            filters.Regex(r'^(📂 /|🚀 /)'),
            reply_menu_handler,
            block=False))
    bot.add_handler(
        MessageHandler(
            filters.ALL,
            dynamic_command_dispatcher,
            block=False))
    bot.add_error_handler(error_handler)
    logger.info("🤖 机器人已启动，开始监听消息...")
    while True:
        try:
            logger.info("Starting polling loop...")
            bot.run_polling()
        except KeyboardInterrupt:
            logger.info("收到中断信号，正在关闭...")
            break
        except Exception as e:
            logger.error(f"⚠️ Polling loop crashed: {e}", exc_info=True)
            logger.info("🔄 将在 5 秒后自动重启...")
            time.sleep(5)


if __name__ == '__main__':
    main()
