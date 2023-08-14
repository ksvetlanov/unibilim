# import requests
# import json

# # URL вашего API-представления
# url = 'http://13.53.177.204//init_payment/'

# # Здесь укажите свои данные
# data = {
#     'professor_id': '1',
#     'time_slots': ['2023-07-20T14:30:00', '2023-07-21T15:00:00'],
#     'amount': 70,
#     'service': 'ServiceName'
# }

# headers = {
#     'Authorization': 'Token 2d00fd8975336f24addbf078130908cb8396690b',  # Если ваше API требует аутентификацию, замените YOUR_ACCESS_TOKEN на ваш токен
#     'Content-Type': 'application/json'
# }

# response = requests.post(url, data=json.dumps(data), headers=headers)

# print(response.status_code)
# print(response.json())


# # import requests
# # import json

# # # URL вашего API-представления
# # url = 'http://13.53.177.204/professors/'

# # # Здесь укажите свои данные
# # data = {
# #     'professor_id': '1',
# #     'time_slots': ['2023-07-20T14:30:00', '2023-07-21T15:00:00'],
# #     'amount': 100,
# #     'service': 'ServiceName'
# # }

# # headers = {
# #     'Authorization': 'Token 2d00fd8975336f24addbf078130908cb8396690b',  # Если ваше API требует аутентификацию, замените YOUR_ACCESS_TOKEN на ваш токен
# #     'Content-Type': 'application/json'}
# # response = requests.get(url,  headers=headers)
# # print(response.json())

import requests

# URL вашего эндпоинта
url = 'http://13.53.177.204/check_payment/'

# Данные, которые вы хотите отправить
data = {
    'payment_id': '2',  # Убедитесь, что у вас есть платеж с этим ID в базе данных
    'status': 'success'
}

# Отправка POST-запроса
response = requests.post(url, data=data)

# Вывод ответа
print(response.status_code)
print(response.text)
