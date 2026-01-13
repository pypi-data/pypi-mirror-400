#!/usr/bin/python3
# -*- coding: utf-8 -*-

from __future__ import annotations

__all__ = ['AioCaptchaMiddleware']

# Import modules
from typing import Any, Awaitable, Callable, Dict, Protocol
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject, Update


class _CaptchaManager(Protocol):
    def is_captcha_callback(self, cq: CallbackQuery) -> bool: ...

    def is_verified(self, user_id: int) -> bool: ...

    async def send_captcha(self, bot: Any, chat_id: int, user_id: int) -> int: ...


class AioCaptchaMiddleware(BaseMiddleware):
    """
    Blocks updates from non-verified users and forces them through emoji captcha.

    Minimal behavior:
    - If user isn't verified: send captcha and stop further handling.
    - Captcha callbacks always pass through (and should be handled by captcha router).
    """

    def __init__(self, manager: _CaptchaManager) -> None:
        self.manager = manager

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # If middleware is attached at dp.update.middleware(...), event is Update.
        if isinstance(event, Update):
            cq = event.callback_query
            if cq is not None and self.manager.is_captcha_callback(cq):
                return await handler(event, data)

            inner = (
                event.message
                or event.edited_message
                or event.callback_query
                or event.inline_query
                or event.chosen_inline_result
                or event.shipping_query
                or event.pre_checkout_query
                or event.poll_answer
                or event.chat_join_request
                or event.my_chat_member
                or event.chat_member
            )
            user = getattr(inner, "from_user", None)
            if user is None:
                return await handler(event, data)

            if self.manager.is_verified(user.id):
                return await handler(event, data)

            chat_id: int | None = None
            if isinstance(inner, Message):
                chat_id = inner.chat.id
            elif isinstance(inner, CallbackQuery):
                if inner.message is not None:
                    chat_id = inner.message.chat.id
            else:
                chat = getattr(inner, "chat", None)
                if chat is not None and hasattr(chat, "id"):
                    chat_id = chat.id

            bot = getattr(inner, "bot", None) or getattr(event, "bot", None) or data.get("bot")
            if chat_id is not None and bot is not None:
                await self.manager.send_captcha(bot=bot, chat_id=chat_id, user_id=user.id)

            if cq is not None:
                await cq.answer()

            return None

        # Let captcha callback reach its handler.
        if isinstance(event, CallbackQuery) and self.manager.is_captcha_callback(event):
            return await handler(event, data)

        user = getattr(event, "from_user", None)
        if user is None:
            return await handler(event, data)

        if self.manager.is_verified(user.id):
            return await handler(event, data)

        chat_id: int | None = None
        if isinstance(event, Message):
            chat_id = event.chat.id
        elif isinstance(event, CallbackQuery):
            if event.message is not None:
                chat_id = event.message.chat.id
        else:
            # Best-effort for other TelegramObject types
            msg = getattr(event, "message", None)
            chat = getattr(event, "chat", None)
            if msg is not None and hasattr(msg, "chat"):
                chat_id = msg.chat.id
            elif chat is not None and hasattr(chat, "id"):
                chat_id = chat.id

        if chat_id is not None:
            await self.manager.send_captcha(
                bot=event.bot,
                chat_id=chat_id,
                user_id=user.id,
            )

        # Prevent client "loading" spinner on button clicks.
        if isinstance(event, CallbackQuery):
            await event.answer()

        # Block any further handlers until captcha is passed.
        return None
