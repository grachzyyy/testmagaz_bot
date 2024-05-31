import sqlite3

# Открываем (или создаем) базу данных users.db
conn = sqlite3.connect('users.db')

# Создаем курсор для выполнения SQL-запросов
c = conn.cursor()

# Создаем таблицу users, если она еще не существует
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    chat_id INTEGER PRIMARY KEYa
)
''')

# Сохраняем изменения и закрываем соединение
conn.commit()
conn.close()
