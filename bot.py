import sqlite3
import telebot
from telebot import types

# Bot configuration
BOT_TOKEN = '8253586903:AAFJGQehaFg1Rm7m1k7VO7vLEB57R6T0fi4'
ALLOWED_CHAT_ID = 5993122611

# Створюємо бота
bot = telebot.TeleBot(BOT_TOKEN)

def get_current_prices():
    """Отримати поточні ціни з бази даних з додаванням суфікса"""
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT Apartament1, Apartament2, Apartament3 FROM prices LIMIT 1")
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'apartament1': row[0] + '/ніч',
                'apartament2': row[1] + '/ніч',
                'apartament3': row[2] + '/ніч'
            }
        else:
            return None
    except sqlite3.Error as e:
        print(f"Помилка бази даних: {e}")
        return None

def update_price(apartment_num, new_price):
    """Оновити ціну для конкретної квартири"""
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        column_name = f"Apartament{apartment_num}"
        cursor.execute(f"UPDATE prices SET {column_name} = ? WHERE id = 1", (new_price,))

        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Помилка оновлення ціни: {e}")
        return False

@bot.message_handler(commands=['start'])
def start(message):
    """Обробник команди /start"""
    if message.chat.id != ALLOWED_CHAT_ID:
        bot.reply_to(message, "❌ Доступ заборонено!")
        return

    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_prices = types.InlineKeyboardButton("💰 Переглянути ціни", callback_data="show_prices")
    btn_set_price = types.InlineKeyboardButton("✏️ Змінити ціну", callback_data="set_price_menu")
    btn_help = types.InlineKeyboardButton("❓ Допомога", callback_data="help")
    markup.add(btn_prices, btn_set_price, btn_help)

    bot.reply_to(message,
        "👋 Привіт! Я бот для управління цінами на квартири в Аланії.\n\n"
        "🏠 Оберіть дію нижче:",
        reply_markup=markup
    )

@bot.message_handler(commands=['prices'])
def show_prices(message):
    """Показати поточні ціни"""
    if message.chat.id != ALLOWED_CHAT_ID:
        bot.reply_to(message, "❌ Доступ заборонено!")
        return

    prices = get_current_prices()
    if prices:
        response = (
            "🏠 Поточні ціни на квартири:\n\n"
            f"1️⃣ Квартира 1: {prices['apartament1']}\n"
            f"2️⃣ Квартира 2: {prices['apartament2']}\n"
            f"3️⃣ Квартира 3: {prices['apartament3']}\n\n"
            "💡 Щоб змінити ціну, використовуйте: /set_price <номер> <ціна>"
        )
    else:
        response = "❌ Не вдалося отримати ціни з бази даних"

    bot.reply_to(message, response)

@bot.message_handler(commands=['set_price'])
def set_price(message):
    """Змінити ціну квартири"""
    if message.chat.id != ALLOWED_CHAT_ID:
        bot.reply_to(message, "❌ Доступ заборонено!")
        return

    try:
        # Розбираємо команду
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message,
                "❌ Неправильний формат!\n\n"
                "📝 Використання: /set_price <номер квартири> <ціна>\n"
                "📋 Приклад: /set_price 1 90€\n\n"
                "🏠 Доступні квартири: 1, 2, 3"
            )
            return

        apartment_num = int(parts[1])
        if apartment_num not in [1, 2, 3]:
            bot.reply_to(message, "❌ Номер квартири має бути 1, 2 або 3!")
            return

        new_price = ' '.join(parts[2:])

        # Оновлюємо ціну
        if update_price(apartment_num, new_price):
            bot.reply_to(message,
                f"✅ Ціна успішно оновлена!\n\n"
                f"🏠 Квартира {apartment_num}: {new_price}\n\n"
                "🔄 Зміни будуть відображені на сайті після перезавантаження сторінки."
            )

            # Показуємо всі поточні ціни після оновлення
            prices = get_current_prices()
            if prices:
                bot.reply_to(message,
                    "📊 Оновлені ціни:\n\n"
                    f"1️⃣ Квартира 1: {prices['apartament1']}\n"
                    f"2️⃣ Квартира 2: {prices['apartament2']}\n"
                    f"3️⃣ Квартира 3: {prices['apartament3']}"
                )
        else:
            bot.reply_to(message, "❌ Помилка оновлення ціни. Спробуйте ще раз.")

    except ValueError:
        bot.reply_to(message, "❌ Номер квартири має бути числом (1, 2 або 3)!")
    except Exception as e:
        bot.reply_to(message, f"❌ Сталася помилка: {str(e)}")

@bot.message_handler(commands=['help'])
def help_command(message):
    """Показати допомогу"""
    if message.chat.id != ALLOWED_CHAT_ID:
        bot.reply_to(message, "❌ Доступ заборонено!")
        return

    help_text = (
        "🤖 Допомога по використанню бота\n\n"
        "📋 Доступні команди:\n\n"
        "/start - Почати роботу з ботом\n"
        "/prices - Переглянути поточні ціни\n"
        "/set_price <номер> <ціна> - Змінити ціну квартири\n"
        "/help - Показати цю допомогу\n\n"
        "📝 Формати цін:\n"
        "• 85€\n"
        "• 2500₴\n"
        "• $100\n\n"
        "💡 Приклади:\n"
        "/set_price 1 90€\n"
        "/set_price 2 2800₴\n"
        "/set_price 3 $120\n\n"
        "🔒 Бот працює тільки для авторизованих користувачів"
    )
    bot.reply_to(message, help_text)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    """Обробник callback запитів від inline кнопок"""
    if call.message.chat.id != ALLOWED_CHAT_ID:
        bot.answer_callback_query(call.id, "❌ Доступ заборонено!")
        return

    if call.data == "show_prices":
        prices = get_current_prices()
        if prices:
            markup = types.InlineKeyboardMarkup()
            btn_back = types.InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")
            markup.add(btn_back)

            response = (
                "🏠 Поточні ціни на квартири:\n\n"
                f"1️⃣ Квартира 1: {prices['apartament1']}\n"
                f"2️⃣ Квартира 2: {prices['apartament2']}\n"
                f"3️⃣ Квартира 3: {prices['apartament3']}\n\n"
                "💡 Натисніть кнопку нижче, щоб повернутися до головного меню."
            )
            bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=response,
                                reply_markup=markup)
        else:
            bot.answer_callback_query(call.id, "❌ Помилка отримання цін")

    elif call.data == "set_price_menu":
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_apart1 = types.InlineKeyboardButton("🏠 Квартира 1", callback_data="set_apart1")
        btn_apart2 = types.InlineKeyboardButton("🏠 Квартира 2", callback_data="set_apart2")
        btn_apart3 = types.InlineKeyboardButton("🏠 Квартира 3", callback_data="set_apart3")
        btn_back = types.InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")
        markup.add(btn_apart1, btn_apart2, btn_apart3, btn_back)

        bot.edit_message_text(chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            text="🏠 Оберіть квартиру для зміни ціни:",
                            reply_markup=markup)

    elif call.data.startswith("set_apart"):
        apartment_num = int(call.data[-1])
        msg = bot.send_message(call.message.chat.id,
                             f"💰 Введіть нову ціну для квартири {apartment_num}:\n\n"
                             "📝 Формати: 85€, 2500₴, $100")
        bot.register_next_step_handler(msg, process_price_input, apartment_num)

    elif call.data == "help":
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")
        markup.add(btn_back)

        help_text = (
            "🤖 Допомога по використанню бота\n\n"
            "💰 **Переглянути ціни** - показує поточні ціни всіх квартир\n\n"
            "✏️ **Змінити ціну** - дозволяє оновити ціну для конкретної квартири\n\n"
            "📝 **Формати цін:**\n"
            "• 85€\n"
            "• 2500₴\n"
            "• $100\n\n"
            "🔒 Бот працює тільки для авторизованих користувачів"
        )
        bot.edit_message_text(chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            text=help_text,
                            reply_markup=markup,
                            parse_mode="Markdown")

    elif call.data == "back_to_main":
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_prices = types.InlineKeyboardButton("💰 Переглянути ціни", callback_data="show_prices")
        btn_set_price = types.InlineKeyboardButton("✏️ Змінити ціну", callback_data="set_price_menu")
        btn_help = types.InlineKeyboardButton("❓ Допомога", callback_data="help")
        markup.add(btn_prices, btn_set_price, btn_help)

        bot.edit_message_text(chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            text="👋 Привіт! Я бот для управління цінами на квартири в Аланії.\n\n"
                                 "🏠 Оберіть дію нижче:",
                            reply_markup=markup)

    bot.answer_callback_query(call.id)

def process_price_input(message, apartment_num):
    """Обробляє введену ціну від користувача"""
    if message.chat.id != ALLOWED_CHAT_ID:
        return

    new_price = message.text.strip()

    if update_price(apartment_num, new_price):
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("⬅️ Назад до меню", callback_data="back_to_main")
        markup.add(btn_back)

        bot.send_message(message.chat.id,
                        f"✅ Ціна успішно оновлена!\n\n"
                        f"🏠 Квартира {apartment_num}: {new_price}\n\n"
                        "🔄 Зміни будуть відображені на сайті після перезавантаження сторінки.",
                        reply_markup=markup)

        # Показуємо всі поточні ціни після оновлення
        prices = get_current_prices()
        if prices:
            bot.send_message(message.chat.id,
                           "📊 Оновлені ціни:\n\n"
                           f"1️⃣ Квартира 1: {prices['apartament1']}\n"
                           f"2️⃣ Квартира 2: {prices['apartament2']}\n"
                           f"3️⃣ Квартира 3: {prices['apartament3']}")
    else:
        markup = types.InlineKeyboardMarkup()
        btn_retry = types.InlineKeyboardButton("🔄 Спробувати ще раз", callback_data=f"set_apart{apartment_num}")
        btn_back = types.InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")
        markup.add(btn_retry, btn_back)

        bot.send_message(message.chat.id,
                        "❌ Помилка оновлення ціни. Спробуйте ще раз.",
                        reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def unknown_command(message):
    """Обробник невідомих команд"""
    if message.chat.id != ALLOWED_CHAT_ID:
        return

    markup = types.InlineKeyboardMarkup()
    btn_menu = types.InlineKeyboardButton("🏠 Головне меню", callback_data="back_to_main")
    markup.add(btn_menu)

    bot.reply_to(message,
        "❓ Невідома команда!\n\n"
        "📋 Натисніть кнопку нижче для повернення до головного меню:",
        reply_markup=markup
    )

def main():
    """Головна функція для запуску бота"""
    print("🤖 Бот запущений! Натисніть Ctrl+C для зупинки.")
    bot.polling(none_stop=True, interval=0)

if __name__ == '__main__':
    main()
