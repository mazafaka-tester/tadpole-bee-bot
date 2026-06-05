import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiohttp import web
from yt_dlp import YoutubeDL

TOKEN = "8583216589:AAFZ1g8ZcS7fdOmdWjHuD4voLSFudgppkWI"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}! Отправь мне ссылку на видео из YouTube или TikTok, и я скачаю его для тебя! 🚀")

# Хэндлер для обработки ссылок
@dp.message()
async def download_video(message: types.Message):
    url = message.text
    
    # Быстрая проверка, что нам скинули ссылку
    if not url.startswith(("http://", "https://")):
        await message.answer("Отправь мне корректную ссылку, которая начинается с http:// или https://")
        return

    status_message = await message.answer("🔄 Начинаю скачивание видео... Пожалуйста, подожди.")

    # Настройки для yt-dlp
    # Скачиваем видео в лучшем качестве, но ограничиваем размер, чтобы Telegram пропустил (до 50 МБ для обычных ботов)
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',  # Сохраняем в папку downloads
        'max_filesize': 50 * 1024 * 1024,       # Лимит 50 МБ
    }

    try:
        # Запускаем скачивание в отдельном потоке, чтобы бот не зависал
        loop = asyncio.get_event_loop()
        with YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            filename = ydl.prepare_filename(info)

        # Проверяем, существует ли файл
        if os.path.exists(filename):
            await status_message.edit_text("⏳ Видео скачано на сервер, отправляю его тебе...")
            
            # Отправляем видео пользователю
            video_file = types.FSInputFile(filename)
            await message.answer_video(video=video_file, caption="Вот твое видео! 🎉")
            
            # Удаляем файл с сервера, чтобы беречь место
            os.remove(filename)
            await status_message.delete()
        else:
            await status_message.edit_text("❌ Не удалось найти скачанный файл.")

    except Exception as e:
        print(f"Ошибка при скачивании: {e}")
        await status_message.edit_text(f"❌ Произошла ошибка при обработке ссылки. Возможно, видео слишком много весит (лимит 50 МБ).")
        
        # Если файл успел создаться, но всё упало — чистим за собой
        if 'filename' in locals() and os.path.exists(filename):
            os.remove(filename)

# Веб-сервер для Render
async def handle(request):
    return web.Response(text="Бот Максим работает!")

async def main():
    # Создаем папку для загрузок, если её нет
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = 8080
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    print(f"Мини-сервер запущен на порту {port}")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())