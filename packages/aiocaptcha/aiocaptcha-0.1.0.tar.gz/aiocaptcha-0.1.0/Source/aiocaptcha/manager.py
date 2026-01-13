#!/usr/bin/python3
# -*- coding: utf-8 -*-

from __future__ import annotations

__all__ = ['CaptchaOptions', 'CaptchaManager']

# Import modules
from logging import getLogger
from dataclasses import dataclass
from random import shuffle, choice
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Set, Tuple
from aiogram import Bot, Dispatcher
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
# Import packages
from .router import build_captcha_router
from .middleware import AioCaptchaMiddleware
from .storage import CaptchaStorage, MemoryCaptchaStorage


logger = getLogger("aiocaptcha")

@dataclass(frozen=True)
class CaptchaOptions:
    callback_prefix: str = "aiocaptcha"
    pool: Tuple[str, ...] = (
        "😀",
        "😎",
        "🥶",
        "🤖",
        "👻",
        "🐶",
        "🐱",
        "🐭",
        "🐼",
        "🦊",
        "🐻",
        "🐸",
        "🍎",
        "🍌",
        "🍉",
        "🍓",
        "🍕",
        "🍔",
        "🍟",
        "🍩",
        "⚽",
        "🏀",
        "🎲",
        "🎯",
    )
    choices: int = 4
    ttl_seconds: int = 120

    prompt_text: str = "Please verify you're human by clicking {target}"
    passed_text: str = "Captcha passed successfully! ✅"
    wrong_alert: str = "Incorrect choice. Please try again."


@dataclass
class _Challenge:
    target: str
    options: Tuple[str, ...]
    expires_at: datetime
    chat_id: Optional[int] = None
    message_id: Optional[int] = None


class CaptchaManager:
    def __init__(
        self,
        options: CaptchaOptions | None = None,
        storage: CaptchaStorage | None = None,
    ) -> None:
        self.options = options or CaptchaOptions()
        self._storage: CaptchaStorage = storage or MemoryCaptchaStorage()
        self._pending: Dict[int, _Challenge] = {}

    def setup(self, dp: Any) -> None:
        """Attach captcha middleware + handlers to a Dispatcher.

        After calling this, the bot will block any user interactions until captcha is passed.
        """
        if not isinstance(dp, Dispatcher):
            raise TypeError("dp must be an aiogram.Dispatcher")

        dp.update.middleware(AioCaptchaMiddleware(self))
        dp.include_router(build_captcha_router(self))

        logger.info("captcha_setup")

    def is_verified(self, user_id: int) -> bool:
        return self._storage.is_verified(user_id)

    def mark_verified(self, user_id: int) -> None:
        if self._storage.is_verified(user_id):
            return

        self._storage.mark_verified(user_id)
        self._pending.pop(user_id, None)

        logger.info("captcha_passed user_id=%s", user_id)

    def reset(self, user_id: int) -> None:
        self._storage.reset(user_id)
        self._pending.pop(user_id, None)

    def _now(self) -> datetime:
        return datetime.now(timezone.utc)

    def _make_challenge(self) -> _Challenge:
        pool = list(self.options.pool)
        if len(pool) < self.options.choices:
            raise ValueError("Captcha pool is smaller than choices")

        target = choice(pool)
        opts = set([target])
        while len(opts) < self.options.choices:
            opts.add(choice(pool))

        options = list(opts)
        shuffle(options)
        return _Challenge(
            target=target,
            options=tuple(options),
            expires_at=self._now() + timedelta(seconds=self.options.ttl_seconds),
        )

    def get_or_create_challenge(self, user_id: int) -> _Challenge:
        ch = self._pending.get(user_id)
        if ch is None or ch.expires_at <= self._now():
            ch = self._make_challenge()
            self._pending[user_id] = ch
        return ch

    def _kbd(self, ch: _Challenge) -> InlineKeyboardMarkup:
        prefix = self.options.callback_prefix
        buttons = [
            [InlineKeyboardButton(text=e, callback_data=f"{prefix}:{e}")]
            for e in ch.options
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    async def send_captcha(self, bot: Bot, chat_id: int, user_id: int) -> int:
        ch = self.get_or_create_challenge(user_id)

        # If we already sent a captcha message in this chat, try to update it.
        if ch.message_id is not None and ch.chat_id == chat_id:
            try:
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=ch.message_id,
                    text=self.options.prompt_text.format(target=ch.target),
                    reply_markup=self._kbd(ch),
                )

                logger.debug(
                    "captcha_edited user_id=%s chat_id=%s message_id=%s",
                    user_id,
                    chat_id,
                    ch.message_id,
                )
                return ch.message_id
            except Exception:
                # Message can be deleted/not editable; fall back to sending a new one.
                pass

        msg = await bot.send_message(
            chat_id=chat_id,
            text=self.options.prompt_text.format(target=ch.target),
            reply_markup=self._kbd(ch),
        )
        ch.chat_id = chat_id
        ch.message_id = msg.message_id
        self._pending[user_id] = ch

        logger.info(
            "captcha_sent user_id=%s chat_id=%s message_id=%s",
            user_id,
            chat_id,
            msg.message_id,
        )
        return msg.message_id

    def is_captcha_callback(self, cq: CallbackQuery) -> bool:
        data = cq.data or ""
        return data.startswith(self.options.callback_prefix + ":")

    def _parse_answer(self, cq: CallbackQuery) -> Optional[str]:
        data = cq.data or ""
        prefix = self.options.callback_prefix + ":"
        if not data.startswith(prefix):
            return None
        return data[len(prefix) :]

    async def handle_callback(self, cq: CallbackQuery) -> bool:
        """Returns True if callback was handled as captcha."""
        user = cq.from_user
        if user is None:
            return False

        user_id = user.id
        answer = self._parse_answer(cq)
        if answer is None:
            return False

        if self.is_verified(user_id):
            await cq.answer()
            return True

        ch = self.get_or_create_challenge(user_id)

        if answer == ch.target:
            self.mark_verified(user_id)
            try:
                if cq.message is not None:
                    await cq.message.edit_text(self.options.passed_text)
            except Exception:
                # message may be not editable; ignore
                pass
            await cq.answer()
            return True

        # Wrong answer -> regenerate challenge and update message
        logger.info(
            "captcha_failed user_id=%s answer=%s expected=%s",
            user_id,
            answer,
            ch.target,
        )
        self._pending[user_id] = self._make_challenge()
        new_ch = self._pending[user_id]

        try:
            if cq.message is not None:
                await cq.message.edit_text(
                    self.options.prompt_text.format(target=new_ch.target),
                    reply_markup=self._kbd(new_ch),
                )
        except Exception:
            pass

        await cq.answer(self.options.wrong_alert, show_alert=True)
        return True
