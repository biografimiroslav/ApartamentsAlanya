import sqlite3
import telebot
from telebot import types

# Bot configuration
BOT_TOKEN = '8253586903:AAFJGQehaFg1Rm7m1k7VO7vLEB57R6T0fi4'
ALLOWED_CHAT_ID = 5993122611

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
    """Головне меню"""
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

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.message.chat.id != ALLOWED_CHAT_ID:
        bot.answer_callback_query(call.id, "❌ Доступ заборонено!")
        return

    # Показати ціни
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
                f"3️⃣ Квартира 3: {prices['apartament3']}"
            )
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text=response,
                                  reply_markup=markup)
        else:
            bot.answer_callback_query(call.id, "❌ Помилка отримання цін")

    # Меню зміни ціни
    elif call.data == "set_price_menu":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("🏠 Квартира 1", callback_data="set_apart1"),
            types.InlineKeyboardButton("🏠 Квартира 2", callback_data="set_apart2"),
            types.InlineKeyboardButton("🏠 Квартира 3", callback_data="set_apart3"),
            types.InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")
        )
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text="🏠 Оберіть квартиру для зміни ціни:",
                              reply_markup=markup)

    # Введення нової ціни
    elif call.data.startswith("set_apart"):
        apartment_num = int(call.data[-1])
        msg = bot.send_message(call.message.chat.id,
                               f"💰 Введіть нову ціну для квартири {apartment_num}:\n📝 Формати: 85€, 2500₴, $100")
        bot.register_next_step_handler(msg, process_price_input, apartment_num)

    # Допомога
    elif call.data == "help":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main"))
        help_text = (
            "🤖 Допомога по використанню бота\n\n"
            "💰 Переглянути ціни - показує поточні ціни всіх квартир\n"
            "✏️ Змінити ціну - дозволяє оновити ціну для конкретної квартири\n"
            "📝 Формати цін: 85€, 2500₴, $100\n"
            "🔒 Бот працює тільки для авторизованих користувачів"
        )
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=help_text,
                              reply_markup=markup)

    # Повернутись в головне меню
    elif call.data == "back_to_main":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("💰 Переглянути ціни", callback_data="show_prices"),
            types.InlineKeyboardButton("✏️ Змінити ціну", callback_data="set_price_menu"),
            types.InlineKeyboardButton("❓ Допомога", callback_data="help")
        )
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
        markup.add(types.InlineKeyboardButton("⬅️ Назад до меню", callback_data="back_to_main"))

        bot.send_message(message.chat.id,
                         f"✅ Ціна успішно оновлена!\n\n"
                         f"🏠 Квартира {apartment_num}: {new_price}\n🔄 Зміни будуть відображені на сайті після перезавантаження сторінки.",
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
        markup.add(
            types.InlineKeyboardButton("🔄 Спробувати ще раз", callback_data=f"set_apart{apartment_num}"),
            types.InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")
        )
        bot.send_message(message.chat.id,
                         "❌ Помилка оновлення ціни. Спробуйте ще раз.",
                         reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def unknown_command(message):
    """Відловлюємо будь-які текстові повідомлення, які не обробляються"""
    if message.chat.id != ALLOWED_CHAT_ID:
        return

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🏠 Головне меню", callback_data="back_to_main"))
    bot.reply_to(message,
                 "❓ Використовуйте кнопки для навігації по меню бота.",
                 reply_markup=markup)

def main():
    print("🤖 Бот запущений! Натисніть Ctrl+C для зупинки.")
    bot.polling(none_stop=True, interval=0)

if __name__ == '__main__':
    main()
