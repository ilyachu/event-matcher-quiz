import os
import asyncio
import httpx
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "@your_channel_username")
BACKEND_URL = os.getenv("BACKEND_INTERNAL_URL", "http://localhost:8080")

if not BOT_TOKEN:
    print("[WARNING] TELEGRAM_BOT_TOKEN не задан. Бот не сможет запуститься без токена.")

bot = Bot(token=BOT_TOKEN) if BOT_TOKEN else None
dp = Dispatcher()

# Кэш связки: telegram_user_id -> quiz_lead_id
user_quiz_sessions = {}

async def check_subscription(user_id: int) -> bool:
    """Проверяет подписку пользователя на обязательный канал."""
    if not bot:
        return False
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        # Статусы подписчика / создателя / админа
        return member.status in ["creator", "administrator", "member"]
    except Exception as e:
        print(f"[Subscription Check Error] User {user_id}: {e}")
        return False

@dp.message(CommandStart(deep_link=True))
async def cmd_start_with_deeplink(message: types.Message, command: CommandObject):
    """Обработка перехода с лендинга по ссылке вида t.me/bot?start=quiz_<uuid>"""
    args = command.args or ""
    quiz_id = args.replace("quiz_", "") if args.startswith("quiz_") else args
    
    if quiz_id:
        user_quiz_sessions[message.from_user.id] = quiz_id

    is_sub = await check_subscription(message.from_user.id)
    if is_sub:
        await message.answer("🎉 Вы подписаны на канал! Загружаю вашу персональную подборку от DeepSeek AI...")
        await deliver_recommendations(message.chat.id, message.from_user.id)
    else:
        channel_clean = CHANNEL_ID.replace("@", "")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 1. Подписаться на канал", url=f"https://t.me/{channel_clean}")],
            [InlineKeyboardButton(text="✅ 2. Я подписался, забрать план", callback_data="check_subscription")]
        ])
        await message.answer(
            f"Привет, {message.from_user.first_name}! 👋\n\n"
            f"Твой персональный дайджест мероприятий уже сформирован нейросетью.\n\n"
            f"👉 Чтобы бот открыл доступ к подборке, подпишись на наш официальный канал сообщества:",
            reply_markup=keyboard
        )

@dp.message(CommandStart())
async def cmd_start_regular(message: types.Message):
    """Обработка обычного /start без параметров квиза"""
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        f"Чтобы получить персональную подборку мероприятий от AI, пройдите короткий 1-минутный квиз на нашем сайте."
    )

@dp.callback_query(F.data == "check_subscription")
async def on_subscription_check(callback: types.CallbackQuery):
    """Callback-кнопка повторной проверки подписки"""
    is_sub = await check_subscription(callback.from_user.id)
    if is_sub:
        await callback.message.edit_text("🎉 Отлично! Подписка подтверждена. Формирую персональный дайджест...")
        await deliver_recommendations(callback.message.chat.id, callback.from_user.id)
    else:
        await callback.answer("❌ Подписка пока не найдена. Пожалуйста, подпишитесь на канал и нажмите кнопку снова!", show_alert=True)

async def deliver_recommendations(chat_id: int, tg_user_id: int):
    """Запрашивает у бэкенда рекомендации и отправляет их в чат."""
    quiz_id = user_quiz_sessions.get(tg_user_id)
    if not quiz_id:
        await bot.send_message(chat_id, "Данные квиза не найдены. Пожалуйста, заполните анкету на сайте заново.")
        return

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            res = await client.get(f"{BACKEND_URL}/api/recommendations/{quiz_id}")
            if res.status_code == 200:
                data = res.json()
                rec_text = data.get("recommendation", "")
                await bot.send_message(chat_id, rec_text)
            else:
                await bot.send_message(chat_id, "Не удалось получить рекомендации. Пожалуйста, попробуйте чуть позже.")
        except Exception as e:
            await bot.send_message(chat_id, f"Ошибка соединения с сервисом: {e}")

async def main():
    if not bot:
        print("[EXIT] Укажите TELEGRAM_BOT_TOKEN для запуска бота.")
        return
    print("✓ Запуск Telegram-бота (VibeMatch Subscription Gate)...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
