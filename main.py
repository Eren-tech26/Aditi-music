import asyncio
from pyrogram import Client
from pytgcalls import PyTgCalls
from config import API_ID, API_HASH, BOT_TOKEN, SESSION_STRING
import commands
from aiohttp import web

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user = Client("user", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
call_py = PyTgCalls(user)

async def handle(request):
    return web.Response(text="Aditi Music Bot is running!")

async def main():
    commands.set_call(call_py)
    commands.register(app)
    await user.start()
    await call_py.start()
    await app.start()
    print("✅ Aditi Music Bot is running!")

    # fake web server so Render doesn't kill us
    server = web.Application()
    server.router.add_get("/", handle)
    runner = web.AppRunner(server)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()

    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
