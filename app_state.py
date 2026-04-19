"""
Shared application state — holds the Bot instance so it can be
accessed by both main.py and api.py without circular imports.
"""

from aiogram import Bot, Dispatcher

_bot: Bot | None = None
_dp: Dispatcher | None = None


def set_bot(bot: Bot):
    global _bot
    _bot = bot


def get_bot() -> Bot:
    if _bot is None:
        raise RuntimeError("Bot has not been initialized yet.")
    return _bot


def set_dp(dp: Dispatcher):
    global _dp
    _dp = dp


def get_dp() -> Dispatcher:
    if _dp is None:
        raise RuntimeError("Dispatcher has not been initialized yet.")
    return _dp
