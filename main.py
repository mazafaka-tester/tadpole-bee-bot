import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import CommandStart

TOKEN = "8583216589:AAFZ1g8ZcS7fdOmdWjHuD4voLSFudgppkWI"

session = AiohttpSession(proxy="http://138.197.148.214:8080")

bot = Bot(token=TOKEN, session=session)
dp = Dispatcher()

@dp.message(CommandStart())
async def command_start_handler(message: types.Message):
    await message.answer(f"Привет, {message.from_user.full_name}! Робот Максим на связи!\nПрямой IP-туннель сработал. Скидывай ссылку!")

@dp.message()
async def echo_handler(message: types.Message):
    await message.reply(f"Принял ссылку: {message.text}")

async def main():
    print("Робот Максим пробивается к Telegram по прямому IP прокси...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())