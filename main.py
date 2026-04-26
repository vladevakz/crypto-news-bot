import os
import feedparser
import google.generativeai as genai
from telegram import Bot
import asyncio

# Получение переменных из секретов GitHub
TELEGRAM_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
GEMINI_KEY = os.environ['GEMINI_API_KEY']
RSS_FEED = os.environ.get('RSS_FEED', 'https://www.coindesk.com/arc/outboundfeeds/rss/')

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

async def main():
    # Парсим RSS
    feed = feedparser.parse(RSS_FEED)
    entries = feed.entries[:5]  # берём 5 свежих новостей

    if not entries:
        print("Нет новостей")
        return

    # Формируем список заголовков
    headlines = "\n".join([f"- {e.title}" for e in entries])

    # Просим ИИ красиво оформить
    prompt = (
        "Ты — редактор крипто-новостей. Сделай из этих заголовков привлекательный "
        "пост для Telegram. Используй эмодзи, разбивай на абзацы, сохраняй смысл. "
        "Вот заголовки:\n" + headlines
    )

    try:
        response = model.generate_content(prompt)
        post_text = response.text
    except Exception as e:
        print(f"Ошибка Gemini: {e}")
        # Если ИИ не сработал, отправляем просто заголовки
        post_text = "🔥 Свежие новости криптомира:\n\n" + headlines

    # Отправляем в канал
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=post_text, parse_mode='HTML')

if __name__ == '__main__':
    asyncio.run(main())
