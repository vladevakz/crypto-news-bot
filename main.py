import os
import feedparser
import google.generativeai as genai
from telegram import Bot
import asyncio

TELEGRAM_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
GEMINI_KEY = os.environ['GEMINI_API_KEY']
RSS_FEED = os.environ.get('RSS_FEED', 'https://decrypt.co/feed')

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

feedparser.USER_AGENT = 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'

async def main():
    feed = feedparser.parse(RSS_FEED)
    print(f"Статус HTTP: {feed.status}")
    print(f"Заголовок ответа: {feed.headers.get('content-type', 'нет')}")
    print(f"Найдено новостей: {len(feed.entries)}")

    entries = feed.entries[:5]
    if not entries:
        print("Первичный источник не дал новостей, пробую запасной...")
        feed = feedparser.parse('https://cointelegraph.com/rss')
        print(f"Cointelegraph найдено: {len(feed.entries)}")
        entries = feed.entries[:5]

    if not entries:
        print("Нет новостей ни в одном источнике. Завершение.")
        return

    headlines = "\n".join([f"- {e.title}" for e in entries])
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
        post_text = "🔥 Свежие новости криптомира:\n\n" + headlines

    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=post_text, parse_mode='HTML')
    print("Сообщение отправлено в канал.")

if __name__ == '__main__':
    asyncio.run(main())
