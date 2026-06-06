import asyncio
import os
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiohttp import web
from yt_dlp import YoutubeDL

TOKEN = "8583216589:AAFZ1g8ZcS7fdOmdWjHuD4voLSFudgppkWI"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}! Бот Максим обновлен. Включена принудительная склейка звука в Full HD! 🔊🔥")

@dp.message()
async def download_video(message: types.Message):
    url = message.text
    
    if not url.startswith(("http://", "https://")):
        await message.answer("Скинь корректную ссылку (http:// или https://)")
        return

    if "youtube.com" in url or "youtu.be" in url:
        await message.answer(
            "⚠️ **YouTube временно недоступен.**\n"
            "Google блокирует IP сервера. Но TikTok и Instagram работают в Full HD! 🔥"
        )
        return

    status_message = await message.answer("🔄 Скачиваю видео и аудиодорожку высокого качества...")

    # Находим, куда именно Python установил FFmpeg
    ffmpeg_dir = os.path.join(sys.prefix, 'bin')
    if not os.path.exists(os.path.join(ffmpeg_dir, 'ffmpeg')):
        # Запасной путь для некоторых версий Linux окружений
        ffmpeg_dir = sys.prefix

    ydl_opts = {
        # Принудительно качаем лучшее видео + лучшее аудио
        'format': 'bestvideo[filesize<45M]+bestaudio/best[filesize<45M]/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'merge_output_format': 'mp4',
        'no_warnings': True,
        'quiet': True,
        # ПРИНУДИТЕЛЬНО указываем путь к FFmpeg, чтобы yt-dlp точно его увидел!
        'ffmpeg_location': ffmpeg_dir,
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
                await status_message.edit_text(f"⚠️ Видео слишком тяжелое ({filesize:.1f} МБ) для лимитов Telegram.")
                os.remove(filename)
                return

            await status_message.edit_text(f"⏳ Склеивание завершено! Размер: {filesize:.1f} МБ. Отправляю...")
            
            video_file = types.FSInputFile(filename)
            await message.answer_video(video=video_file, caption="Вот твое видео со стерео-звуком и в HD качестве! 🌟")
            
            os.remove(filename)
            await status_message.delete()
        else:
            await status_message.edit_text("❌ Ошибка при обработке файлов кодеками.")

    except Exception as e:
        print(f"Ошибка загрузки: {e}")
        await status_message.edit_text(f"❌ Ошибка склейки дорожек.\nТехнический лог: `{str(e)[:200]}`")
        if 'filename' in locals() and os.path.exists(filename):
            os.remove(filename)

async def handle(request):
    return web.Response(text="Бот Максим работает!")

async def main():
    # Принудительная установка FFmpeg в системную папку Python-окружения
    print("Проверка и установка FFmpeg...")
    os.system("ffdl install --add-path")
    
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = 8080
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    print("Бот Максим в супер-HD запущен!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())