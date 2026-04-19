import json
from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    WebAppInfo, MenuButtonWebApp
)
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.callbacks import CancelAppointmentCallback
import database
from config import MINI_APP_URL

router = Router()


class BookingState(StatesGroup):
    choosing_service = State()
    choosing_date = State()
    choosing_time = State()


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


# ── Inline booking flow (legacy) ────────────────────────────────

@router.message(F.text == "Book Appointment")
async def start_booking(message: Message, state: FSMContext):
    services = await database.get_services()
    if not services:
        await message.answer("Sorry, no services are currently available.")
        return

    await message.answer(
        "Please select a service:",
        reply_markup=get_services_keyboard(services)
    )
    await state.set_state(BookingState.choosing_service)


@router.callback_query(ServiceCallback.filter(), BookingState.choosing_service)
async def process_service(callback: CallbackQuery, callback_data: ServiceCallback, state: FSMContext):
    await state.update_data(service_id=callback_data.id, service_name=callback_data.name)
    await callback.message.edit_text(
        f"You selected {callback_data.name}. Now choose a date:",
        reply_markup=get_dates_keyboard()
    )
    await state.set_state(BookingState.choosing_date)


@router.callback_query(DateCallback.filter(), BookingState.choosing_date)
async def process_date(callback: CallbackQuery, callback_data: DateCallback, state: FSMContext):
    await state.update_data(date=callback_data.date)
    await callback.message.edit_text(
        f"Date {callback_data.date} selected. Now choose a time:",
        reply_markup=get_times_keyboard()
    )
    await state.set_state(BookingState.choosing_time)


@router.callback_query(TimeCallback.filter(), BookingState.choosing_time)
async def process_time(callback: CallbackQuery, callback_data: TimeCallback, state: FSMContext):
    data = await state.get_data()
    date_str = f"{data['date']} {callback_data.time}"

    await database.add_appointment(
        user_id=callback.from_user.id,
        service_id=data['service_id'],
        dt=date_str
    )

    await callback.message.edit_text(
        f"🎉 Appointment confirmed for {data['service_name']} on {date_str}!"
    )
    await state.clear()


# ── "My Appointments" ────────────────────────────────────────────

@router.message(F.text == "My Appointments")
async def my_appointments(message: Message):
    appointments = await database.get_user_appointments(message.from_user.id)

    if not appointments:
        await message.answer(
            "📋 You have no upcoming appointments.\n\n"
            "Use the booking menu to schedule one!"
        )
        return

    lines = [f"📋 <b>Your Upcoming Appointments</b> ({len(appointments)})\n"]
    for apt in appointments:
        service_ids = apt.get("service_ids", "[]")
        if isinstance(service_ids, str):
            service_ids = json.loads(service_ids)
        service_names = await database.get_service_names_by_ids(service_ids)
        services_text = ", ".join(service_names) or "—"

        lines.append(
            f"📅 <b>{apt['appointment_date']}</b> at <b>{apt['appointment_time']}</b>\n"
            f"   💅 {services_text}\n"
        )

    await message.answer(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=get_cancel_booking_keyboard(appointments)
    )


# ── Cancel own appointment (client) ─────────────────────────────

@router.callback_query(CancelAppointmentCallback.filter())
async def client_cancel_appointment(callback: CallbackQuery, callback_data: CancelAppointmentCallback):
    appointment = await database.get_appointment_by_id(callback_data.id)

    if not appointment:
        await callback.answer("Appointment not found.", show_alert=True)
        return

    # Only allow cancelling own appointments
    if appointment.get("user_id") != callback.from_user.id:
        await callback.answer("You can only cancel your own appointments.", show_alert=True)
        return

    success = await database.cancel_appointment(callback_data.id)
    if success:
        await callback.answer("✅ Appointment cancelled.", show_alert=True)
        # Refresh the list
        await my_appointments(callback.message)
    else:
        await callback.answer("Could not cancel this appointment.", show_alert=True)


# ── "Services" ───────────────────────────────────────────────────

@router.message(F.text == "Services")
async def show_services(message: Message):
    categories = await database.get_categories()
    all_services = await database.get_services()

    if not all_services:
        await message.answer("No services available at the moment.")
        return

    lines = ["💅 <b>Our Services</b>\n"]
    for cat in categories:
        cat_services = [s for s in all_services if s["category_id"] == cat["category_id"]]
        if not cat_services:
            continue

        lines.append(f"\n{cat.get('emoji', '')} <b>{cat['name']}</b>")
        for svc in cat_services:
            duration_text = svc.get("duration_text") or f"{svc['duration']}m"
            lines.append(
                f"  • {svc['name']} — {svc['price']} ֏ ({duration_text})"
            )

    lines.append("\n\nUse the booking menu to book an appointment! 🗓")
    await message.answer("\n".join(lines), parse_mode="HTML")


# ── "Contacts" ───────────────────────────────────────────────────

@router.message(F.text == "Contacts")
async def show_contacts(message: Message):
    await message.answer(
        "📍 <b>Beauty Studio</b>\n\n"
        "🏠 14 Tumanyan St, Yerevan, Armenia\n"
        "📞 +374 XX XXX XXX\n"
        "🕐 Mon–Sat: 09:00 – 19:00\n"
        "🚫 Sunday: Closed\n\n"
        "💬 Have questions? Just send a message here!",
        parse_mode="HTML"
    )
