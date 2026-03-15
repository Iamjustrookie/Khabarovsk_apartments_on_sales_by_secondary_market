import pandas as pd

common_data = pd.read_csv('output.csv', encoding='utf-8') # спарсенные данные
coordinates = pd.read_csv('coordinates.csv', encoding='utf-8') # api геоточек

coordinates['Адрес'] = coordinates['Адрес'].drop_duplicates()

data = pd.merge(common_data, coordinates, on='Адрес', how='left')

data = data[data['Цена за квадратный метр'] < 400000] # избавляемся от явных выбросов по цене
data.to_csv('khabarovsk_flats_domclick.csv', encoding='utf-8')
print(len(data))
