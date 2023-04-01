import logging
import asyncio
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from telegram import Update
from unifi.settings import TELEGRAM_TOKEN
from tgbot.models import TelegramUser
from channels.db import database_sync_to_async
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


@database_sync_to_async
def create_user(tg_username, chat_id):
    telegram_user, created = TelegramUser.objects.get_or_create(username=tg_username, chat_id=chat_id)
    return created


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await asyncio.sleep(1)
    created = await create_user(user.username, user.id)
    if created:
        await context.bot.send_message(
            chat_id=user.id,
            text="unifi knu\nbot started\n"
        )


async def handle_err_notify(chat_id, message, bot):
    try:
        await bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        logging.error(f"Error sending message to chat {chat_id}: {e}")


bot = bot_instance()
handler = CommandHandler('start', handle_start)
bot.add_handler(handler)


def main():
    bot.run_polling()
