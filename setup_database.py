import sqlite3
from datetime import datetime

DB_PATH = 'database.db'
# Змініть на ваш початковий адмінський chat_id, якщо потрібно
INITIAL_ADMIN_CHAT_ID = 5993122611


def setup_database(db_path: str = DB_PATH, initial_admin: int = INITIAL_ADMIN_CHAT_ID):
    """Створює таблиці `prices` та `admins` і додає тестові дані/першого адміна.

    - Гарантує, що в таблиці `prices` є рядок з id=1 (бот очікує наявність такого рядка).
    - Створює таблицю `admins` і додає `initial_admin` якщо його ще нема.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Таблиця prices
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prices (
                id INTEGER PRIMARY KEY,
                Apartament1 TEXT,
                Apartament2 TEXT,
                Apartament3 TEXT
            )
        ''')

        # Переконатися, що є щонайменше один рядок з id=1
        cursor.execute('SELECT COUNT(*) FROM prices')
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.execute('''
                INSERT INTO prices (id, Apartament1, Apartament2, Apartament3)
                VALUES (1, ?, ?, ?)
            ''', ('85€', '70€', '120€'))
            print('Вставлено тестові ціни в prices (id=1).')
        else:
            # Якщо є записи, переконаємось, що рядок з id=1 існує
            cursor.execute('SELECT 1 FROM prices WHERE id = 1')
            if cursor.fetchone() is None:
                # беремо перший рядок і ставимо його як id=1 (щоб уникнути конфліктів)
                cursor.execute('SELECT rowid, Apartament1, Apartament2, Apartament3 FROM prices LIMIT 1')
                row = cursor.fetchone()
                if row:
                    _, a1, a2, a3 = row
                    cursor.execute('INSERT INTO prices (id, Apartament1, Apartament2, Apartament3) VALUES (1,?,?,?)',
                                   (a1 or '85€', a2 or '70€', a3 or '120€'))
                    print('Додано рядок id=1 у таблицю prices на основі існуючого запису.')

        # Таблиця phones для номера телефону (один номер для всіх мов)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS phones (
                id INTEGER PRIMARY KEY,
                phone_number TEXT NOT NULL
            )
        ''')

        # Таблиця reviews для відгуків (спільні для всіх мов)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                review_text TEXT NOT NULL
            )
        ''')

        # Таблиця admins
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                chat_id INTEGER PRIMARY KEY,
                username TEXT,
                added_by INTEGER,
                added_at TEXT
            )
        ''')

        # Додаємо тестовий номер телефону (один для всіх мов)
        cursor.execute('INSERT OR IGNORE INTO phones (id, phone_number) VALUES (1, ?)', ('+38 (012) 345-67-89',))
        print('Додано тестовий номер телефону.')

        # Додаємо тестові відгуки (спільні для всіх мов)
        reviews_data = [
            'Really liked it! Everything fast and high quality.',
            'Great service, I\'ll contact again.',
            'Everything is great! I recommend to everyone.',
            'Service at a high level!',
            'Prices pleasantly surprised, recommend!',
            'I\'m not a first-time guest, everything is excellent!',
            'Дуже сподобалося! Все швидко та якісно.',
            'Чудовий сервіс, звернуся ще раз.',
            'Все чудово! Рекомендую всім.',
            'Сервіс на високому рівні!',
            'Ціни приємно здивували, рекомендую!',
            'Я не вперше гість, все відмінно!',
            'Velmi se mi líbilo! Vše rychle a kvalitně.',
            'Skvělá služba, ozvu se znovu.',
            'Vše je skvělé! Doporučuji všem.',
            'Služba na vysoké úrovni!',
            'Ceny příjemně překvapily, doporučuji!',
            'Nejsem poprvé host, vše je výborné!',
            'Çok beğendim! Her şey hızlı ve kaliteli.',
            'Harika servis, tekrar başvuracağım.',
            'Her şey harika! Herkese tavsiye ederim.',
            'Hizmet yüksek seviyede!',
            'Fiyatlar hoş bir şekilde şaşırttı, tavsiye ederim!',
            'İlk kez misafir değilim, her şey mükemmel!',
            'Очень понравилось! Всё быстро и качественно.',
            'Отличный сервис, свяжусь ещё раз.',
            'Всё отлично! Рекомендую всем.',
            'Сервис на высоком уровне!',
            'Цены приятно удивили, рекомендую!',
            'Я не в первый раз гость, всё отлично!'
        ]
        for review in reviews_data:
            cursor.execute('INSERT OR IGNORE INTO reviews (review_text) VALUES (?)', (review,))
        print('Додано тестові відгуки.')

        # Додаємо початкового адміна якщо його немає
        cursor.execute('SELECT 1 FROM admins WHERE chat_id = ?', (initial_admin,))
        if cursor.fetchone() is None:
            cursor.execute(
                'INSERT INTO admins (chat_id, username, added_by, added_at) VALUES (?,?,?,?)',
                (initial_admin, None, initial_admin, datetime.utcnow().isoformat())
            )
            print(f'Початковий адмін ({initial_admin}) доданий у таблицю admins.')
        else:
            print(f'Початковий адмін ({initial_admin}) вже присутній у базі.')

        conn.commit()
    except sqlite3.Error as e:
        print(f'Помилка роботи з базою: {e}')
    finally:
        conn.close()


if __name__ == '__main__':
    setup_database()
    print('Налаштування бази даних завершено.')
