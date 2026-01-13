# -*- coding: utf-8 -*-
import functools
from .utils import logger, reply_message_safely
from .config import PermissionHelper


def authorized_only(func):
    """装饰器：检查用户是否有权限，并记录所有请求状态"""
    @functools.wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        if not update.effective_user:
            return
        user = update.effective_user
        content = update.message.text if update.message and update.message.text else "Interaction"
        is_allowed = PermissionHelper().is_allowed(user.id)
        status = "✅ AUTHORIZED" if is_allowed else "⛔ UNAUTHORIZED"
        logger.info(
            f"[{status}] User: {user.name}({user.id}) | Action: {func.__name__} | Content: {content}")
        if not is_allowed:
            await reply_message_safely(update, '⚠️ 警告: 你没有访问权限！')
            return
        return await func(update, context, *args, **kwargs)
    return wrapper
