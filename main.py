"""
Main entry point — runs the Telegram bot AND the FastAPI server
in a single asyncio process so they can share the Bot instance.
"""

import asyncio
import logging
import uvicorn

from aiogram import Bot, Dispatcher
from config import BOT_TOKEN, API_PORT
from database import init_db
from handlers.client import router as client_router
from handlers.admin import router as admin_router
import app_state


async def start_bot(dp: Dispatcher, bot_instance: Bot):
    """Run the bot polling loop."""
    logging.info("Starting Telegram bot polling...")
    await dp.start_polling(bot_instance)


async def start_api():
    """Run the FastAPI server via uvicorn."""
    logging.info(f"Starting API server on port {API_PORT}...")
    config = uvicorn.Config(
        "api:app",
        host="0.0.0.0",
        port=API_PORT,
        log_level="info",
    )
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    # Initialize database
    await init_db()

    # Initialize bot and dispatcher
    bot = Bot(token=BOT_TOKEN)
    app_state.set_bot(bot)
    dp = Dispatcher()

    # Include routers (admin first so /admin takes priority)
    dp.include_router(admin_router)
    dp.include_router(client_router)

    # Run bot polling and API concurrently
    await asyncio.gather(
        start_bot(dp, bot),
        start_api(),
    )


if __name__ == "__main__":
    asyncio.run(main())
