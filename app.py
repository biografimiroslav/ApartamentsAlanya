import sqlite3
from flask import Flask, jsonify, send_from_directory
import os

app = Flask(__name__)

def get_prices(lang='en'):
    """Функція для отримання цін з бази даних SQLite з додаванням суфікса залежно від мови"""
    suffixes = {
        'en': '/night',
        'ua': '/ніч',
        'cz': '/noc',
        'tr': '/gece',
        'ru': '/ночь'
    }
    suffix = suffixes.get(lang, '/night')

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Отримуємо дані з таблиці prices
        cursor.execute("SELECT Apartament1, Apartament2, Apartament3 FROM prices LIMIT 1")
        row = cursor.fetchone()

        if row:
            prices = {
                'apartament1': row[0] + suffix,
                'apartament2': row[1] + suffix,
                'apartament3': row[2] + suffix
            }

        else:
            # Якщо немає даних, використовуємо значення за замовчуванням
            prices = {
                'apartament1': '— €' + suffix,
                'apartament2': '— €' + suffix,
                'apartament3': '— €' + suffix
            }

        conn.close()
        return prices

    except sqlite3.Error as e:
        print(f"Помилка бази даних: {e}")
        return {
            'apartament1': '— €' + suffix,
            'apartament2': '— €' + suffix,
            'apartament3': '— €' + suffix
        }

def get_phone(lang='en'):
    """Функція для отримання номера телефону (один номер для всіх мов)"""
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("SELECT phone_number FROM phones LIMIT 1")
        row = cursor.fetchone()

        conn.close()

        if row:
            return row[0]
        else:
            return '+38 (012) 345-67-89'  # значення за замовчуванням

    except sqlite3.Error as e:
        print(f"Помилка бази даних: {e}")
        return '+38 (012) 345-67-89'

def get_reviews(lang='en'):
    """Функція для отримання відгуків (спільні для всіх мов)"""
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("SELECT review_text FROM reviews")
        rows = cursor.fetchall()

        conn.close()

        if rows:
            return [row[0] for row in rows]
        else:
            # значення за замовчуванням
            return [
                'Дуже сподобалося! Все швидко та якісно.'
            ]

    except sqlite3.Error as e:
        print(f"Помилка бази даних: {e}")
        return [
            'Дуже сподобалося! Все швидко та якісно.',
            'Чудовий сервіс, звернуся ще раз.',
            'Все чудово! Рекомендую всім.',
            'Сервіс на високому рівні!',
            'Ціни приємно здивували, рекомендую!',
            'Я не вперше гість, все відмінно!'
        ]

@app.route('/')
def index():
    """Головна сторінка - завантажуємо HTML файл"""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        return html_content
    except FileNotFoundError:
        return "Помилка: файл index.html не знайдено", 404

@app.route('/<path:filename>')
def serve_static(filename):
    """Служба статичних файлів (CSS, JS, зображення)"""
    root_dir = os.getcwd()
    return send_from_directory(root_dir, filename)

@app.route('/api/prices')
def prices_api():
    """API endpoint для отримання цін"""
    from flask import request
    lang = request.args.get('lang', 'en')
    return jsonify(get_prices(lang))

@app.route('/api/phone')
def phone_api():
    """API endpoint для отримання номера телефону"""
    from flask import request
    lang = request.args.get('lang', 'en')
    phone = get_phone(lang)
    return jsonify({'phone_number': phone})

@app.route('/api/reviews')
def reviews_api():
    """API endpoint для отримання відгуків"""
    from flask import request
    lang = request.args.get('lang', 'en')
    reviews = get_reviews(lang)
    return jsonify({'reviews': reviews})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
