# Beauty Salon Booking Bot

This is a Telegram bot for booking appointments for a manicurist, built with `aiogram 3.x` and `aiosqlite`.

## Setup Instructions

1. **Create and activate a virtual environment** (Windows):
   ```cmd
   python -m venv venv
   .\venv\Scripts\activate
   ```
   *(On macOS/Linux, use `python3 -m venv venv` and `source venv/bin/activate`)*

2. **Install dependencies**:
   ```cmd
   pip install -r requirements.txt
   ```
   *(If you don't use a virtual environment and `pip` is not recognized, use `python -m pip install -r requirements.txt`)*

3. **Configure Environment Variables**:
   Open the `.env` file in the root directory and set your `BOT_TOKEN`:
   ```env
   BOT_TOKEN=your_actual_token_here
   ```
   You can get this token from [@BotFather](https://t.me/BotFather) on Telegram.

3. **Run the Bot**:
   ```cmd
   python main.py
   ```

The bot will automatically initialize the SQLite database `bot_database.db` upon its first run.
