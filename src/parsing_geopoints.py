import requests
import pandas as pd
import time
import yaml

with open('../text.yaml', 'r') as file:
    data = yaml.safe_load(file)

API_KEY = data['API_KEY']

df = pd.read_csv("../output.csv")

for i, address in enumerate(df["Адрес"]):
    values = []
    print(f"Обрабатываю {i+1}: {address}")

    url = "https://geocode-maps.yandex.ru/v1/"
    params = {
        "apikey": API_KEY,
        "geocode": address,
        "format": "json"
    }

    try:
        r = requests.get(url, params=params, timeout=5)

        data = r.json()

        members = data["response"]["GeoObjectCollection"]["featureMember"]

        if members:
            pos = members[0]["GeoObject"]["Point"]["pos"]
            lon, lat = map(float, pos.split())   # широта, долгота
        else:
            lat, lon = None, None

    except Exception as e:
        print("Ошибка:", e)
        lat, lon = None, None

    coordinates = [lat, lon] # словарь для геоточек
    values.append([address, coordinates])

    time.sleep(0.05)

    result = pd.DataFrame(values, columns=["Адрес", "Координаты"])

    if i == 0:
        result.to_csv("coordinates.csv", mode='a', index=False, encoding="utf-8") # содержит названия колонок
    else:
        result.to_csv("coordinates.csv", mode='a', header=False, index=False, encoding="utf-8") # не содержит названия колонок

