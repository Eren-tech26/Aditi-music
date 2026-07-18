from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from pytgcalls.exceptions import NoActiveGroupCall
import asyncio
from player import get_audio_url, add_to_queue, get_queue, clear_queue, pop_queue
from config import OWNER_ID

# Shared call instance (set from main.py)
call_py: PyTgCalls = None

def set_call(c):
    global call_py
    call_py = c

def is_admin(func):
    """Decorator: only admins or owner can use the command."""
    async def wrapper(client, message: Message):
        if message.from_user.id == OWNER_ID:
            return await func(client, message)
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status in ("administrator", "creator"):
            return await func(client, message)
        await message.reply("❌ Admins only.")
    return wrapper

async def play_next(chat_id):
    item = pop_queue(chat_id)
    if item:
        title, url = item
        await call_py.play(chat_id, MediaStream(url))
        return title
    return None

def register(app: Client):

    @app.on_message(filters.command("play") & filters.group)
    async def play(client, message: Message):
        if len(message.command) < 2:
            return await message.reply("Usage: /play <song name or YouTube URL>")

        query = message.text.split(None, 1)[1]
        msg = await message.reply("🔎 Searching...")

        try:
            title, url = await asyncio.to_thread(get_audio_url, query)
        except Exception as e:
            return await msg.edit(f"❌ Could not find: {e}")

        chat_id = message.chat.id

        try:
            # Check if already playing
            active = await call_py.get_active_call(chat_id)
            # Already playing — add to queue
            add_to_queue(chat_id, (title, url))
            await msg.edit(f"📋 Added to queue: **{title}**")
        except Exception:
            # Not playing — start now
            add_to_queue(chat_id, (title, url))
            t = await play_next(chat_id)
            await msg.edit(f"🎶 Now playing: **{t}**")

    @app.on_message(filters.command("skip") & filters.group)
    @is_admin
    async def skip(client, message: Message):
        chat_id = message.chat.id
        title = await play_next(chat_id)
        if title:
            await message.reply(f"⏭ Skipped! Now playing: **{title}**")
        else:
            await call_py.leave_call(chat_id)
            await message.reply("⏭ Skipped! Queue is empty, left VC.")

    @app.on_message(filters.command("pause") & filters.group)
    @is_admin
    async def pause(client, message: Message):
        await call_py.pause_stream(message.chat.id)
        await message.reply("⏸ Paused.")

    @app.on_message(filters.command("resume") & filters.group)
    @is_admin
    async def resume(client, message: Message):
        await call_py.resume_stream(message.chat.id)
        await message.reply("▶️ Resumed.")

    @app.on_message(filters.command("stop") & filters.group)
    @is_admin
    async def stop(client, message: Message):
        clear_queue(message.chat.id)
        await call_py.leave_call(message.chat.id)
        await message.reply("⏹ Stopped and left VC.")

    @app.on_message(filters.command("volume") & filters.group)
    @is_admin
    async def volume(client, message: Message):
        if len(message.command) < 2:
            return await message.reply("Usage: /volume 1-200")
        try:
            vol = int(message.command[1])
            await call_py.change_volume_call(message.chat.id, vol)
            await message.reply(f"🔊 Volume set to {vol}%")
        except Exception as e:
            await message.reply(f"❌ Error: {e}")

    @app.on_message(filters.command("queue") & filters.group)
    async def queue(client, message: Message):
        q = get_queue(message.chat.id)
        if not q:
            return await message.reply("📋 Queue is empty.")
        text = "📋 **Queue:**\n"
        for i, (title, _) in enumerate(q, 1):
            text += f"{i}. {title}\n"
        await message.reply(text)

    @app.on_message(filters.command("help"))
    async def help(client, message: Message):
        await message.reply(
            "🎵 **Aditi Music Bot**\n\n"
            "/play <song> — Play a song\n"
            "/queue — Show queue\n"
            "/skip — Skip current song\n"
            "/pause — Pause\n"
            "/resume — Resume\n"
            "/volume <1-200> — Set volume\n"
            "/stop — Stop and leave VC\n\n"
            "⚙️ Skip, pause, resume, volume & stop are admin-only."
        )
