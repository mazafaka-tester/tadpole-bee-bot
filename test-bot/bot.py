import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder # Инструмент для создания кнопок
import os
from aiohttp import web

bot = Bot(token="8935286501:AAGlrQnKOlIumc24SDsZ-iongeLn6xI0UQw")
dp = Dispatcher()

@dp.message(CommandStart())
async def start_message(message: types.Message):
    # Создаем клавиатуру с кнопкой
    builder = InlineKeyboardBuilder()
    # text — что написано на кнопке, callback_data — скрытый индентификатор кнопки
    builder.add(types.InlineKeyboardButton(text="Нажми меня! 🚀", callback_data="button_pressed"))
    
    await message.answer("Привет! Вот твоя кнопка:", reply_markup=builder.as_markup())

# ХЭНДЛЕР ДЛЯ НАЖАТИЯ ИНЛАЙН-КНОПКИ
@dp.callback_query(F.data == "button_pressed") # Ловим кнопку со скрытым значением "button_pressed"
async def handle_button(callback: types.CallbackQuery):
    # Отвечаем на сам клик (чтобы у пользователя перестала крутиться иконка загрузки на кнопке)
    await callback.answer("Успешно!") 
    
    # Отправляем новое сообщение в чат
    await callback.message.answer("Ты успешно нажал на инлайн-кнопку! 🎉")

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