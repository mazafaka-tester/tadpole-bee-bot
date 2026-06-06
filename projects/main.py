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
    await message.answer(f"Привет, {message.from_user.first_name}! Отправляй ссылку, маскировка включена! 🚀")

@dp.message()
async def download_video(message: types.Message):
    url = message.text
    
    if not url.startswith(("http://", "https://")):
        await message.answer("Скинь корректную ссылку (http:// или https://)")
        return

    # Красиво перехватываем YouTube, чтобы не гонять скрипт вхолопую
    if "youtube.com" in url or "youtu.be" in url:
        await message.answer(
            "⚠️ **YouTube временно недоступен.**\n\n"
            "Google заблокировал IP-адрес сервера Render и требует авторизацию (куки).\n"
            "Но вы можете скинуть мне ссылку на **TikTok**, и я без проблем скачаю видео! 🎬"
        )
        return

    status_message = await message.answer("🔄 Скачиваю видео... Пожалуйста, подождите.")

    ydl_opts = {
        'format': 'best[ext=mp4][filesize<45M]/best[ext=mp4]/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'no_warnings': True,
        'quiet': True
    }

    try:
        loop = asyncio.get_event_loop()
        with YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            filename = ydl.prepare_filename(info)
            
            if not os.path.exists(filename):
                base, _ = os.path.splitext(filename)
                filename = base + ".mp4"

        if os.path.exists(filename):
            filesize = os.path.getsize(filename) / (1024 * 1024)
            
            if filesize > 49.9:
                await status_message.edit_text(f"⚠️ Видео слишком огромное ({filesize:.1f} МБ) для лимитов Telegram.")
                os.remove(filename)
                return

            await status_message.edit_text(f"⏳ Загружаю в Телеграм...")
            
            video_file = types.FSInputFile(filename)
            await message.answer_video(video=video_file, caption="Вот твое видео! 🎉")
            
            os.remove(filename)
            await status_message.delete()
        else:
            await status_message.edit_text("❌ Ошибка: файл не найден после скачивания.")

    except Exception as e:
        print(f"Ошибка загрузки: {e}")
        await status_message.edit_text("❌ Не удалось скачать это видео. Возможно, сработала защита платформы.")
        if 'filename' in locals() and os.path.exists(filename):
            os.remove(filename)

async def handle(request):
    return web.Response(text="Бот Максим работает!")

async def main():
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = 8080
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    print("Бот запущен с обходом блокировок!")
    # Сбрасываем старые вебхуки и сессии, чтобы убрать ошибку Conflict
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())