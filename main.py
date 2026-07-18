import asyncio
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from aiohttp import web
import yt_dlp

logging.basicConfig(level=logging.INFO)

API_ID = int(os.environ.get("API_ID", "26177051"))
API_HASH = os.environ.get("API_HASH", "f90dac56d2dd04adfef001e89a3acd67")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8407576273:AAEkmKPXW2re_wmVYkT5peaBuiqY-dYm3pM")
SESSION_STRING = os.environ.get("SESSION_STRING", "BQGPbhsAVqVkmfKWK_8FaERhc66CQ4koHbrCAzDg2TFk2JszkVtLvUQf06wr-I9n9USRh3CVP3-_FTkoXaiXNuRqCpbqjWYHF7VWNFB_udvXc9VAEUYQ_eJL3MTPYSq9PYys0ApCQuG2E5a_epK5B6kGgj8GODIskhmSskPs14DVcjS2WB3gTByxdHrTlFUSSjJixPQOP8Hqu3ctH12nVIwOsloFtjnWkaWw8lZplbwx8B5jmrm1pUeanlKeOiVfMoOtXdX7c1m7oYoXe-MOXfEyrljOoliX11X2J53QqAmgEipWtKGaR7S24w9_7MLoNF08bukLCUT4O3qbtEWW71Gp4iGHNgAAAAH1IW7RAQ")

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

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong! Bot is alive!")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 Aditi Music Bot\n\n"
        "/play <song> — Play\n"
        "/skip — Skip\n"
        "/pause — Pause\n"
        "/resume — Resume\n"
        "/stop — Stop\n"
        "/queue — Queue\n"
        "/ping — Check bot"
    )

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /play <song>")
    query = " ".join(context.args)
    msg = await update.message.reply_text("🔎 Searching...")
    try:
        title, url = await asyncio.to_thread(get_url, query)
        chat_id = update.effective_chat.id
        if chat_id not in queues:
            queues[chat_id] = []
        queues[chat_id].append((title, url))
        if len(queues[chat_id]) == 1:
            await call_py.play(chat_id, MediaStream(url))
            await msg.edit_text(f"🎶 Now playing: {title}")
        else:
            await msg.edit_text(f"📋 Added to queue: {title}")
    except Exception as e:
        await msg.edit_text(f"❌ Error: {e}")

async def skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in queues and queues[chat_id]:
        queues[chat_id].pop(0)
    if chat_id in queues and queues[chat_id]:
        title, url = queues[chat_id][0]
        await call_py.play(chat_id, MediaStream(url))
        await update.message.reply_text(f"⏭ Now playing: {title}")
    else:
        try:
            await call_py.leave_call(chat_id)
        except:
            pass
        await update.message.reply_text("⏭ Queue empty, left VC.")

async def pause(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await call_py.pause_stream(update.effective_chat.id)
        await update.message.reply_text("⏸ Paused.")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")

async def resume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await call_py.resume_stream(update.effective_chat.id)
        await update.message.reply_text("▶️ Resumed.")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    queues[chat_id] = []
    try:
        await call_py.leave_call(chat_id)
    except:
        pass
    await update.message.reply_text("⏹ Stopped.")

async def queue_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = queues.get(update.effective_chat.id, [])
    if not q:
        return await update.message.reply_text("📋 Queue is empty.")
    text = "📋 Queue:\n" + "\n".join(f"{i}. {t}" for i, (t, _) in enumerate(q, 1))
    await update.message.reply_text(text)

async def web_handler(request):
    return web.Response(text="Aditi Music Bot Running!")

async def main():
    await user.start()
    print("✅ Userbot started!")
    await call_py.start()
    print("✅ PyTgCalls started!")

    ptb = Application.builder().token(BOT_TOKEN).build()
    ptb.add_handler(CommandHandler("ping", ping))
    ptb.add_handler(CommandHandler("help", help_cmd))
    ptb.add_handler(CommandHandler("play", play))
    ptb.add_handler(CommandHandler("skip", skip))
    ptb.add_handler(CommandHandler("pause", pause))
    ptb.add_handler(CommandHandler("resume", resume))
    ptb.add_handler(CommandHandler("stop", stop))
    ptb.add_handler(CommandHandler("queue", queue_cmd))

    server = web.Application()
    server.router.add_get("/", web_handler)
    runner = web.AppRunner(server)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    print("✅ Web server started!")

    await ptb.initialize()
    await ptb.start()
    await ptb.updater.start_polling(drop_pending_updates=True)
    print("✅ Bot polling started!")

    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
