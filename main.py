import asyncio
import os
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from aiohttp import web
import yt_dlp

API_ID = int(os.environ.get("API_ID", "26177051"))
API_HASH = os.environ.get("API_HASH", "f90dac56d2dd04adfef001e89a3acd67")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8407576273:AAEkmKPXW2re_wmVYkT5peaBuiqY-dYm3pM")
SESSION_STRING = os.environ.get("SESSION_STRING", "BQGPbhsAVqVkmfKWK_8FaERhc66CQ4koHbrCAzDg2TFk2JszkVtLvUQf06wr-I9n9USRh3CVP3-_FTkoXaiXNuRqCpbqjWYHF7VWNFB_udvXc9VAEUYQ_eJL3MTPYSq9PYys0ApCQuG2E5a_epK5B6kGgj8GODIskhmSskPs14DVcjS2WB3gTByxdHrTlFUSSjJixPQOP8Hqu3ctH12nVIwOsloFtjnWkaWw8lZplbwx8B5jmrm1pUeanlKeOiVfMoOtXdX7c1m7oYoXe-MOXfEyrljOoliX11X2J53QqAmgEipWtKGaR7S24w9_7MLoNF08bukLCUT4O3qbtEWW71Gp4iGHNgAAAAH1IW7RAQ")
OWNER_ID = int(os.environ.get("OWNER_ID", "7774827065"))

bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user = Client("user", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
call_py = PyTgCalls(user)
queues = {}

def get_url(query):
    opts = {"format": "bestaudio/best", "noplaylist": True, "quiet": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        q = query if query.startswith("http") else f"ytsearch1:{query}"
        info = ydl.extract_info(q, download=False)
        if "entries" in info:
            info = info["entries"][0]
        return info["title"], info["url"]

@bot.on_message(filters.command("play") & filters.group)
async def play(client, message):
    if len(message.command) < 2:
        return await message.reply("Usage: /play <song>")
    query = message.text.split(None, 1)[1]
    msg = await message.reply("🔎 Searching...")
    try:
        title, url = await asyncio.to_thread(get_url, query)
        chat_id = message.chat.id
        if chat_id not in queues:
            queues[chat_id] = []
        queues[chat_id].append((title, url))
        if len(queues[chat_id]) == 1:
            await call_py.play(chat_id, MediaStream(url))
            await msg.edit(f"🎶 Now playing: **{title}**")
        else:
            await msg.edit(f"📋 Added to queue: **{title}**")
    except Exception as e:
        await msg.edit(f"❌ Error: {e}")

@bot.on_message(filters.command("skip") & filters.group)
async def skip(client, message):
    chat_id = message.chat.id
    if chat_id in queues and queues[chat_id]:
        queues[chat_id].pop(0)
    if chat_id in queues and queues[chat_id]:
        title, url = queues[chat_id][0]
        await call_py.play(chat_id, MediaStream(url))
        await message.reply(f"⏭ Now playing: **{title}**")
    else:
        await call_py.leave_call(chat_id)
        await message.reply("⏭ Queue empty, left VC.")

@bot.on_message(filters.command("pause") & filters.group)
async def pause(client, message):
    await call_py.pause_stream(message.chat.id)
    await message.reply("⏸ Paused.")

@bot.on_message(filters.command("resume") & filters.group)
async def resume(client, message):
    await call_py.resume_stream(message.chat.id)
    await message.reply("▶️ Resumed.")

@bot.on_message(filters.command("stop") & filters.group)
async def stop(client, message):
    queues[message.chat.id] = []
    await call_py.leave_call(message.chat.id)
    await message.reply("⏹ Stopped.")

@bot.on_message(filters.command("help"))
async def help(client, message):
    await message.reply("🎵 **Aditi Music Bot**\n\n/play <song> — Play\n/skip — Skip\n/pause — Pause\n/resume — Resume\n/stop — Stop")

async def web_handler(request):
    return web.Response(text="Aditi Music Bot Running!")

async def main():
    await user.start()
    await call_py.start()
    await bot.start()
    print("✅ Aditi Music Bot is running!")
    server = web.Application()
    server.router.add_get("/", web_handler)
    runner = web.AppRunner(server)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
