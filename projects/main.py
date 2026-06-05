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
    await message.answer(f"Привет, {message.from_user.first_name}! Отправляй ссылку, теперь качаем на максималках и без жестких лимитов! 🚀")

@dp.message()
async def download_video(message: types.Message):
    url = message.text
    
    if not url.startswith(("http://", "https://")):
        await message.answer("Скинь корректную ссылку (http:// или https://)")
        return

    status_message = await message.answer("🔄 Анализирую видео и подбираю лучший размер...")

    # Настройки yt-dlp: убираем жесткий лимит размера, но просим скачать 
    # лучшее качество, которое при этом укладывается в 50 МБ (размер в байтах)
    ydl_opts = {
        # Скрипт пытается взять лучшее качество, но если оно тяжелое, 
        # автоматически выбирает формат полегче, чтобы влезть в лимит TG
        'format': 'bestvideo[filesize<45M]+bestaudio/best[filesize<45M]/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'merge_output_format': 'mp4',
    }

    try:
        loop = asyncio.get_event_loop()
        with YoutubeDL(ydl_opts) as ydl:
            # Извлекаем инфу и качаем
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            filename = ydl.prepare_filename(info)
            
            # Если скачалось в mkv или другом формате, yt-dlp может изменить расширение на mp4 при склейке
            if not os.path.exists(filename):
                base, _ = os.path.splitext(filename)
                filename = base + ".mp4"

        if os.path.exists(filename):
            filesize = os.path.getsize(filename) / (1024 * 1024) # Переводим в МБ
            
            # Проверка на дурака: если видео всё равно больше 50 МБ (например, стрим)
            if filesize > 49.9:
                await status_message.edit_text(f"⚠️ Видео слишком огромное ({filesize:.1f} МБ). Телеграм разрешает ботам отправлять файлы только до 50 МБ.")
                os.remove(filename)
                return

            await status_message.edit_text(f"⏳ Видео весит {filesize:.1f} МБ. Загружаю в Телеграм...")
            
            video_file = types.FSInputFile(filename)
            await message.answer_video(video=video_file, caption="Твое видео готово! 🎉")
            
            os.remove(filename)
            await status_message.delete()
        else:
            await status_message.edit_text("❌ Ошибка: не удалось создать файл видео.")

    except Exception as e:
        print(f"Ошибка: {e}")
        await status_message.edit_text("❌ Не удалось скачать. Возможно, это закрытое видео, стрим или формат не поддерживается.")
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
    
    print("Бот Максим на максималках запущен!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())