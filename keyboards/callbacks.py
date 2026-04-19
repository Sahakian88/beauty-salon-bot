from aiogram.filters.callback_data import CallbackData

class ServiceCallback(CallbackData, prefix="service"):
    id: int
    name: str

class DateCallback(CallbackData, prefix="date"):
    date: str

class TimeCallback(CallbackData, prefix="time"):
    time: str

class AdminMenuCallback(CallbackData, prefix="adm"):
    action: str  # "today", "tomorrow", "find_client"

class CancelAppointmentCallback(CallbackData, prefix="cancel_apt"):
    id: int

