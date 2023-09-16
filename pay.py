import requests
import json
import xml.etree.ElementTree as ET
# URL вашего API-представления
url = 'http://13.53.177.204//init_payment/'
url = 'http://13.53.177.204/meetings/3'
# Здесь укажите свои данные
data = {
    'professor_id': '1',
    'time_slots': ['2023-07-20T14:30:00', '2023-07-21T15:00:00'],
    'amount': 3233,
    'service': 'math'
}

headers = {
    'Authorization': 'Token de4e43c3ad218159ea0c872a33e9072ec85268e9',  # Если ваше API требует аутентификацию, замените YOUR_ACCESS_TOKEN на ваш токен
    'Content-Type': 'application/json'
}

response = requests.get(url, headers=headers)



#print(response.status_code)
#json_response = response.json()
print(response.text)

# xml_str = ''.join(json_response['payment_data'])
# root = ET.fromstring(xml_str)
# pg_redirect_url = root.find('pg_redirect_url').text
# print(pg_redirect_url)


# import urllib.parse

# encoded_description = "%D0%9D%D0%BE%D0%BC%D0%B5%D1%80+%D0%BA%D1%80%D0%B5%D0%B4%D0%B8%D1%82%D0%BD%D0%BE%D0%B9+%D0%BA%D0%B0%D1%80%D1%82%D1%8B+%D0%BE%D1%82%D1%81%D1%83%D1%82%D1%81%D1%82%D0%B2%D1%83%D0%B5%D1%82+%D0%B8%D0%BB%D0%B8+%D0%BF%D1%83%D1%81%D1%82."

# decoded_description = urllib.parse.unquote(encoded_description)
# print(decoded_description)

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

# import requests

# # URL вашего эндпоинта
# url = 'http://13.53.177.204/check_payment/'

# # Данные, которые вы хотите отправить
# data = {
#     'payment_id': '3',  # Убедитесь, что у вас есть платеж с этим ID в базе данных
#     'status': 'success'
# }

# # Отправка POST-запроса
# response = requests.post(url, data=data)

# # Вывод ответа
# print(response.status_code)
# print(response.text)
