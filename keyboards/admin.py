"""Admin-specific keyboards."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.callbacks import AdminMenuCallback, CancelAppointmentCallback


def get_admin_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📅 Today's schedule",
            callback_data=AdminMenuCallback(action="today").pack()
        )],
        [InlineKeyboardButton(
            text="📅 Tomorrow's schedule",
            callback_data=AdminMenuCallback(action="tomorrow").pack()
        )],
        [InlineKeyboardButton(
            text="🔍 Find client",
            callback_data=AdminMenuCallback(action="find_client").pack()
        )],
    ])


def get_schedule_keyboard(appointments: list[dict]) -> InlineKeyboardMarkup:
    """Build inline keyboard with cancel buttons for each appointment."""
    kb = []
    for apt in appointments:
        kb.append([InlineKeyboardButton(
            text=f"❌ Cancel: {apt['appointment_time']} — {apt.get('client_name', 'Unknown')}",
            callback_data=CancelAppointmentCallback(id=apt['appointment_id']).pack()
        )])
    return InlineKeyboardMarkup(inline_keyboard=kb) if kb else None
