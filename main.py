"""
YouTube Search Bot - ищет видео по описанию
Безопасный - токен берется из переменной окружения BOT_TOKEN
Установи: pip install python-telegram-bot youtubesearchpython
"""

import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from youtubesearchpython import VideosSearch

# Токен НЕ пишем сюда! Берем из окружения
TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Салом! Я нахожу видео с YouTube по описанию.\n\n"
        "Просто напиши что хочешь найти, например:\n"
        "• как чинить экран айфона\n"
        "• обзор iPhone 18 Pro Max\n"
        "• смешные коты\n"
        "• как приготовить лагман\n\n"
        "И я найду 5 лучших видео! 🎬"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ Как пользоваться:\n"
        "Просто напиши любой текст - я найду видео на YouTube.\n\n"
        "Команды:\n"
        "/start - начать\n"
        "/help - помощь"
    )

async def search_youtube(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    if not query or query.startswith('/'):
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    status_msg = await update.message.reply_text(f"🔍 Ищу: '{query}'...")

    try:
        videos_search = VideosSearch(query, limit=5)
        results = videos_search.result()
        videos = results.get('result', [])

        if not videos:
            await status_msg.edit_text("😔 Ничего не нашел. Попробуй написать по-другому.")
            return

        await status_msg.delete()

        for video in videos:
            title = video.get('title', 'Без названия')
            link = video.get('link', '')
            duration = video.get('duration', '')
            channel = video.get('channel', {}).get('name', '')
            views = video.get('viewCount', {}).get('short', '')
            thumbnail = video.get('thumbnails', [{}])[0].get('url', '')

            caption = f"🎬 <b>{title}</b>\n"
            caption += f"📺 {channel} | ⏱ {duration} | 👁 {views}\n\n"
            caption += f"🔗 {link}"

            keyboard = [[InlineKeyboardButton("▶️ Смотреть на YouTube", url=link)]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Отправляем с превью если есть
            try:
                await update.message.reply_photo(
                    photo=thumbnail,
                    caption=caption,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
            except:
                await update.message.reply_text(
                    caption,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
            await asyncio.sleep(0.3)

    except Exception as e:
        print(f"Error: {e}")
        await status_msg.edit_text("⚠️ Ошибка поиска. Попробуй еще раз чуть позже.")

def main():
    if not TOKEN:
        print("❌ ОШИБКА: Не найден BOT_TOKEN!")
        print("Установи переменную окружения:")
        print("export BOT_TOKEN='твой_новый_токен'")
        print("Или в Replit -> Secrets -> BOT_TOKEN")
        return

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_youtube))

    print("✅ Бот запущен! Ищет YouTube видео...")
    app.run_polling()

if __name__ == "__main__":
    main()
