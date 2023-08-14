import psycopg2

# Параметры подключения
db_params = {
    'host': 'your_host',
    'dbname': 'your_dbname',
    'user': 'your_user',
    'password': 'your_password'
}

# Создание подключения
connection = psycopg2.connect(**db_params)

# Создание курсора
cursor = connection.cursor()

# Выполнение SQL-запросов
cursor.execute('SELECT * FROM your_table')
result = cursor.fetchall()
print(result)

# Закрытие курсора и подключения
cursor.close()
connection.close()
