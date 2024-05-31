import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import sqlite3

TOKEN = '6924056969:AAGVuZkht5p7XhWju1kdHcGbCWdJ8blHYes'  # Замените на токен вашего бота

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (chat_id) VALUES (?)', (chat_id,))
    conn.commit()
    conn.close()
    
    # Создание кнопки для открытия веб-приложения
    web_app_url = "https://marketplace-production.tg-shops.com/testmagazin"
    keyboard = [
        [InlineKeyboardButton("Open", web_app=WebAppInfo(url=web_app_url))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        'Добро пожаловать в TestMagaz!\n\nДля заказа нажмите на кнопку "Open"\n\nПриятных заказов! 🍕✨',
        reply_markup=reply_markup
    )

# Функция рассылки сообщений с изображением или GIF
async def broadcast_media(bot, message, media, media_type) -> None:
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT chat_id FROM users')
    users = c.fetchall()
    conn.close()

    for user in users:
        chat_id = user[0]
        try:
            if media_type == 'photo':
                await bot.send_photo(chat_id=chat_id, photo=media, caption=message)
            elif media_type == 'gif':
                await bot.send_animation(chat_id=chat_id, animation=media, caption=message)
        except Exception as e:
            print(f"Failed to send media to {chat_id}: {e}")

# Обработчик медиа (фото и GIF)
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if 'broadcast_message' in context.user_data:
        message = context.user_data.pop('broadcast_message')
        media = update.message.photo[-1].file_id if update.message.photo else update.message.animation.file_id
        media_type = 'photo' if update.message.photo else 'gif'
        bot = context.bot

        await broadcast_media(bot, message, media, media_type)

        # Удаление всех сообщений после рассылки
        if 'broadcast_prompt_message' in context.user_data:
            await context.user_data['broadcast_prompt_message'].delete()
            context.user_data.pop('broadcast_prompt_message')
        if 'broadcast_command_message' in context.user_data:
            await context.user_data['broadcast_command_message'].delete()
            context.user_data.pop('broadcast_command_message')

        await update.message.delete()
        await update.message.reply_text('Пост отправлен всем пользователям!')

# Команда /post
async def broadcast_media_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        message = ' '.join(context.args)
        context.user_data['broadcast_message'] = message

        prompt_message = await update.message.reply_text('Пришлите фото или GIF к посту.')
        context.user_data['broadcast_prompt_message'] = prompt_message
        context.user_data['broadcast_command_message'] = update.message

    else:
        await update.message.reply_text('Напишите: /post <текст>')

# Основная функция
def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('post', broadcast_media_command))
    application.add_handler(MessageHandler(filters.PHOTO | filters.ANIMATION, handle_media))

    application.run_polling()

if __name__ == '__main__':
    main()
