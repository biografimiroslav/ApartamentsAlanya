import sqlite3
import telebot
from telebot import types
from datetime import datetime

# Bot configuration
BOT_TOKEN = '8253586903:AAFJGQehaFg1Rm7m1k7VO7vLEB57R6T0fi4'
# Первинний власник/суперадмін (його chat_id буде додано в таблицю admins під час ініціалізації)
ALLOWED_CHAT_ID = 5993122611

bot = telebot.TeleBot(BOT_TOKEN)
DB_PATH = 'database.db'

# --------------------  DB helpers for admins  --------------------
def init_db():
    """Створює потрібні таблиці якщо їх нема та додає первинного адміна"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # таблиця для цін вже є у вашому проєкті, тут додаємо таблицю адмінів
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                chat_id INTEGER PRIMARY KEY,
                username TEXT,
                added_by INTEGER,
                added_at TEXT
            )
        ''')
        # Додаємо первинного власника якщо його нема
        cursor.execute('SELECT 1 FROM admins WHERE chat_id = ?', (ALLOWED_CHAT_ID,))
        if cursor.fetchone() is None:
            cursor.execute(
                'INSERT INTO admins (chat_id, username, added_by, added_at) VALUES (?,?,?,?)',
                (ALLOWED_CHAT_ID, None, ALLOWED_CHAT_ID, datetime.utcnow().isoformat())
            )
        conn.commit()
    except sqlite3.Error as e:
        print(f"DB init error: {e}")
    finally:
        conn.close()


def is_admin(chat_id: int) -> bool:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM admins WHERE chat_id = ?', (chat_id,))
        result = cursor.fetchone() is not None
        return result
    except sqlite3.Error as e:
        print(f"is_admin db error: {e}")
        return False
    finally:
        conn.close()


def get_admins():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT chat_id, username, added_by, added_at FROM admins')
        rows = cursor.fetchall()
        return rows
    except sqlite3.Error as e:
        print(f"get_admins db error: {e}")
        return []
    finally:
        conn.close()


def add_admin_db(chat_id: int, username: str | None, added_by: int) -> bool:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO admins (chat_id, username, added_by, added_at) VALUES (?,?,?,?)',
                       (chat_id, username, added_by, datetime.utcnow().isoformat()))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"add_admin db error: {e}")
        return False
    finally:
        conn.close()


def remove_admin_db(chat_id: int) -> bool:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM admins WHERE chat_id = ?', (chat_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"remove_admin db error: {e}")
        return False
    finally:
        conn.close()

# --------------------  Existing price helpers  --------------------

def get_current_prices():
    """Отримати поточні ціни з бази даних з додаванням суфікса"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT Apartament1, Apartament2, Apartament3 FROM prices LIMIT 1")
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'apartament1': str(row[0]) + '/ніч',
                'apartament2': str(row[1]) + '/ніч',
                'apartament3': str(row[2]) + '/ніч'
            }
        return None
    except sqlite3.Error as e:
        print(f"Помилка бази даних: {e}")
        return None


def update_price(apartment_num, new_price):
    """Оновити ціну для конкретної квартири"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        column_name = f"Apartament{apartment_num}"
        cursor.execute(f"UPDATE prices SET {column_name} = ? WHERE id = 1", (new_price,))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Помилка оновлення ціни: {e}")
        return False

# --------------------  Bot handlers  --------------------
@bot.message_handler(commands=['start'])
def start(message):
    """Головне меню"""
    if not is_admin(message.chat.id):
        bot.reply_to(message, "❌ Доступ заборонено!")
        return

    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_prices = types.InlineKeyboardButton("💰 Переглянути ціни", callback_data="show_prices")
    btn_set_price = types.InlineKeyboardButton("✏️ Змінити ціну", callback_data="set_price_menu")
    btn_help = types.InlineKeyboardButton("❓ Допомога", callback_data="help")
    markup.add(btn_prices, btn_set_price, btn_help)

    # Кнопка керування адмінами бачить тільки адмін
    btn_manage_admins = types.InlineKeyboardButton("🔐 Керувати адмінами", callback_data="manage_admins")
    markup.add(btn_manage_admins)

    bot.reply_to(message,
        "👋 Привіт! Я бот для управління цінами на квартири в Аланії.\n\n"
        "🏠 Оберіть дію нижче:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if not is_admin(call.message.chat.id):
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

    # Меню керування адмінами
    elif call.data == "manage_admins":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("➕ Додати адміна", callback_data="add_admin"),
            types.InlineKeyboardButton("➖ Видалити адміна", callback_data="remove_admin"),
            types.InlineKeyboardButton("📋 Показати адмінів", callback_data="list_admins"),
            types.InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")
        )
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text="🔐 Керування адмінами:",
                              reply_markup=markup)

    elif call.data == "list_admins":
        rows = get_admins()
        if not rows:
            bot.answer_callback_query(call.id, "Немає адмінів у базі.")
        else:
            text = '📋 Список адмінів:\n\n'
            for r in rows:
                chat_id, username, added_by, added_at = r
                text += f"• {chat_id}"
                if username:
                    text += f" ({username})"
                text += f" — доданий: {added_at}\n"
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, text)

    elif call.data == "add_admin":
        msg = bot.send_message(call.message.chat.id, "Введіть chat_id або @username нового адміна:")
        bot.register_next_step_handler(msg, process_add_admin, call.from_user.id)

    elif call.data == "remove_admin":
        msg = bot.send_message(call.message.chat.id, "Введіть chat_id або @username адміна, якого потрібно видалити:")
        bot.register_next_step_handler(msg, process_remove_admin, call.from_user.id)

    # Повернутись в головне меню
    elif call.data == "back_to_main":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("💰 Переглянути ціни", callback_data="show_prices"),
            types.InlineKeyboardButton("✏️ Змінити ціну", callback_data="set_price_menu"),
            types.InlineKeyboardButton("❓ Допомога", callback_data="help")
        )
        markup.add(types.InlineKeyboardButton("🔐 Керувати адмінами", callback_data="manage_admins"))
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text="👋 Привіт! Я бот для управління цінами на квартири в Аланії.\n\n"
                                   "🏠 Оберіть дію нижче:",
                              reply_markup=markup)

    bot.answer_callback_query(call.id)


def process_price_input(message, apartment_num):
    """Обробляє введену ціну від користувача"""
    if not is_admin(message.chat.id):
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
    if not is_admin(message.chat.id):
        return

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🏠 Головне меню", callback_data="back_to_main"))
    bot.reply_to(message,
                 "❓ Використовуйте кнопки для навігації по меню бота.",
                 reply_markup=markup)

# --------------------  Handlers for add/remove admin flows  --------------------

def process_add_admin(message, requested_by_id):
    """Обробляє введення для додавання адміна"""
    if not is_admin(message.chat.id):
        return

    text = message.text.strip()
    target_chat_id = None
    target_username = None

    # Якщо ввели @username, спробуємо отримати chat через get_chat
    if text.startswith('@'):
        try:
            chat = bot.get_chat(text)
            target_chat_id = chat.id
            target_username = text
        except Exception as e:
            bot.send_message(message.chat.id, f"Не вдалося знайти користувача за ім'ям {text}. Якщо це приватний користувач — він має спочатку натиснути /start у бота або використайте числовий chat_id.\nПомилка: {e}")
            return
    else:
        # намагаємось перетворити на число
        try:
            target_chat_id = int(text)
        except ValueError:
            bot.send_message(message.chat.id, "Некоректний формат. Введіть числовий chat_id або @username.")
            return

    # Перевіримо, чи вже є такий адмін
    if is_admin(target_chat_id):
        bot.send_message(message.chat.id, "Цей користувач вже є адміном.")
        return

    ok = add_admin_db(target_chat_id, target_username, message.from_user.id)
    if ok:
        bot.send_message(message.chat.id, f"✅ Адмін ({target_chat_id}{' ' + target_username if target_username else ''}) успішно доданий.")
    else:
        bot.send_message(message.chat.id, "❌ Не вдалося додати адміна. Перевірте лог бота.")


def process_remove_admin(message, requested_by_id):
    """Обробляє введення для видалення адміна"""
    if not is_admin(message.chat.id):
        return

    text = message.text.strip()
    target_chat_id = None

    if text.startswith('@'):
        try:
            chat = bot.get_chat(text)
            target_chat_id = chat.id
        except Exception as e:
            bot.send_message(message.chat.id, f"Не вдалося знайти користувача за ім'ям {text}.\nПомилка: {e}")
            return
    else:
        try:
            target_chat_id = int(text)
        except ValueError:
            bot.send_message(message.chat.id, "Некоректний формат. Введіть числовий chat_id або @username.")
            return

    # Не дозволяємо видалити останнього адміна
    admins = get_admins()
    if len(admins) <= 1:
        bot.send_message(message.chat.id, "❌ Неможливо видалити останнього адміна.")
        return

    if not is_admin(target_chat_id):
        bot.send_message(message.chat.id, "Користувач не є адміном.")
        return

    ok = remove_admin_db(target_chat_id)
    if ok:
        bot.send_message(message.chat.id, f"✅ Адмін {target_chat_id} видалений.")
    else:
        bot.send_message(message.chat.id, "❌ Не вдалося видалити адміна. Перевірте лог бота.")


def main():
    init_db()
    print("🤖 Бот запущений! Натисніть Ctrl+C для зупинки.")
    bot.polling(none_stop=True, interval=0)


if __name__ == '__main__':
    main()
