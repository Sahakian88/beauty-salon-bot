"""
Admin handlers — restricted to ADMIN_ID.
Provides schedule viewing, client search, and appointment cancellation.
"""

import json
from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_ID
import database
from keyboards.admin import get_admin_menu_keyboard, get_schedule_keyboard
from keyboards.callbacks import AdminMenuCallback, CancelAppointmentCallback
from notifications import notify_admin_cancellation, notify_client_cancellation

router = Router()


# ── Guard: only allow the admin ─────────────────────────────────

def _is_admin(user_id: int) -> bool:
    return ADMIN_ID is not None and user_id == ADMIN_ID


class AdminStates(StatesGroup):
    waiting_for_search = State()


# ── /admin command ──────────────────────────────────────────────

@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    if not _is_admin(message.from_user.id):
        await message.answer("⛔ You are not authorized to use admin commands.")
        return

    await state.clear()
    await message.answer(
        "🔧 <b>Admin Panel</b>\n\nWhat would you like to do?",
        parse_mode="HTML",
        reply_markup=get_admin_menu_keyboard()
    )


# ── Schedule callbacks ──────────────────────────────────────────

async def _send_schedule(callback: CallbackQuery, date: datetime, label: str):
    """Format and send the schedule for a given date."""
    date_str = date.strftime("%Y-%m-%d")
    appointments = await database.get_schedule_for_date(date_str)

    if not appointments:
        await callback.message.edit_text(
            f"📅 <b>{label}</b> ({date.strftime('%d %B')})\n\n"
            "No appointments scheduled.",
            parse_mode="HTML",
            reply_markup=get_admin_menu_keyboard()
        )
        return

    lines = [f"📅 <b>{label}</b> ({date.strftime('%d %B')}) — {len(appointments)} appointment(s)\n"]
    for i, apt in enumerate(appointments, 1):
        service_ids = apt.get("service_ids", "[]")
        if isinstance(service_ids, str):
            service_ids = json.loads(service_ids)
        service_names = await database.get_service_names_by_ids(service_ids)
        services_text = ", ".join(service_names) or "—"

        end_time_min = _time_to_min(apt["appointment_time"]) + apt["total_duration"]
        end_time = f"{end_time_min // 60:02d}:{end_time_min % 60:02d}"

        lines.append(
            f"<b>{i}. {apt['appointment_time']} – {end_time}</b>\n"
            f"   👤 {apt.get('client_name', '—')} · 📞 {apt.get('client_phone', '—')}\n"
            f"   💅 {services_text}"
        )
        if apt.get("comments"):
            lines.append(f"   💬 <i>{apt['comments']}</i>")
        lines.append("")

    text = "\n".join(lines)
    cancel_kb = get_schedule_keyboard(appointments)

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=cancel_kb
    )


def _time_to_min(t: str) -> int:
    h, m = t.split(":")
    return int(h) * 60 + int(m)


@router.callback_query(AdminMenuCallback.filter(F.action == "today"))
async def admin_today(callback: CallbackQuery):
    if not _is_admin(callback.from_user.id):
        await callback.answer("⛔ Not authorized", show_alert=True)
        return
    await callback.answer()
    await _send_schedule(callback, datetime.now(), "Today's Schedule")


@router.callback_query(AdminMenuCallback.filter(F.action == "tomorrow"))
async def admin_tomorrow(callback: CallbackQuery):
    if not _is_admin(callback.from_user.id):
        await callback.answer("⛔ Not authorized", show_alert=True)
        return
    await callback.answer()
    await _send_schedule(callback, datetime.now() + timedelta(days=1), "Tomorrow's Schedule")


# ── Find client ─────────────────────────────────────────────────

@router.callback_query(AdminMenuCallback.filter(F.action == "find_client"))
async def admin_find_client_start(callback: CallbackQuery, state: FSMContext):
    if not _is_admin(callback.from_user.id):
        await callback.answer("⛔ Not authorized", show_alert=True)
        return
    await callback.answer()
    await callback.message.edit_text(
        "🔍 <b>Find Client</b>\n\nType a name or phone number to search:",
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.waiting_for_search)


@router.message(AdminStates.waiting_for_search)
async def admin_search_results(message: Message, state: FSMContext):
    if not _is_admin(message.from_user.id):
        return

    query = message.text.strip()
    if not query:
        await message.answer("Please enter a search term.")
        return

    results = await database.search_clients(query)
    await state.clear()

    if not results:
        await message.answer(
            f"🔍 No clients found for <b>'{query}'</b>.\n\nUse /admin to go back.",
            parse_mode="HTML"
        )
        return

    lines = [f"🔍 <b>Search results for '{query}'</b> ({len(results)} found)\n"]
    for r in results:
        name = r.get("name") or "—"
        phone = r.get("phone") or "—"
        total = r.get("total_bookings", 0)
        last = r.get("last_visit") or "—"
        lines.append(
            f"👤 <b>{name}</b>\n"
            f"   📞 {phone}\n"
            f"   📊 {total} booking(s) · Last: {last}\n"
        )

    lines.append("Use /admin to go back.")
    await message.answer("\n".join(lines), parse_mode="HTML")


# ── Cancel appointment ──────────────────────────────────────────

@router.callback_query(CancelAppointmentCallback.filter())
async def admin_cancel_appointment(callback: CallbackQuery, callback_data: CancelAppointmentCallback):
    if not _is_admin(callback.from_user.id):
        await callback.answer("⛔ Not authorized", show_alert=True)
        return

    appointment = await database.get_appointment_by_id(callback_data.id)
    if not appointment:
        await callback.answer("Appointment not found.", show_alert=True)
        return

    success = await database.cancel_appointment(callback_data.id)
    if success:
        await callback.answer("✅ Appointment cancelled.", show_alert=True)
        # Notify the client
        await notify_client_cancellation(callback.bot, appointment)
        # Refresh the schedule view
        date_str = appointment["appointment_date"]
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")
        label = "Today's Schedule" if date_str == today else "Schedule"
        await _send_schedule(callback, date_obj, label)
    else:
        await callback.answer("Could not cancel — may already be cancelled.", show_alert=True)
