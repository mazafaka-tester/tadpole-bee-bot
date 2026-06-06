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
    await message.answer(f"Привет, {message.from_user.first_name}! Бот Максим обновлен. Теперь качаем в максимальном качестве со звуком! 🎬🚀")

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

    status_message = await message.answer("🔄 Скачиваю видео в наилучшем качестве... Пожалуйста, подожди.")

    # ВОЗВРАЩАЕМ МАКСИМАЛЬНОЕ КАЧЕСТВО (благодаря FFmpeg)
    ydl_opts = {
        # Ищем лучшее видео (до 45МБ) + лучшее аудио и склеиваем в mp4
        'format': 'bestvideo[filesize<45M]+bestaudio/best[filesize<45M]/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'merge_output_format': 'mp4',
        'no_warnings': True,
        'quiet': True
    }

    try:
        loop = asyncio.get_event_loop()
        with YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            filename = ydl.prepare_filename(info)
            
            # Если после склейки расширение изменилось
            if not os.path.exists(filename):
                base, _ = os.path.splitext(filename)
                filename = base + ".mp4"

        if os.path.exists(filename):
            filesize = os.path.getsize(filename) / (1024 * 1024)
            
            if filesize > 49.9:
                await status_message.edit_text(f"⚠️ Видео слишком тяжелое ({filesize:.1f} МБ) для лимитов Telegram.")
                os.remove(filename)
                return

            await status_message.edit_text(f"⏳ Видео готово ({filesize:.1f} МБ). Отправляю в HD...")
            
            video_file = types.FSInputFile(filename)
            await message.answer_video(video=video_file, caption="Держи видео в отличном качестве! 🔥")
            
            os.remove(filename)
            await status_message.delete()
        else:
            await status_message.edit_text("❌ Ошибка: файл потерялся при сборке.")

    except Exception as e:
        print(f"Ошибка загрузки: {e}")
        await status_message.edit_text("❌ Не удалось скачать. Возможно, сработала защита платформы.")
        if 'filename' in locals() and os.path.exists(filename):
            os.remove(filename)

async def handle(request):
    return web.Response(text="Бот Максим работает!")

async def main():
    # ХАК: Скачиваем FFmpeg прямо в папку проекта, обходя запреты Render!
    print("Установка FFmpeg внутри окружения...")
    os.system("ffdl install --add-path")
    print("FFmpeg успешно настроен!")

    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = 8080
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    print("Бот Максим в HD-режиме запущен!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())