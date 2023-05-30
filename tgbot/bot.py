import logging
import asyncio

from asgiref.sync import sync_to_async
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from telegram import Update
from unifi.settings import TELEGRAM_TOKEN
from tgbot.models import TelegramUser
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

# initialize the Django ORM
django.setup()
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def bot_instance():
    bot = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    return bot


@sync_to_async
def create_telegram_user(username, chat_id):
    from tgbot.models import TelegramUser
    TelegramUser.objects.get_or_create(username=username, chat_id=chat_id)


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await asyncio.sleep(1)
    username = user.username or ''
    await create_telegram_user(username, user.id)
    await context.bot.send_message(
        chat_id=user.id,
        text="unifi knu\nbot started\n"
    )


@sync_to_async
def get_telegram_users():
    from tgbot.models import TelegramUser
    return list(TelegramUser.objects.all())


async def send_message_tg(message):
    users = await get_telegram_users()
    for user in users:
        await handle_err_notify(chat_id=user.chat_id, message=message, bot=bot.bot)


async def handle_err_notify(chat_id, message, bot):
    try:
        await bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        logging.error(f"Error sending message to users: {e}")


bot = bot_instance()
handler = CommandHandler('start', handle_start)
bot.add_handler(handler)


def main():
    bot.run_polling()
