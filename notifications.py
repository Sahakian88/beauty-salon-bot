"""
Admin notification helpers.
Sends formatted Telegram messages to the admin when bookings are created or cancelled.
"""

import json
import logging
from aiogram import Bot
from config import ADMIN_ID
import database

logger = logging.getLogger(__name__)


async def notify_admin_new_booking(bot: Bot, booking_data: dict):
    """
    Send a rich notification to the admin about a new booking.

    booking_data should contain: service_ids, date, time, name, phone, comments, total_duration
    """
    if not ADMIN_ID:
        logger.warning("ADMIN_ID not set — skipping booking notification.")
        return

    try:
        # Resolve service names
        service_ids = booking_data.get("service_ids", [])
        if isinstance(service_ids, str):
            service_ids = json.loads(service_ids)

        service_names = await database.get_service_names_by_ids(service_ids)
        services_text = "\n".join(f"  • {name}" for name in service_names) or "  • (unknown)"

        date = booking_data.get("date", "—")
        time = booking_data.get("time", "—")
        duration = booking_data.get("total_duration", 0)
        name = booking_data.get("name", "—")
        phone = booking_data.get("phone", "—")
        comments = booking_data.get("comments", "")

        duration_text = f"{duration} min" if duration else ""

        text = (
            "🆕 <b>New Booking!</b>\n\n"
            f"👤 <b>{name}</b>\n"
            f"📞 {phone}\n\n"
            f"💅 <b>Services:</b>\n{services_text}\n\n"
            f"📅 {date}  🕐 {time}"
        )
        if duration_text:
            text += f"  ({duration_text})"
        if comments:
            text += f"\n\n💬 <i>{comments}</i>"

        await bot.send_message(ADMIN_ID, text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Failed to send admin notification: {e}")


async def notify_admin_cancellation(bot: Bot, appointment: dict, cancelled_by: str = "admin"):
    """Notify admin about an appointment cancellation."""
    if not ADMIN_ID:
        return

    try:
        service_ids = appointment.get("service_ids", "[]")
        if isinstance(service_ids, str):
            service_ids = json.loads(service_ids)
        service_names = await database.get_service_names_by_ids(service_ids)
        services_text = ", ".join(service_names) or "(unknown)"

        text = (
            "❌ <b>Appointment Cancelled</b>\n\n"
            f"👤 {appointment.get('client_name', '—')}\n"
            f"📅 {appointment.get('appointment_date', '—')} at {appointment.get('appointment_time', '—')}\n"
            f"💅 {services_text}\n"
            f"🔹 Cancelled by: {cancelled_by}"
        )
        await bot.send_message(ADMIN_ID, text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Failed to send cancellation notification: {e}")


async def notify_client_cancellation(bot: Bot, appointment: dict):
    """Notify the client that their appointment has been cancelled by the admin."""
    user_id = appointment.get("user_id")
    if not user_id:
        return

    try:
        text = (
            "❌ <b>Appointment Cancelled</b>\n\n"
            f"Your appointment on <b>{appointment.get('appointment_date', '—')}</b> "
            f"at <b>{appointment.get('appointment_time', '—')}</b> has been cancelled.\n\n"
            "Please contact us to reschedule."
        )
        await bot.send_message(user_id, text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Failed to notify client of cancellation: {e}")
