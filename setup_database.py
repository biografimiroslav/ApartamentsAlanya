import sqlite3

def setup_database():
    """Створює таблицю prices та додає тестові дані"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Створюємо таблицю prices
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY,
            Apartament1 TEXT,
            Apartament2 TEXT,
            Apartament3 TEXT
        )
    ''')

    # Додаємо тестові дані (якщо таблиця порожня)
    cursor.execute("SELECT COUNT(*) FROM prices")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO prices (Apartament1, Apartament2, Apartament3)
            VALUES (?, ?, ?)
        ''', ('85€', '70€', '120€'))

    conn.commit()
    conn.close()
    print("База даних налаштована успішно!")

if __name__ == '__main__':
    setup_database()
