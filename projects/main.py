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

    status_message = await message.answer("🔄 Обхожу защиту YouTube и анализирую видео...")

    # Хакерские настройки маскировки для обхода "Sign in to confirm you're not a bot"
    ydl_opts = {
        'format': 'best[ext=mp4][filesize<45M]/best[ext=mp4]/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'no_warnings': True,
        'quiet': True,
        # Имитируем запросы от обычного браузера и официальных клиентов
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        },
        # Заставляем yt-dlp использовать альтернативные клиенты для извлечения данных
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web_embedded', 'ios'],
                'skip': ['dash', 'hls']
            }
        }
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

            await status_message.edit_text(f"⏳ Видео весит {filesize:.1f} МБ. Загружаю...")
            
            video_file = types.FSInputFile(filename)
            await message.answer_video(video=video_file, caption="Готово! 🎉")
            
            os.remove(filename)
            await status_message.delete()
        else:
            await status_message.edit_text("❌ Ошибка: файл не найден после скачивания.")

    except Exception as e:
        print(f"Ошибка загрузки: {e}")
        await status_message.edit_text(f"❌ Ошибка обхода защиты YouTube.\nПопробуй другую ссылку или Shorts/TikTok.")
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