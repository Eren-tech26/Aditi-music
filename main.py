import asyncio
from pyrogram import Client
from pytgcalls import PyTgCalls
from config import API_ID, API_HASH, BOT_TOKEN, SESSION_STRING
import commands

# Bot client (handles commands)
app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Userbot client (joins VC)
user = Client("user", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# PyTgCalls on userbot
call_py = PyTgCalls(user)

async def main():
    commands.set_call(call_py)
    commands.register(app)

    await user.start()
    await call_py.start()
    await app.start()

    print("✅ Aditi Music Bot is running!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
