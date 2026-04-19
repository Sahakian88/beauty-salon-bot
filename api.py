"""
FastAPI backend for the Beauty Salon Booking Mini-App.

When run via main.py, runs alongside the Telegram bot in one process.
Standalone:  uvicorn api:app --port 8000 --reload
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import database
from config import ADMIN_ID

logger = logging.getLogger(__name__)


# ── Lifespan (init DB on startup) ────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.init_db()
    
    yield


app = FastAPI(title="Beauty Salon API", lifespan=lifespan)

# ── CORS — allow Vite dev server & Telegram WebApp ──────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Schemas ──────────────────────────────────────────────────

class BookingRequest(BaseModel):
    service_ids: list[int]
    date: str           # YYYY-MM-DD
    time: str           # HH:MM
    name: str
    phone: str
    comments: str = ""
    telegram_user_id: int | None = None


# ── Endpoints ────────────────────────────────────────────────

@app.get("/api/categories")
async def list_categories():
    return await database.get_categories()


@app.get("/api/services")
async def list_services(category_id: int | None = None):
    return await database.get_services(category_id)


@app.get("/api/slots")
async def available_slots(
    date: str,
    service_ids: str = Query(default="", description="Comma-separated service IDs, e.g. '1,3'"),
):
    """
    Return available time slots for the given date, considering the total
    duration of the selected services.
    """
    parsed_service_ids = []
    if service_ids:
        try:
            parsed_service_ids = [int(x.strip()) for x in service_ids.split(",") if x.strip()]
        except ValueError:
            pass

    total_duration = await database.get_services_duration(parsed_service_ids)
    slots = await database.get_available_slots(date, total_duration)
    return slots


@app.get("/api/slots/month")
async def month_availability(
    year: int,
    month: int,
    service_ids: str = Query(default="", description="Comma-separated service IDs"),
):
    """
    Returns a dictionary of dates with 'morning' and 'afternoon' booleans
    to power the dot indicators on the calendar.
    """
    parsed_service_ids = []
    if service_ids:
        try:
            parsed_service_ids = [int(x.strip()) for x in service_ids.split(",") if x.strip()]
        except ValueError:
            pass

    total_duration = await database.get_services_duration(parsed_service_ids)
    availability = await database.get_month_availability(year, month, total_duration)
    return availability


@app.post("/api/bookings")
async def create_booking(req: BookingRequest):
    if not req.service_ids:
        raise HTTPException(status_code=400, detail="At least one service is required.")
        
    # Calculate total duration
    total_duration = await database.get_services_duration(req.service_ids)

    # Check the slot range is still free
    slots_data = await database.get_available_slots(req.date, total_duration)
    available_times = [s["time"] for s in slots_data if s["available"]]
    
    if req.time not in available_times:
        raise HTTPException(
            status_code=409,
            detail="This time slot is no longer available for the selected services duration."
        )

    await database.add_appointment_full(
        service_ids=req.service_ids,
        date=req.date,
        time=req.time,
        total_duration=total_duration,
        client_name=req.name,
        client_phone=req.phone,
        comments=req.comments,
        telegram_user_id=req.telegram_user_id,
    )

    # ── Send admin notification ─────────────────────────────
    try:
        from app_state import get_bot
        from notifications import notify_admin_new_booking
        bot = get_bot()
        await notify_admin_new_booking(bot, {
            "service_ids": req.service_ids,
            "date": req.date,
            "time": req.time,
            "total_duration": total_duration,
            "name": req.name,
            "phone": req.phone,
            "comments": req.comments,
        })
    except Exception as e:
        # Don't fail the booking if notification fails
        logger.warning(f"Could not send admin notification: {e}")

    return {"ok": True, "message": "Appointment booked successfully!"}


# ── Appointments endpoints ───────────────────────────────────

@app.get("/api/appointments")
async def list_appointments(user_id: int | None = None):
    """List upcoming appointments, optionally filtered by user_id."""
    if user_id:
        return await database.get_user_appointments(user_id)
    return []


@app.patch("/api/bookings/{appointment_id}/cancel")
async def cancel_booking(appointment_id: int):
    """Cancel an appointment by ID."""
    appointment = await database.get_appointment_by_id(appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found.")
    
    success = await database.cancel_appointment(appointment_id)
    if not success:
        raise HTTPException(status_code=409, detail="Appointment is already cancelled.")
    
    # Notify admin about the cancellation
    try:
        from app_state import get_bot
        from notifications import notify_admin_cancellation
        bot = get_bot()
        await notify_admin_cancellation(bot, appointment, cancelled_by="client (via API)")
    except Exception as e:
        logger.warning(f"Could not send cancellation notification: {e}")

    return {"ok": True, "message": "Appointment cancelled."}


@app.get("/api/bookings/{appointment_id}")
async def get_booking(appointment_id: int):
    """Get booking details by ID."""
    appointment = await database.get_appointment_by_id(appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found.")
    return appointment


@app.get("/api/config")
async def get_config():
    """Return app configuration for the frontend (e.g., admin ID for conditional UI)."""
    return {"admin_id": ADMIN_ID}


@app.get("/api/schedule/{date}")
async def get_schedule(date: str):
    """Return all appointments for a given date (admin use)."""
    appointments = await database.get_schedule_for_date(date)
    # Enrich with service names
    for apt in appointments:
        service_ids = apt.get("service_ids", "[]")
        if isinstance(service_ids, str):
            import json
            service_ids = json.loads(service_ids)
        apt["service_names"] = await database.get_service_names_by_ids(service_ids)
    return appointments
