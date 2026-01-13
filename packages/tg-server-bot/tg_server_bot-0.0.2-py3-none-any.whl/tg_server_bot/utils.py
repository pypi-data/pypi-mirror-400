# -*- coding: utf-8 -*-
import asyncio
import functools
import logging
import logging.handlers
import os
import queue
from io import BytesIO
import aiofiles
import aiohttp
from telegram import Update
from telegram.constants import ParseMode
from telegram.error import BadRequest, NetworkError, TimedOut
from .const import IPV4_APIS, IPV6_APIS
log_queue = queue.Queue(-1)
queue_handler = logging.handlers.QueueHandler(log_queue)
logger = logging.getLogger('tg_server_bot')
logger.setLevel(logging.INFO)
logger.propagate = False
if not logger.handlers:
    logger.addHandler(queue_handler)


def setup_logging(log_file=None, enable_console=True):
    """初始化日志监听器"""
    handlers = []
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            handlers.append(file_handler)
        except Exception as e:
            print(f"⚠️ 无法创建日志文件 {log_file}: {e}")
    listener = logging.handlers.QueueListener(log_queue, *handlers)
    listener.start()
    return listener


def singleton(cls):
    """单例模式装饰器"""
    instances = {}

    @functools.wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance


def get_file_modify_time(file_path: str) -> float:
    try:
        return os.path.getmtime(file_path)
    except OSError:
        return 0


def check_file_exist(file_path: str) -> bool:
    return bool(
        file_path and os.path.exists(file_path) and os.path.isfile(file_path)
    )


def escape_md(text: str) -> str:
    """转义 MarkdownV2 特殊字符"""
    escape_chars = r'_*[]()~`><#+-=|{}.!'
    return "".join(
        f"\\{char}" if char in escape_chars else char for char in text
    )


def strip_markdown(text: str) -> str:
    """
    移除 MarkdownV2 格式标记，返回纯文本
    用于在 Markdown 解析失败时提供干净的降级文本
    """
    import re

    # 移除代码块标记 ```
    result = re.sub(r'```\n?', '', text)

    # 移除行内代码标记 `
    result = re.sub(r'`', '', result)

    # 移除粗体标记 **text** 或 *text* (先处理双星号，再处理单星号)
    result = re.sub(r'\*\*(.+?)\*\*', r'\1', result)
    result = re.sub(r'\*(.+?)\*', r'\1', result)

    # 移除斜体标记 __text__ 或 _text_
    result = re.sub(r'__(.+?)__', r'\1', result)
    result = re.sub(r'_(.+?)_', r'\1', result)

    # 移除删除线 ~~text~~
    result = re.sub(r'~~(.+?)~~', r'\1', result)

    # 移除链接 [text](url)，保留文本
    result = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', result)

    # 移除转义符号 (包括双反斜杠)
    # 先处理 \\ -> \
    result = re.sub(r'\\\\', '\x00', result)  # 临时标记
    # 再移除单个转义符
    result = re.sub(r'\\([_*\[\]()~`><#+=|{}.!-])', r'\1', result)
    # 恢复双反斜杠为单反斜杠
    result = result.replace('\x00', '\\')

    return result


def validate_markdown_v2(text: str) -> bool:
    """
    验证文本是否可能导致 MarkdownV2 解析错误
    返回 True 表示格式可能有问题，应该使用纯文本
    """
    # 检查不平衡的标记
    for marker in ['*', '_', '`']:
        # 这些标记需要成对出现
        if text.count(marker) % 2 != 0:
            return False

    # 检查方括号和圆括号的平衡
    if text.count('[') != text.count(']'):
        return False
    if text.count('(') != text.count(')'):
        return False

    # 检查是否有未转义的特殊字符（在非 code 块中）
    # 简单检查：如果有很多特殊字符但没有反斜杠，可能有问题
    special_chars = r'_*[]()~`><#+-=|{}.!'
    special_count = sum(1 for c in text if c in special_chars)
    escape_count = text.count('\\')

    # 如果特殊字符很多但转义很少，可能有问题
    if special_count > 10 and escape_count < special_count * 0.3:
        return False

    return True


def prepare_markdown_text(text: str, auto_escape: bool = False) -> tuple:
    """
    准备 Markdown 文本，返回 (markdown_text, parse_mode, fallback_text)

    Args:
        text: 原始文本
        auto_escape: 是否自动转义（用于命令输出等动态内容）

    Returns:
        (markdown_text, parse_mode, fallback_text)
        - 如果格式正确: (markdown_text, ParseMode.MARKDOWN_V2, None)
        - 如果需要降级: (plain_text, None, None)
    """
    if auto_escape:
        # 对于动态内容，自动转义并包裹在 code 块中
        escaped = escape_md(text)
        markdown_text = f"```\n{escaped}\n```"
        return (markdown_text, ParseMode.MARKDOWN_V2, text)

    # 验证 Markdown 格式
    if validate_markdown_v2(text):
        return (text, ParseMode.MARKDOWN_V2, None)
    else:
        # 格式可能有问题，直接使用纯文本
        logger.warning("检测到可能的 Markdown 格式问题，使用纯文本模式")
        return (text, None, None)


async def reply_message_safely(
    update: Update,
    text: str,
    parse_mode=ParseMode.MARKDOWN_V2,
    max_retries=3,
    reply_markup=None,
    fallback_text=None
):
    """安全回复消息，带重试机制和提前验证"""
    async def _do_send(content, p_mode):
        """内部发送逻辑"""
        target = (
            update.message if update.message else update.callback_query.message
        )
        if not target:
            return
        await target.reply_text(
            content, parse_mode=p_mode, reply_markup=reply_markup
        )

    current_text = text
    current_parse_mode = parse_mode

    # 提前验证 Markdown 格式
    if parse_mode == ParseMode.MARKDOWN_V2:
        if not validate_markdown_v2(text):
            logger.info("检测到 Markdown 格式问题，提前降级为纯文本")
            current_parse_mode = None
            # 如果有 fallback_text 就用，否则自动清理 Markdown 标记
            current_text = fallback_text if fallback_text else strip_markdown(text)

    attempt = 0
    while attempt < max_retries:
        try:
            await _do_send(current_text, current_parse_mode)
            return
        except BadRequest as e:
            # 如果是 Markdown 解析错误，降级为纯文本
            err_msg = str(e).lower()
            if (
                ("parse" in err_msg or "entities" in err_msg)
                and current_parse_mode is not None
            ):
                logger.warning(
                    f"Markdown 解析失败，降级为纯文本重试。文本: {current_text}, 错误: {e}")
                # 切换到纯文本模式，并且不计入网络重试次数 (continue 重新进入循环)
                current_parse_mode = None
                # 如果有 fallback_text 就用，否则自动清理 Markdown 标记
                current_text = fallback_text if fallback_text else strip_markdown(text)
                continue
            else:
                # 其他 BadRequest 错误也优雅处理，避免 bot 崩溃
                logger.error(f"回复请求错误: {e}，跳过此消息")
                return
        except (NetworkError, TimedOut) as e:
            attempt += 1
            if attempt < max_retries:
                wait_time = attempt * 2
                logger.warning(
                    f"网络错误 ({attempt}/{max_retries}), {wait_time}s后重试: {e}"
                )
                await asyncio.sleep(wait_time)
            else:
                # 网络超时是暂时性错误，不应该让整个 bot 崩溃
                # 记录错误后优雅返回，让 bot 继续处理其他更新
                logger.error(f"回复失败 ({max_retries}次): {e}，跳过此消息")
                return  # 优雅返回，不抛出异常
        except Exception as e:
            # 任何其他异常也优雅处理，避免 bot 崩溃
            logger.error(f"回复出错: {e}，跳过此消息")
            return


async def send_doc_safely(update: Update, doc_path: str, max_retries=3):
    """安全发送文件，带重试机制"""
    for attempt in range(max_retries):
        try:
            async with aiofiles.open(doc_path, 'rb') as f:
                content = await f.read()
            bio = BytesIO(content)
            bio.name = os.path.basename(doc_path)
            await update.message.reply_document(document=bio)
            return
        except Exception as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(2)
            else:
                logger.error(f"发送文件失败 {doc_path}: {e}")
                await reply_message_safely(
                    update, f"❌ 发送文件失败: {doc_path}", parse_mode=None
                )


async def fetch_ip_text(is_ipv6: bool = False) -> str:
    """获取 IP 核心逻辑，返回适用于 MarkdownV2 的格式"""
    apis = IPV6_APIS if is_ipv6 else IPV4_APIS
    res = "❌ 无法获取"
    timeout = aiohttp.ClientTimeout(total=5)
    async with aiohttp.ClientSession(timeout=timeout) as s:
        for url in apis:
            try:
                async with s.get(url) as r:
                    if r.status == 200:
                        ip = (await r.text()).strip()
                        # 反引号内的内容不需要转义
                        res = f"`{ip}`"
                        break
            except Exception:
                continue
    return res


def get_package_file_path(filename):
    """获取安装目录下的文件绝对路径"""
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(pkg_dir, filename)
