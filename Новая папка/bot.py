import logging
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ⚠️ ВАЖНО: Токен будет взят из переменных окружения Railway
TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    print("ОШИБКА: Токен не найден! Установите переменную окружения TOKEN в Railway")
    exit(1)

# Ваши данные
ADMIN_CARD_NUMBER = "0000 0000 0000 0000"  # Замените на ваш номер карты

# Данные о товарах
ITEMS = {
    "100": {"price": 100, "stars": 100},
    "250": {"price": 250, "stars": 250},
    "500": {"price": 450, "stars": 500},
    "1000": {"price": 950, "stars": 1000},
    "2500": {"price": 2200, "stars": 2500},
    "10000": {"price": 11000, "stars": 10000},
    "35000": {"price": 30000, "stars": 35000}
}

# Состояния пользователей
user_data = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # URL картинки (замените на свой)
    photo_url = "https://i.postimg.cc/yxZVhqzn/2.jpg"

    # Создаем клавиатуру с товарами
    keyboard = []
    for key, item in ITEMS.items():
        button = InlineKeyboardButton(
            f"{item['stars']} ⭐ - {item['price']} руб",
            callback_data=f"select_{key}"
        )
        keyboard.append([button])

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем сообщение с картинкой
    await update.message.reply_photo(
        photo=photo_url,
        caption="Добро пожаловать! Тут звезды ⭐ по самым вкусным ценам. Выберите кол-во:",
        reply_markup=reply_markup
    )

# Обработка нажатий на кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if data.startswith("select_"):
        # Пользователь выбрал товар
        item_key = data.split("_")[1]
        item = ITEMS[item_key]

        # Сохраняем выбор пользователя
        user_data[user_id] = {"selected_item": item_key}

        # Клавиатура подтверждения
        keyboard = [
            [
                InlineKeyboardButton("✅ Да", callback_data=f"confirm_{item_key}"),
                InlineKeyboardButton("❌ Нет", callback_data="cancel")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # URL картинки для подтверждения (замените на свой)
        photo_url = "https://i.postimg.cc/yxZVhqzn/2.jpg"

        # Отправляем новое сообщение вместо редактирования
        await query.message.reply_photo(
            photo=photo_url,
            caption=f"Вы хотите купить {item['stars']} ⭐ за {item['price']} руб?",
            reply_markup=reply_markup
        )

    elif data.startswith("confirm_"):
        # Пользователь подтвердил покупку
        item_key = data.split("_")[1]

        # Клавиатура для выбора оплаты
        keyboard = [[InlineKeyboardButton("💳 Перевод", callback_data="payment_method")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # URL картинки для выбора оплаты (замените на свой)
        photo_url = "https://i.postimg.cc/g2P0D0j0/pay.jpg"

        # Отправляем новое сообщение
        await query.message.reply_photo(
            photo=photo_url,
            caption="Выберите способ оплаты:",
            reply_markup=reply_markup
        )

    elif data == "payment_method":
        # Пользователь выбрал перевод
        keyboard = [[InlineKeyboardButton("✅ Я оплатил", callback_data="paid")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # URL картинки для реквизитов (замените на свой)
        photo_url = "https://i.postimg.cc/g2P0D0j0/pay.jpg"

        item_price = ITEMS[user_data[user_id]['selected_item']]['price']

        # Отправляем новое сообщение с реквизитами
        await query.message.reply_photo(
            photo=photo_url,
            caption=f"📋 Реквизиты для оплаты:\n\n"
                   f"Номер карты: `{ADMIN_CARD_NUMBER}`\n\n"
                   f"Сумма: {item_price} руб\n\n"
                   f"После оплаты нажмите кнопку ниже:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    elif data == "paid":
        # Пользователь подтвердил оплату
        item = ITEMS[user_data[user_id]['selected_item']]

        # URL финальной картинки (замените на свой)
        photo_url = "https://i.postimg.cc/2yb5HbnS/1.jpg"

        # Отправляем новое сообщение
        await query.message.reply_photo(
            photo=photo_url,
            caption="✅ Спасибо за заказ!\n\n"
                   "Проверка платежа занимает 5-10 минут. "
                   "По окончанию проверки звезды поступят на Ваш аккаунт.\n\n"
                   "Для нового заказа нажмите /start"
        )

        # Очищаем данные пользователя
        if user_id in user_data:
            del user_data[user_id]

    elif data == "cancel":
        # Пользователь отменил - возвращаем к выбору товара
        keyboard = []
        for key, item in ITEMS.items():
            button = InlineKeyboardButton(
                f"{item['stars']} ⭐ - {item['price']} руб",
                callback_data=f"select_{key}"
            )
            keyboard.append([button])

        reply_markup = InlineKeyboardMarkup(keyboard)

        # URL картинки приветствия (замените на свой)
        photo_url = "https://i.imgur.com/9vOMVqL.png"

        # Отправляем новое сообщение
        await query.message.reply_photo(
            photo=photo_url,
            caption="Добро пожаловать! Тут звезды ⭐ по самым вкусным ценам. Выберите кол-во:",
            reply_markup=reply_markup
        )

# Обработка обычных сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Если пользователь отправил просто текст
    if update.message and update.message.text and update.message.text != "/start":
        await update.message.reply_text("Используйте команду /start для начала работы")

# Ошибки
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

# Главная функция
def main():
    # Вставьте ваш токен от BotFather
    TOKEN = "8307833358:AAG4ogAtDn2kK-i882a_VBszfOylHBY284E"  # Замените на ваш токен

    # Создаем приложение
    application = Application.builder().token(TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)

    # Запускаем бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
