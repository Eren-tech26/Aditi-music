import asyncio
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
import yt_dlp

# Queue: {chat_id: [list of stream urls]}
queues = {}

def get_audio_url(query: str) -> tuple:
    """Returns (title, url) from YouTube search or URL."""
    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        search = query if query.startswith("http") else f"ytsearch1:{query}"
        info = ydl.extract_info(search, download=False)
        if "entries" in info:
            info = info["entries"][0]
        return info["title"], info["url"]

def add_to_queue(chat_id, item):
    if chat_id not in queues:
        queues[chat_id] = []
    queues[chat_id].append(item)

def get_queue(chat_id):
    return queues.get(chat_id, [])

def clear_queue(chat_id):
    queues[chat_id] = []

def pop_queue(chat_id):
    if chat_id in queues and queues[chat_id]:
        return queues[chat_id].pop(0)
    return None
