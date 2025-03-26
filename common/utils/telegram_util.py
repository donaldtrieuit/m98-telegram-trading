import logging

import requests
from m98_trading import settings

logger = logging.getLogger(__name__)


def send_telegram_message(chat_id, message):
    """Send a message to Telegram using bot's configured credentials."""
    bot_telegram_token = settings.TELEGRAM_BOT_API_KEY
    url = f"https://api.telegram.org/bot{bot_telegram_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }
    response = requests.post(url, data=payload)
    if not response.ok:
        logger.error(f"Failed to send message: {response.text}")
    return response.json()
