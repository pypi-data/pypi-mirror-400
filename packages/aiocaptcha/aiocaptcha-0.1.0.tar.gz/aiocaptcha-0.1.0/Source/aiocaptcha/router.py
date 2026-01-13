#!/usr/bin/python3
# -*- coding: utf-8 -*-

from __future__ import annotations

__all__ = ['build_captcha_router']

# Import modules
from typing import Protocol
from aiogram import Router
from aiogram.types import CallbackQuery


class _CaptchaManager(Protocol):
    def is_captcha_callback(self, cq: CallbackQuery) -> bool: ...

    async def handle_callback(self, cq: CallbackQuery) -> bool: ...


def build_captcha_router(manager: _CaptchaManager) -> Router:
    router = Router(name="aiocaptcha")

    @router.callback_query(lambda cq: manager.is_captcha_callback(cq))
    async def _captcha_callback(cq: CallbackQuery) -> None:
        await manager.handle_callback(cq)

    return router
