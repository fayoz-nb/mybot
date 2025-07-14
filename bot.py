import logging, aiohttp, asyncio, time, os
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.types import FSInputFile
from insta_utils import get_instagram_video, get_youtube_video
from flask import Flask
from threading import Thread

BOT_TOKEN = "7623800708:AAGqn3deRMrK8UJAym655XyUJ2X1uw50iQw"

# Logging
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# URL checkers
def is_tiktok_url(text): return "tiktok.com" in text
def is_instagram_url(text): return "instagram.com" in text or "instagram." in text
def is_youtube_url(text): return "youtube.com" in text or "youtu.be" in text

# Flask server for uptime
app = Flask('')

@app.route('/')
def home():
    return "✅ Бот работает!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run).start()

# TikTok downloader
async def get_tiktok_video(url):
    api = f"https://www.tikwm.com/api/?url={url}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api) as resp:
                data = await resp.json()
                return data.get("data", {}).get("play")
    except Exception as e:
        print("❌ TikTok error:", e)
    return None

# /start
@dp.message(Command("start"))
async def start_cmd(msg: types.Message):
    await msg.answer("👋 Привет! Отправь ссылку на TikTok, Instagram или YouTube 🎬")

# Обработка ссылок
@dp.message()
async def download_video(msg: types.Message):
    start = time.time()
    video_url = None
    file_path = None

    if is_tiktok_url(msg.text):
        await msg.answer("⏳ Загружаю TikTok...")
        video_url = await get_tiktok_video(msg.text)

    elif is_instagram_url(msg.text):
        await msg.answer("⏳ Загружаю Instagram...")
        file_path = get_instagram_video(msg.text, "insta_video.mp4")

    elif is_youtube_url(msg.text):
        await msg.answer("⏳ Загружаю YouTube...")
        file_path = get_youtube_video(msg.text, "yt_video.mp4")

    else:
        await msg.answer("❗ Неподдерживаемая ссылка. Присылай TikTok, Instagram или YouTube.")
        return

    duration = time.time() - start

    if file_path and os.path.exists(file_path):
        video = FSInputFile(file_path)
        await msg.answer_video(video, caption=f"✅ Готово за {duration:.2f} сек.")
        os.remove(file_path)
        return

    if video_url:
        try:
            await msg.answer_video(video_url, caption=f"✅ Готово за {duration:.2f} сек.")
        except Exception:
            await msg.answer_document(video_url, caption=f"📎 Видео сохранено как файл ({duration:.2f} сек.)")
    else:
        await msg.answer("❌ Не удалось скачать. Попробуй другой пост.")

# Запуск
async def main():
    print("🤖 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())
