"""Client-facing keyboards."""

from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
)
from keyboards.callbacks import ServiceCallback, DateCallback, TimeCallback, CancelAppointmentCallback
from datetime import datetime, timedelta
from config import MINI_APP_URL


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Main reply keyboard with optional Mini-App booking button."""
    kb = []

    # If MINI_APP_URL is set, show a Web App button for booking
    if MINI_APP_URL:
        kb.append([KeyboardButton(
            text="📱 Book Online",
            web_app=WebAppInfo(url=MINI_APP_URL)
        )])

    kb.extend([
        [KeyboardButton(text="Book Appointment")],
        [KeyboardButton(text="My Appointments"), KeyboardButton(text="Services")],
        [KeyboardButton(text="Contacts")]
    ])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def get_services_keyboard(services: list) -> InlineKeyboardMarkup:
    kb = []
    for service in services:
        desc = f"{service['name']} - {service['price']}֏ ({service['duration']}m)"
        kb.append([InlineKeyboardButton(
            text=desc,
            callback_data=ServiceCallback(id=service['service_id'], name=service['name']).pack()
        )])
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_dates_keyboard() -> InlineKeyboardMarkup:
    kb = []
    today = datetime.now()
    for i in range(1, 6):  # next 5 days
        date_obj = today + timedelta(days=i)
        date_str = date_obj.strftime("%Y-%m-%d")
        kb.append([InlineKeyboardButton(
            text=date_obj.strftime("%d %b"),
            callback_data=DateCallback(date=date_str).pack()
        )])
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_times_keyboard() -> InlineKeyboardMarkup:
    kb = []
    # static times for demo
    times = ["10:00", "12:00", "14:00", "16:00"]
    row = []
    for t in times:
        row.append(InlineKeyboardButton(
            text=t,
            callback_data=TimeCallback(time=t).pack()
        ))
        if len(row) == 2:
            kb.append(row)
            row = []
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_cancel_booking_keyboard(appointments: list[dict]) -> InlineKeyboardMarkup | None:
    """Build inline keyboard with cancel buttons for the user's appointments."""
    kb = []
    for apt in appointments:
        kb.append([InlineKeyboardButton(
            text=f"❌ Cancel: {apt['appointment_date']} at {apt['appointment_time']}",
            callback_data=CancelAppointmentCallback(id=apt['appointment_id']).pack()
        )])
    return InlineKeyboardMarkup(inline_keyboard=kb) if kb else None
