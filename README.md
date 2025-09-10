# Apartaments Alanya - Динамічні ціни з бази даних

## Опис проекту

Це веб-сайт для оренди квартир в Аланії з можливістю динамічного завантаження цін з бази даних SQLite. Ціни для кожного апартаменту зберігаються в таблиці `prices` та автоматично відображаються на сайті.

## Структура файлів

- `index.html` - головна сторінка сайту
- `style.css` - стилі сайту
- `script.js` - JavaScript для функціональності та завантаження цін
- `animations.css` - додаткові анімації
- `app.py` - Flask сервер для API
- `setup_database.py` - скрипт для налаштування бази даних
- `bot.py` - Telegram бот для управління цінами
- `requirements.txt` - залежності Python
- `database.db` - файл бази даних SQLite

## Налаштування та запуск

### 1. Налаштування бази даних

Запустіть скрипт для створення таблиці та додавання тестових даних:

```bash
python setup_database.py
```

### 2. Встановлення залежностей

```bash
pip install -r requirements.txt
```

Або встановіть окремо:
```bash
pip install flask pyTelegramBotAPI
```

### 3. Запуск веб-сервера

```bash
python app.py
```

Сервер буде запущений на `http://localhost:5000`

### 4. Запуск Telegram бота (в окремому терміналі)

```bash
python bot.py
```

Бот буде доступний у Telegram за вашим токеном

### 5. Відкриття сайту

Відкрийте браузер та перейдіть на `http://localhost:5000`

## Telegram бот

Бот дозволяє керувати цінами на квартири через Telegram з інтуїтивним інтерфейсом кнопок:

### Функції бота:
- **💰 Переглянути ціни** - показує поточні ціни всіх квартир
- **✏️ Змінити ціну** - інтерактивне меню для вибору квартири та введення нової ціни
- **❓ Допомога** - інформація про використання бота

### Як використовувати:
1. Напишіть `/start` або просто почніть спілкування з ботом
2. Натисніть на кнопки для навігації по меню
3. Для зміни ціни оберіть квартиру та введіть нову ціну в чат
4. Бот підтвердить успішне оновлення та покаже всі поточні ціни

### Приклади форматів цін:
- €85/ніч
- ₴2500/ніч
- $100/night

### Безпека:
Бот працює тільки для авторизованих користувачів (ваш chat ID: 5993122611)

## Структура бази даних

### Таблиця `prices`

| Стовпець     | Тип    | Опис                    |
|--------------|--------|-------------------------|
| id          | INTEGER | Первинний ключ         |
| Apartament1 | TEXT   | Ціна першого апартаменту |
| Apartament2 | TEXT   | Ціна другого апартаменту |
| Apartament3 | TEXT   | Ціна третього апартаменту |

### Приклад даних

```sql
INSERT INTO prices (Apartament1, Apartament2, Apartament3)
VALUES ('€85/ніч', '€70/ніч', '€120/ніч');
```

## API Endpoints

### GET /api/prices

Повертає ціни у форматі JSON:

```json
{
  "apartament1": "€85/ніч",
  "apartament2": "€70/ніч",
  "apartament3": "€120/ніч"
}
```

## Як це працює

1. **Завантаження сторінки**: При завантаженні `index.html` виконується `script.js`
2. **Запит до API**: JavaScript робить запит до `/api/prices` на Flask сервері
3. **Отримання даних**: Сервер зчитує дані з таблиці `prices` в SQLite
4. **Оновлення HTML**: JavaScript оновлює елементи з класами `.apartamentPrice` новими цінами

## Код приклади

### Підключення до SQLite в Python

```python
import sqlite3

def get_prices():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT Apartament1, Apartament2, Apartament3 FROM prices LIMIT 1")
    row = cursor.fetchone()

    if row:
        prices = {
            'apartament1': row[0],
            'apartament2': row[1],
            'apartament3': row[2]
        }

    conn.close()
    return prices
```

### Завантаження цін через JavaScript

```javascript
function loadPricesFromDatabase() {
  fetch('/api/prices')
    .then(response => response.json())
    .then(data => {
      updateApartmentPrices(data);
    })
    .catch(error => {
      console.error('Error loading prices:', error);
    });
}

function updateApartmentPrices(prices) {
  const priceElements = document.querySelectorAll('.apartamentPrice');
  priceElements.forEach((element, index) => {
    if (index === 0 || index === 1) {
      element.textContent = prices.apartament1;
    } else if (index === 2 || index === 3) {
      element.textContent = prices.apartament2;
    } else {
      element.textContent = prices.apartament3;
    }
  });
}
```

## Налаштування цін

Для зміни цін оновіть дані в таблиці `prices`:

```python
import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute('''
    UPDATE prices
    SET Apartament1 = ?, Apartament2 = ?, Apartament3 = ?
    WHERE id = 1
''', ('€90/ніч', '€75/ніч', '€130/ніч'))

conn.commit()
conn.close()
```

Після оновлення цін перезавантажте сторінку сайту - ціни будуть автоматично оновлені.

## Особливості реалізації

- ✅ Не змінює дизайн та верстку сайту
- ✅ Не змінює інший функціонал (слайдери, форми, стилі)
- ✅ Використовує тільки дані з таблиці `prices`
- ✅ Автоматичне оновлення цін при завантаженні сторінки
- ✅ Graceful fallback на дефолтні значення при помилках
- ✅ Підтримка кількох екземплярів цін на сторінці
- ✅ Telegram бот для управління цінами

## Troubleshooting

### Проблема: Ціни не оновлюються
**Рішення**: Переконайтеся, що:
1. Flask сервер запущений (`python app.py`)
2. База даних `database.db` існує та містить таблицю `prices`
3. В таблиці є хоча б один рядок з даними

### Проблема: Помилка підключення до бази даних
**Рішення**: Перевірте, чи встановлений sqlite3 та чи є права на читання файлу `database.db`

### Проблема: API повертає помилку
**Рішення**: Перевірте консоль браузера на наявність помилок та логи Flask сервера

### Проблема: Бот не працює
**Рішення**:
1. Перевірте токен бота
2. Переконайтеся, що chat ID правильний
3. Перевірте підключення до інтернету
4. Запустіть бота в окремому терміналі
