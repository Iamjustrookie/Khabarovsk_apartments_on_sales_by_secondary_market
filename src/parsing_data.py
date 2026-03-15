from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc # маска
from selenium.webdriver.common.by import By
import time
import random
import pandas as pd

# изменение типа признака на float
def convert_to_float(value1, default=None):
    if value1 is None or value1 == '':
        return default
    else:
        return float(value1.replace(' ', '').replace('м2', '').replace(',', '.'))

# изменение типа признака на int
def convert_to_int(value2):
    if value2 is None or value2 == '':
        return None
    else:
        return int(value2.replace(' ', '').replace('₽', '').replace('/м²', ''))

driver = None


try:
    driver = uc.Chrome(version_main=145) # маска для блокировки

    for offset in range(0, 1801, 20):
        data = []
        driver.get(f'https://xabarovsk.domclick.ru/search?deal_type=sale&category=living&offer_type=flat&aids=78259&offset={offset}')
        wait = WebDriverWait(driver, 4)

        try:
            # нажимаем на кнопку с cookie файлами
            cookie_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-root-119-19-5-3.btn-primary-a30-19-5-3.btn-medium-fdc-19-5-3.btn-typeButtonReset-268-19-5-3.btn-fluid-af4-19-5-3.btn-withContainer-203-19-5-3"))
            )
            cookie_button.click()
        except Exception as e:
            print("Ошибка с cookies:", e)

        # Ссылки внутри карточек
        cards = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".sNO6x.sYIdf.sP3YK"))
        )
        all_links = [c.get_attribute("href") for c in cards]
        links = [l for l in all_links if l and l.startswith("http")]

        # для каждой ссылки
        for link in links:
            try:
                driver.get(link)
                time.sleep(random.uniform(0.5, 1.2))
                info = {}

                # парсинг
                total_price = int(driver.find_elements(By.CSS_SELECTOR, ".JfVCK")[1].text.replace(' ', '').replace('₽', ''))
                price_by_squares = int(driver.find_elements(By.CSS_SELECTOR, ".xp7iu")[1].text.replace(' ', '').replace('₽/м²', ''))
                address = driver.find_element(By.CLASS_NAME, "ByOQP").text
                quarter = driver.find_element(By.CLASS_NAME, "link-link-777-13-1-0").text

                list_blocks = driver.find_elements(By.CLASS_NAME, "C_L_4")
                # добавляем все найденные элементы в словарь
                for block in list_blocks:
                    key = block.find_element(By.CLASS_NAME, "fiwfl").text
                    value = block.find_element(By.CLASS_NAME, "yNtG9").text
                    info[key] = value

                info_building = driver.find_elements(By.CLASS_NAME, "ByFq7")
                # добавляем все найденные элементы в словарь
                for feature in info_building:
                    key = feature.find_element(By.CLASS_NAME, "sQK5j").text
                    value = feature.find_element(By.CLASS_NAME, "upbHP").text
                    info[key] = value

                count_rooms = info.get('Комнат')
                area = info.get('Площадь')
                area_living = info.get('Жилая')
                kitchen = info.get('Кухня')
                floor = info.get('Этаж')
                type_deal = info.get('Тип сделки')
                type_housing = info.get('Тип жилья')
                repair = info.get('Ремонт')
                year_construction = info.get('Год постройки')
                floors = info.get('Количество этажей')

                # словарь значений
                row = {
                    'Цена': total_price,
                    'Цена за квадратный метр': price_by_squares,
                    'Адрес': address,
                    'Район': quarter,
                    'Комнаты': convert_to_int(count_rooms),
                    'Площадь': convert_to_float(area),
                    'Жилая площадь': convert_to_float(area),
                    'Кухня': convert_to_float(kitchen),
                    'Этаж': convert_to_int(floor),
                    'Тип сделки': type_deal,
                    'Тип жилья': type_housing,
                    'Ремонт': repair,
                    'Год постройки': year_construction,
                    'Количество этажей': floors,
                    'Ссылка на объявление': link
                }
                data.append(row)

            except Exception as e:
                print("Ошибка при обработке объявления:", e)
                continue # пропускаем часть кода

        print(f'Изучена страница номер {offset//20}')

        df = pd.DataFrame(data) # датафрейм из данных

        if offset == 0:
            df.to_csv('output.csv', mode='a', index=False, encoding='utf-8') # содержит названия колонок
        else:
            df.to_csv('output.csv', mode='a', header=False, index=False, encoding='utf-8') # не содержит названия колонок

finally:
    if driver:
        try:
            driver.quit()
        except Exception:
            pass
        driver = None



