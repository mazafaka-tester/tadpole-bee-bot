import asyncio
from aiogram import Bot, Dispatcher
from aiohttp import web

# Твой токен
TOKEN = "8583216589:AAFZ1g8ZcS7fdOmdWjHuD4voLSFudgppkWI"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Хэндлеры твоего бота (кнопки, старт и т.д.) оставь ниже, 
# а в самый конец файла, вместо dp.start_polling(), вставь вот этот блок:

async def handle(request):
    return web.Response(text="Бот Максим работает!")

async def main():
    # Создаем мини-сайт для обмана Render
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    await site.start()
    
    print("Мини-сервер запущен на порту 10000")
    
    # Запускаем самого бота
    print("Бот Максим успешно запущен!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())