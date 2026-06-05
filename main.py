import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiohttp import web

# Твой токен
TOKEN = "8583216589:AAFZ1g8ZcS7fdOmdWjHuD4voLSFudgppkWI"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 1. Вот эта функция оживит команду /start
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}! Бот Максим на связи и официально работает на сервере Render! 🚀")

# 2. А эта функция будет отвечать на любое другое текстовое сообщение
@dp.message()
async def echo_msg(message: types.Message):
    await message.answer(f"Ты написал: {message.text}. Я пока только учусь, но сервер уже покорил!")


# Наш спасительный микро-веб-сервер для Render
async def handle(request):
    return web.Response(text="Бот Максим работает!")

async def main():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Жестко ставим порт 8080, который так сильно хочет Render
    port = 8080
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    print(f"Мини-сервер успешно обманул Render на порту {port}")
    print("Бот Максим официально запущен!")
    
    # Запуск самого бота
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())