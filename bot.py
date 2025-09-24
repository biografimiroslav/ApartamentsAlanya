import sqlite3
import telebot
from telebot import types
from datetime import datetime
from typing import Optional

# Bot configuration
BOT_TOKEN = '8253586903:AAFJGQehaFg1Rm7m1k7VO7vLEB57R6T0fi4'
# Первинний власник/суперадмін (його chat_id буде додано в таблицю admins під час ініціалізації)
ALLOWED_CHAT_ID = 5993122611

bot = telebot.TeleBot(BOT_TOKEN)
DB_PATH = 'database.db'

# --------------------  DB helpers for admins  --------------------
def init_db():
    """Створює потрібні таблиці якщо їх нема та додає первинного адміна
    а також гарантує початкові рядки для prices та phones"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # таблиця адмінів
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                chat_id INTEGER PRIMARY KEY,
                username TEXT,
                added_by INTEGER,
                added_at TEXT
            )
        ''')

        # таблиця цін (якщо структура інша у вашому реальному проєкті — підлаштуйте)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prices (
                id INTEGER PRIMARY KEY,
                Apartament1 TEXT,
                Apartament2 TEXT,
                Apartament3 TEXT
            )
        ''')
        # переконаємось, що існує хоча б один рядок з id=1
        cursor.execute('SELECT 1 FROM prices WHERE id = 1')
        if cursor.fetchone() is None:
            cursor.execute('INSERT INTO prices (id, Apartament1, Apartament2, Apartament3) VALUES (1, ?, ?, ?)',
                           ('85€', '100€', '120€'))

        # таблиця телефонів
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS phones (
                id INTEGER PRIMARY KEY,
                phone_number TEXT
            )
        ''')
        cursor.execute('SELECT 1 FROM phones WHERE id = 1')
        if cursor.fetchone() is None:
            cursor.execute('INSERT INTO phones (id, phone_number) VALUES (1, ?)', ('+380660000000',))

        # таблиця відгуків
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                review_text TEXT
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


def add_admin_db(chat_id: int, username: Optional[str], added_by: int) -> bool:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO admins (chat_id, username, added_by, added_at) VALUES (?,?,?,?)',
                       (chat_id, username, added_by, datetime.utcnow().isoformat()))
        conn.commit()
        # переконаємось що адмін тепер є
        cursor.execute('SELECT 1 FROM admins WHERE chat_id = ?', (chat_id,))
        exists = cursor.fetchone() is not None
        return exists
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
        cursor.execute("SELECT Apartament1, Apartament2, Apartament3 FROM prices WHERE id = 1 LIMIT 1")
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
    if str(apartment_num) not in ('1', '2', '3'):
        print(f"Невірний номер квартири: {apartment_num}")
        return False
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        column_name = f"Apartament{apartment_num}"
        # назва колонки фіксована у коді => ризик ін'єкції мінімальний
        cursor.execute(f"UPDATE prices SET {column_name} = ? WHERE id = 1", (new_price,))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Помилка оновлення ціни: {e}")
        return False


# --------------------  Phone helpers  --------------------
def get_phone():
    """Отримати поточний номер телефону"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT phone_number FROM phones WHERE id = 1 LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    except sqlite3.Error as e:
        print(f"Помилка отримання телефону: {e}")
        return None


def update_phone(new_phone):
    """Оновити номер телефону"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE phones SET phone_number = ? WHERE id = 1", (new_phone,))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Помилка оновлення телефону: {e}")
        return False


# --------------------  Reviews helpers  --------------------

def get_reviews():
    """Отримати всі відгуки"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, review_text FROM reviews")
        rows = cursor.fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"Помилка отримання відгуків: {e}")
        return []


def add_review(review_text):
    """Додати новий відгук"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO reviews (review_text) VALUES (?)", (review_text,))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Помилка додавання відгуку: {e}")
        return False


def delete_review(review_id):
    """Видалити відгук за ID"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reviews WHERE id = ?", (review_id,))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Помилка видалення відгуку: {e}")
        return False


# --------------------  Helper for safe answering callback queries  --------------------
def safe_answer_callback(call, text: Optional[str] = None, show_alert: bool = False):
    try:
        # відповідаємо коротко — якщо помилка (наприклад, "query is too old") — ігноруємо
        bot.answer_callback_query(call.id, text=text, show_alert=show_alert)
    except Exception:
        pass


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
    btn_phone = types.InlineKeyboardButton("📞 Змінити телефон", callback_data="set_phone")
    btn_reviews = types.InlineKeyboardButton("💬 Керувати відгуками", callback_data="manage_reviews")
    btn_help = types.InlineKeyboardButton("❓ Допомога", callback_data="help")
    markup.add(btn_prices, btn_set_price)
    markup.add(btn_phone, btn_reviews)
    markup.add(btn_help)

    # Кнопка керування адмінами бачить тільки адмін
    btn_manage_admins = types.InlineKeyboardButton("🔐 Керувати адмінами", callback_data="manage_admins")
    markup.add(btn_manage_admins)

    bot.reply_to(message,
        "👋 Привіт! Я бот для управління сайтом квартир в Аланії.\n\n"
        "🏠 Оберіть дію нижче:",
        reply_markup=markup
    )


# Виніс повторювані меню у окремі функції для чистоти

def show_main_menu(chat_id, message_id=None):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_prices = types.InlineKeyboardButton("💰 Переглянути ціни", callback_data="show_prices")
    btn_set_price = types.InlineKeyboardButton("✏️ Змінити ціну", callback_data="set_price_menu")
    btn_phone = types.InlineKeyboardButton("📞 Змінити телефон", callback_data="set_phone")
    btn_reviews = types.InlineKeyboardButton("💬 Керувати відгуками", callback_data="manage_reviews")
    btn_help = types.InlineKeyboardButton("❓ Допомога", callback_data="help")
    markup.add(btn_prices, btn_set_price)
    markup.add(btn_phone, btn_reviews)
    markup.add(btn_help)
    markup.add(types.InlineKeyboardButton("🔐 Керувати адмінами", callback_data="manage_admins"))

    text = "👋 Привіт! Я бот для управління сайтом квартир в Аланії.\n\n" \
           "🏠 Оберіть дію нижче:"
    if message_id:
        try:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=markup)
            return
        except Exception:
            pass
    bot.send_message(chat_id, text, reply_markup=markup)


def show_manage_admins(chat_id, message_id=None):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("➕ Додати адміна", callback_data="add_admin"),
        types.InlineKeyboardButton("➖ Видалити адміна", callback_data="remove_admin"),
        types.InlineKeyboardButton("📋 Показати адмінів", callback_data="list_admins"),
        types.InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")
    )
    text = "🔐 Керування адмінами:"
    if message_id:
        try:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=markup)
            return
        except Exception:
            pass
    bot.send_message(chat_id, text, reply_markup=markup)


def show_manage_reviews(chat_id, message_id=None):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("➕ Додати відгук", callback_data="add_review"),
        types.InlineKeyboardButton("➖ Видалити відгук", callback_data="delete_review"),
        types.InlineKeyboardButton("📋 Показати відгуки", callback_data="list_reviews"),
        types.InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")
    )
    text = "💬 Керування відгуками:"
    if message_id:
        try:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=markup)
            return
        except Exception:
            pass
    bot.send_message(chat_id, text, reply_markup=markup)


def show_delete_reviews_menu(call):
    reviews = get_reviews()
    if not reviews:
        safe_answer_callback(call, "Немає відгуків для видалення.")
        return
    markup = types.InlineKeyboardMarkup()
    for r_id, text in reviews:
        short_text = text[:50] + "..." if len(text) > 50 else text
        markup.add(types.InlineKeyboardButton(f"Видалити: {short_text}", callback_data=f"del_rev_{r_id}"))
    markup.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="manage_reviews"))
    try:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text="💬 Оберіть відгук для видалення:",
                              reply_markup=markup)
    except Exception:
        bot.send_message(call.message.chat.id, "💬 Оберіть відгук для видалення:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    # Перевірка права доступу
    if not is_admin(call.message.chat.id):
        safe_answer_callback(call, "❌ Доступ заборонено!", show_alert=True)
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
            try:
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text=response,
                                      reply_markup=markup)
            except Exception:
                bot.send_message(call.message.chat.id, response, reply_markup=markup)
        else:
            safe_answer_callback(call, "❌ Помилка отримання цін")
        return

    # Меню зміни ціни
    if call.data == "set_price_menu":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("🏠 Квартира 1", callback_data="set_apart1"),
            types.InlineKeyboardButton("🏠 Квартира 2", callback_data="set_apart2"),
            types.InlineKeyboardButton("🏠 Квартира 3", callback_data="set_apart3"),
            types.InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")
        )
        try:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="🏠 Оберіть квартиру для зміни ціни:",
                                  reply_markup=markup)
        except Exception:
            bot.send_message(call.message.chat.id, "🏠 Оберіть квартиру для зміни ціни:", reply_markup=markup)
        return

    # Введення нової ціни
    if call.data.startswith("set_apart"):
        apartment_num = int(call.data[-1])
        msg = bot.send_message(call.message.chat.id,
                               f"💰 Введіть нову ціну для квартири {apartment_num}:\n📝 Формати: 85€, 2500₴, $100")
        bot.register_next_step_handler(msg, process_price_input, apartment_num)
        safe_answer_callback(call)
        return

    # Допомога
    if call.data == "help":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main"))
        help_text = (
            "🤖 Допомога по використанню бота\n\n"
            "💰 Переглянути ціни - показує поточні ціни всіх квартир\n"
            "✏️ Змінити ціну - дозволяє оновити ціну для конкретної квартири\n"
            "📞 Змінити телефон - дозволяє оновити номер телефону\n"
            "💬 Керувати відгуками - додавати, видаляти, переглядати відгуки\n"
            "📝 Формати цін: 85€, 2500₴, $100\n"
            "🔒 Бот працює тільки для авторизованих користувачів"
        )
        try:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text=help_text,
                                  reply_markup=markup)
        except Exception:
            bot.send_message(call.message.chat.id, help_text, reply_markup=markup)
        return

    # Меню керування адмінами
    if call.data == "manage_admins":
        show_manage_admins(call.message.chat.id, message_id=call.message.message_id)
        return

    if call.data == "list_admins":
        rows = get_admins()
        if not rows:
            safe_answer_callback(call, "Немає адмінів у базі.")
            return
        text = '📋 Список адмінів:\n\n'
        for r in rows:
            chat_id, username, added_by, added_at = r
            text += f"• {chat_id}"
            if username:
                text += f" ({username})"
            text += f" — доданий: {added_at}\n"
        safe_answer_callback(call)
        bot.send_message(call.message.chat.id, text)
        return

    if call.data == "add_admin":
        msg = bot.send_message(call.message.chat.id, "Введіть chat_id або @username нового адміна:")
        bot.register_next_step_handler(msg, process_add_admin, call.from_user.id)
        safe_answer_callback(call)
        return

    if call.data == "remove_admin":
        msg = bot.send_message(call.message.chat.id, "Введіть chat_id або @username адміна, якого потрібно видалити:")
        bot.register_next_step_handler(msg, process_remove_admin, call.from_user.id)
        safe_answer_callback(call)
        return

    # Зміна телефону
    if call.data == "set_phone":
        current_phone = get_phone()
        msg = bot.send_message(call.message.chat.id, f"📞 Поточний телефон: {current_phone or 'Не встановлено'}\n\nВведіть новий номер телефону:")
        bot.register_next_step_handler(msg, process_phone_input)
        safe_answer_callback(call)
        return

    # Меню керування відгуками
    if call.data == "manage_reviews":
        show_manage_reviews(call.message.chat.id, message_id=call.message.message_id)
        return

    if call.data == "add_review":
        msg = bot.send_message(call.message.chat.id, "💬 Введіть текст нового відгуку:")
        bot.register_next_step_handler(msg, process_add_review)
        safe_answer_callback(call)
        return

    if call.data == "delete_review":
        # показуємо меню видалення відгуків
        show_delete_reviews_menu(call)
        safe_answer_callback(call)
        return

    if call.data == "list_reviews":
        reviews = get_reviews()
        if not reviews:
            safe_answer_callback(call, "Немає відгуків.")
            return
        text = "💬 Список відгуків:\n\n"
        for r_id, rev_text in reviews:
            text += f"{r_id}. {rev_text}\n\n"
        safe_answer_callback(call)
        bot.send_message(call.message.chat.id, text)
        return

    if call.data.startswith("del_rev_"):
        try:
            r_id = int(call.data.split("_")[2])
        except Exception:
            safe_answer_callback(call, "Некоректний ID відгуку.")
            return
        if delete_review(r_id):
            safe_answer_callback(call, "Відгук видалено.")
            # Оновлюємо меню видалення
            show_delete_reviews_menu(call)
        else:
            safe_answer_callback(call, "Помилка видалення.")
        return

    # Повернутись в головне меню
    if call.data == "back_to_main":
        show_main_menu(call.message.chat.id, message_id=call.message.message_id)
        return


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


# --------------------  Handlers for phone and reviews flows  --------------------

def process_phone_input(message):
    """Обробляє введення нового телефону"""
    if not is_admin(message.chat.id):
        return

    new_phone = message.text.strip()
    if update_phone(new_phone):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("⬅️ Назад до меню", callback_data="back_to_main"))
        bot.send_message(message.chat.id,
                         f"✅ Телефон успішно оновлений!\n\n📞 Новий телефон: {new_phone}\n🔄 Зміни будуть відображені на сайті після перезавантаження сторінки.",
                         reply_markup=markup)
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("🔄 Спробувати ще раз", callback_data="set_phone"),
            types.InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")
        )
        bot.send_message(message.chat.id,
                         "❌ Помилка оновлення телефону. Спробуйте ще раз.",
                         reply_markup=markup)


def process_add_review(message):
    """Обробляє додавання нового відгуку"""
    if not is_admin(message.chat.id):
        return

    review_text = message.text.strip()
    if add_review(review_text):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("⬅️ Назад до меню", callback_data="back_to_main"))
        bot.send_message(message.chat.id,
                         f"✅ Відгук успішно додано!\n\n💬 Текст: {review_text}\n🔄 Зміни будуть відображені на сайті після перезавантаження сторінки.",
                         reply_markup=markup)
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("🔄 Спробувати ще раз", callback_data="add_review"),
            types.InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")
        )
        bot.send_message(message.chat.id,
                         "❌ Помилка додавання відгуку. Спробуйте ще раз.",
                         reply_markup=markup)


def main():
    init_db()
    print("🤖 Бот запущений! Натисніть Ctrl+C для зупинки.")
    bot.polling(none_stop=True, interval=0)


if __name__ == '__main__':
    main()
