import os
import asyncpg
import ssl
import json
import logging
from datetime import datetime
import calendar

logger = logging.getLogger(__name__)

# Will be initialized in init_db
pool = None

async def init_db():
    global pool
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        logger.error("DATABASE_URL environment variable is missing! DB not initialized.")
        return

    # Mask password for safe logging
    masked = DATABASE_URL
    try:
        at_idx = DATABASE_URL.index("@")
        colon_idx = DATABASE_URL.index(":", DATABASE_URL.index("//") + 2)
        masked = DATABASE_URL[:colon_idx+1] + "****" + DATABASE_URL[at_idx:]
    except Exception:
        pass
    logger.info(f"Connecting to database: {masked}")

    try:
        # Create SSL context for Supabase (required for pooler connections)
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE

        pool = await asyncpg.create_pool(
            DATABASE_URL,
            ssl=ssl_ctx,
            timeout=10,
            command_timeout=10,
            min_size=1,
            max_size=5,
        )
        logger.info("Database connection pool created successfully!")
    except Exception as e:
        logger.error(f"Failed to connect to database: {type(e).__name__}: {e}")
        raise

    async with pool.acquire() as db:
        # ── Core tables ──────────────────────────────────────
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                phone TEXT
            )
        ''')

        await db.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                category_id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                emoji TEXT NOT NULL DEFAULT ''
            )
        ''')

        await db.execute('''
            CREATE TABLE IF NOT EXISTS services (
                service_id SERIAL PRIMARY KEY,
                category_id INTEGER,
                name TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                price INTEGER NOT NULL,
                duration INTEGER NOT NULL,
                duration_text TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (category_id) REFERENCES categories (category_id)
            )
        ''')

        await db.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                appointment_id SERIAL PRIMARY KEY,
                user_id BIGINT,
                service_ids TEXT NOT NULL,
                appointment_date TEXT,
                appointment_time TEXT,
                total_duration INTEGER NOT NULL DEFAULT 30,
                client_name TEXT,
                client_phone TEXT,
                comments TEXT DEFAULT '',
                status TEXT DEFAULT 'BOOKED',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        # ── Seed categories ──────────────────────────────────
        count = await db.fetchval("SELECT COUNT(*) FROM categories")
        if count == 0:
            await db.executemany(
                "INSERT INTO categories (name, emoji) VALUES ($1, $2)",
                [
                    ("Մանիկյուր (Manicure)", "💅"),
                    ("Պեդիկյուր (Pedicure)", "🦶"),
                ]
            )

        # ── Seed services ────────────────────────────────────
        count = await db.fetchval("SELECT COUNT(*) FROM services")
        if count == 0:
            cats = {}
            rows = await db.fetch("SELECT category_id, name FROM categories")
            for row in rows:
                if "Manicure" in row['name']:
                    cats["Manicure"] = row['category_id']
                else:
                    cats["Pedicure"] = row['category_id']

            demo_services = [
                # Manicure Category
                (cats["Manicure"], "Շելլակ մանիկյուր", "Basic shellac manicure", 6000, 60, "1h"),
                (cats["Manicure"], "Շելլակ մանիկյուր, ամրացումով", "Shellac manicure with reinforcement", 8000, 90, "1h 30m"),
                (cats["Manicure"], "Լիցք", "Nail extensions", 10000, 120, "2h"),
                (cats["Manicure"], "Չիստկա", "Cleaning", 3000, 30, "30m"),
                (cats["Manicure"], "Դիզայն", "Design", 1000, 15, "15m"),
                (cats["Manicure"], "Եղունգի վերականգնում (1 հատ)", "Nail repair (1 piece)", 1000, 15, "15m"),
                
                # Pedicure Category
                (cats["Pedicure"], "Շելլակ պեդիկյուր կրունկով", "Shellac pedicure with heel care", 10000, 90, "1h 30m"),
                (cats["Pedicure"], "Շելլակ պեդիկյուր առանց կրունկ", "Shellac pedicure without heel care", 7000, 60, "1h"),
                (cats["Pedicure"], "Պեդիկյուր չիստկա + կրունկ", "Pedicure cleaning + heel", 8000, 60, "1h"),
                (cats["Pedicure"], "Բորբոքված, ներաճած եղունքի բուժում", "Ingrown/inflamed nail treatment", 10000, 45, "45m"),
                (cats["Pedicure"], "Ներաճած եղունգի բուժում(սկոբա)", "Ingrown nail treatment (brace)", 18000, 60, "1h"),
                (cats["Pedicure"], "Ոտքերի սնկային բուժում", "Foot fungal treatment", 10000, 60, "1h"),
            ]
            await db.executemany(
                "INSERT INTO services (category_id, name, description, price, duration, duration_text) VALUES ($1, $2, $3, $4, $5, $6)",
                demo_services
            )


# ── Query helpers (used by API) ───────────────────────────────

async def get_categories():
    async with pool.acquire() as db:
        rows = await db.fetch("SELECT category_id, name, emoji FROM categories ORDER BY category_id")
        return [dict(r) for r in rows]


async def get_services(category_id: int | None = None):
    async with pool.acquire() as db:
        if category_id is not None:
            query = "SELECT service_id, category_id, name, description, price, duration, duration_text FROM services WHERE category_id = $1 ORDER BY service_id"
            rows = await db.fetch(query, category_id)
        else:
            query = "SELECT service_id, category_id, name, description, price, duration, duration_text FROM services ORDER BY service_id"
            rows = await db.fetch(query)
        return [dict(r) for r in rows]


async def get_services_duration(service_ids: list[int]) -> int:
    """Return total duration in minutes for a list of service IDs."""
    if not service_ids:
        return 0
    async with pool.acquire() as db:
        query = "SELECT COALESCE(SUM(duration), 0) FROM services WHERE service_id = ANY($1::int[])"
        val = await db.fetchval(query, service_ids)
        return val


async def get_bookings_for_date(date: str) -> list[dict]:
    """Return all booked appointments for a date with their time and total_duration."""
    async with pool.acquire() as db:
        rows = await db.fetch(
            "SELECT appointment_time, total_duration FROM appointments WHERE appointment_date = $1 AND status = 'BOOKED'",
            date
        )
        return [dict(r) for r in rows]


async def add_appointment_full(
    service_ids: list[int],
    date: str,
    time: str,
    total_duration: int,
    client_name: str,
    client_phone: str,
    comments: str = "",
    telegram_user_id: int | None = None,
):
    async with pool.acquire() as db:
        await db.execute(
            """INSERT INTO appointments
               (user_id, service_ids, appointment_date, appointment_time, total_duration, client_name, client_phone, comments, status)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'BOOKED')""",
            telegram_user_id,
            json.dumps(service_ids),
            date,
            time,
            total_duration,
            client_name,
            client_phone,
            comments,
        )


# ── Slot availability logic ──────────────────────────────────

def _time_to_minutes(t: str) -> int:
    """Convert 'HH:MM' to minutes since midnight."""
    h, m = t.split(":")
    return int(h) * 60 + int(m)


def _minutes_to_time(mins: int) -> str:
    """Convert minutes since midnight to 'HH:MM'."""
    return f"{mins // 60:02d}:{mins % 60:02d}"


# Working hours: 09:00 – 19:00, slots every 30 min
WORK_START = 9 * 60   # 540
WORK_END = 19 * 60    # 1140

ALL_SLOT_MINUTES = list(range(WORK_START, WORK_END + 1, 30))  # 09:00 .. 19:00


async def get_available_slots(date: str, needed_duration: int) -> list[dict]:
    """
    Return all possible slots for the day with an 'available' boolean.
    Slots that are already in the past (if date is today) are omitted entirely.
    """
    bookings = await get_bookings_for_date(date)

    # Build set of all occupied minutes
    occupied = set()
    for b in bookings:
        start = _time_to_minutes(b["appointment_time"])
        dur = b["total_duration"]
        for m in range(start, start + dur):
            occupied.add(m)

    # Determine current time to filter past slots if 'date' is today
    now = datetime.now()
    is_today = (date == now.strftime("%Y-%m-%d"))
    current_minutes = now.hour * 60 + now.minute

    slots_data = []
    for slot_min in ALL_SLOT_MINUTES:
        # Hide past slots completely
        if is_today and slot_min <= current_minutes:
            continue
            
        end_min = slot_min + needed_duration
        is_available = True
        
        if end_min > WORK_END:
            # Appointment would run past closing time
            is_available = False
        else:
            # Check no overlap with any occupied minute
            for m in range(slot_min, end_min):
                if m in occupied:
                    is_available = False
                    break
                    
        slots_data.append({
            "time": _minutes_to_time(slot_min),
            "available": is_available
        })

    return slots_data


async def get_month_availability(year: int, month: int, needed_duration: int) -> dict:
    """
    Calculate morning/afternoon availability for every day in the given month.
    """
    num_days = calendar.monthrange(year, month)[1]
    result = {}
    
    for day in range(1, num_days + 1):
        date_str = f"{year}-{month:02d}-{day:02d}"
        slots = await get_available_slots(date_str, needed_duration)
        
        has_morning = False
        has_afternoon = False
        
        for slot in slots:
            if slot["available"]:
                hour = int(slot["time"].split(":")[0])
                if hour < 12:
                    has_morning = True
                else:
                    has_afternoon = True
                
                # short-circuit if both are true
                if has_morning and has_afternoon:
                    break
                    
        result[date_str] = {
            "morning": has_morning,
            "afternoon": has_afternoon
        }
        
    return result


# ── Legacy helpers ────────────────────────────

async def add_user(user_id: int, username: str, full_name: str):
    async with pool.acquire() as db:
        await db.execute(
            """INSERT INTO users (user_id, username, full_name) 
               VALUES ($1, $2, $3) 
               ON CONFLICT (user_id) DO NOTHING""",
            user_id, username, full_name
        )


async def add_appointment(user_id: int, service_id: int, dt: str):
    """Legacy: used by the inline-keyboard bot flow."""
    async with pool.acquire() as db:
        await db.execute(
            "INSERT INTO appointments (user_id, service_ids, appointment_date, appointment_time, total_duration, status) VALUES ($1, $2, $3, $4, $5, $6)",
            user_id, f"[{service_id}]", dt.split(" ")[0] if " " in dt else dt, dt.split(" ")[1] if " " in dt else "", 30, "BOOKED"
        )


# ── New helpers (admin + client features) ─────────────────────

async def get_user_appointments(user_id: int) -> list[dict]:
    """Return upcoming BOOKED appointments for a specific user."""
    today = datetime.now().strftime("%Y-%m-%d")
    async with pool.acquire() as db:
        search_phone = f"%{user_id}%"
        rows = await db.fetch(
            """SELECT appointment_id, service_ids, appointment_date, appointment_time,
                      total_duration, client_name, client_phone, status
               FROM appointments
               WHERE (user_id = $1 OR client_phone LIKE $2)
                 AND status = 'BOOKED'
                 AND appointment_date >= $3
               ORDER BY appointment_date, appointment_time""",
            user_id, search_phone, today
        )
        return [dict(r) for r in rows]


async def get_schedule_for_date(date: str) -> list[dict]:
    """Return all appointments for a date with full details (for admin schedule view)."""
    async with pool.acquire() as db:
        rows = await db.fetch(
            """SELECT a.appointment_id, a.service_ids, a.appointment_date,
                      a.appointment_time, a.total_duration, a.client_name,
                      a.client_phone, a.comments, a.status, a.user_id
               FROM appointments a
               WHERE a.appointment_date = $1
                 AND a.status = 'BOOKED'
               ORDER BY a.appointment_time""",
            date
        )
        return [dict(r) for r in rows]


async def get_appointment_by_id(appointment_id: int) -> dict | None:
    """Return a single appointment by ID."""
    async with pool.acquire() as db:
        row = await db.fetchrow(
            """SELECT appointment_id, user_id, service_ids, appointment_date,
                      appointment_time, total_duration, client_name, client_phone,
                      comments, status
               FROM appointments WHERE appointment_id = $1""",
            appointment_id
        )
        return dict(row) if row else None


async def cancel_appointment(appointment_id: int) -> bool:
    """Set an appointment's status to CANCELLED. Returns True if a row was updated."""
    async with pool.acquire() as db:
        result = await db.execute(
            "UPDATE appointments SET status = 'CANCELLED' WHERE appointment_id = $1 AND status = 'BOOKED'",
            appointment_id
        )
        return result == "UPDATE 1"


async def search_clients(query: str) -> list[dict]:
    """Search clients by name or phone across users and appointments tables."""
    pattern = f"%{query}%"
    async with pool.acquire() as db:
        rows = await db.fetch(
            """SELECT DISTINCT
                      COALESCE(a.client_name, u.full_name) AS name,
                      COALESCE(a.client_phone, u.phone) AS phone,
                      u.user_id,
                      u.username,
                      (SELECT COUNT(*) FROM appointments a2
                       WHERE a2.user_id = u.user_id OR a2.client_phone = COALESCE(a.client_phone, u.phone)
                      ) AS total_bookings,
                      (SELECT MAX(appointment_date) FROM appointments a3
                       WHERE a3.user_id = u.user_id OR a3.client_phone = COALESCE(a.client_phone, u.phone)
                      ) AS last_visit
               FROM appointments a
               LEFT JOIN users u ON a.user_id = u.user_id
               WHERE a.client_name LIKE $1 OR a.client_phone LIKE $2
                  OR u.full_name LIKE $3 OR u.phone LIKE $4
               LIMIT 10""",
            pattern, pattern, pattern, pattern
        )
        return [dict(r) for r in rows]


async def get_service_names_by_ids(service_ids: list[int]) -> list[str]:
    """Return service names for a list of IDs."""
    if not service_ids:
        return []
    async with pool.acquire() as db:
        query = "SELECT name FROM services WHERE service_id = ANY($1::int[])"
        rows = await db.fetch(query, service_ids)
        return [r['name'] for r in rows]
