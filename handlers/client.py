import json
from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    WebAppInfo, MenuButtonWebApp
)
from aiogram.filters import CommandStart

from keyboards.callbacks import CancelAppointmentCallback
import database
from config import MINI_APP_URL

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await database.add_user(message.from_user.id, message.from_user.username or "", message.from_user.full_name)

    # Set the persistent blue "Menu" button to open the mini-app
    if MINI_APP_URL:
        try:
            await message.bot.set_chat_menu_button(
                chat_id=message.chat.id,
                menu_button=MenuButtonWebApp(
                    text="📱 Записаться",
                    web_app=WebAppInfo(url=MINI_APP_URL)
                )
            )
        except Exception:
            pass  # Silently fail if menu button can't be set

    # Send welcome message with inline button fallback
    kb = None
    if MINI_APP_URL:
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text="📱 Записаться онлайн",
                web_app=WebAppInfo(url=MINI_APP_URL)
            )
        ]])

    await message.answer(
        f"Здравствуйте, {message.from_user.full_name}! 👋\n\n"
        "Добро пожаловать! Нажмите кнопку ниже, чтобы записаться на приём.",
        reply_markup=kb
    )
