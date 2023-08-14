import requests
import json

# URL вашего API-представления
url = 'http://127.0.0.1:8000/init_payment/'

# Здесь укажите свои данные
data = {
    'professor_id': '2',
    'time_slots': ['2023-07-20T14:30:00', '2023-07-21T15:00:00'],
    'amount': 2100,
    'service': 'ServiceName'
}

headers = {
    'Authorization': 'Token 2b979d442373b980c517e489fd667222c9cfb9e0',  # Если ваше API требует аутентификацию, замените YOUR_ACCESS_TOKEN на ваш токен
    'Content-Type': 'application/json'
}

response = requests.post(url, data=json.dumps(data), headers=headers)

print(response.status_code)
print(response.json())


# import requests
# import json

# # URL вашего API-представления
# url = 'http://127.0.0.1:8000/professors/'

# # Здесь укажите свои данные
# data = {
#     'professor_id': '1',
#     'time_slots': ['2023-07-20T14:30:00', '2023-07-21T15:00:00'],
#     'amount': 100,
#     'service': 'ServiceName'
# }

# headers = {
#     'Authorization': 'Token 2b979d442373b980c517e489fd667222c9cfb9e0',  # Если ваше API требует аутентификацию, замените YOUR_ACCESS_TOKEN на ваш токен
#     'Content-Type': 'application/json'}
# response = requests.get(url,  headers=headers)
# print(response.json())