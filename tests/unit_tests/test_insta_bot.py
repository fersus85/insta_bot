import requests


def test_login():
    response = requests.get('https://www.google.com/')
    print(response)
