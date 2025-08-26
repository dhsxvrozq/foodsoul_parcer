import logging
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
import json
from typing import List
import yaml

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("scraper.log", encoding="utf-8"),  # Лог в файл
        logging.StreamHandler()  # Лог в консоль
    ]
)

def wait_for_page_load(driver, timeout=30):
    """Ждем полной загрузки страницы"""
    WebDriverWait(driver, timeout).until(
        lambda driver: driver.execute_script("return document.readyState") == "complete"
    )

def initialize_driver():
    """Инициализация драйвера Firefox."""
    firefox_options = Options()
    firefox_options.add_argument("--headless") 
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=firefox_options)
    logging.info("Драйвер инициализирован")
    return driver

def click_element(driver, xpath, element_name):
    """Клик по элементу с заданным XPath."""
    try:
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        element.click()
        logging.info(f"Кликнули на элемент: {element_name}")
    except Exception as e:
        logging.error(f"Ошибка при клике на {element_name}: {e}")

def get_list(driver, xpath_template: str, attr=None) -> List:
    """Получение элементов с заданным атрибутом или текстом."""
    try:
        wait = WebDriverWait(driver, 10)
        items = wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath_template)))
        
        if attr == "text" or attr is None:
            values = [item.text for item in items]
        else:
            values = [item.get_attribute(attr) for item in items]
        
        logging.debug(f"Найдено {len(values)} элементов по xpath: {xpath_template}")
        return values

    except Exception as e:
        logging.warning(f"Элементы не найдены: {e}")
        return []

def main():
    with open("config.yml", "r", encoding="utf-8") as f:
        CONFIG = yaml.safe_load(f)
    
    all_data = []  # Список для всех данных вместо словаря
    
    # Запускаем действия
    driver = initialize_driver()
    driver.get(CONFIG["url"])  # Открываем сайт
    wait_for_page_load(driver)
    logging.info(f"Открыта страница: {CONFIG['url']}")
    
    click_element(driver, CONFIG["pick_up_xpath"], "pickup")
    wait_for_page_load(driver)
    
    # если на дворе ночь и появляется сообщение о том, что в это время не работают
    ok_button = driver.find_elements(By.XPATH, CONFIG["ok_xpath"])
    if ok_button:
        click_element(driver, CONFIG["ok_xpath"], "ok_button")
        wait_for_page_load(driver)
    
    categories = get_list(driver, CONFIG["categories"], "href")
    logging.info(f"Найдено {len(categories)} категорий")
    
    for category in categories:
        driver.get(category)
        wait_for_page_load(driver)
        logging.info(f"Открыта категория: {category}")
        
        # если на дворе ночь и появляется сообщение о том, что в это время не работают
        if ok_button:
            click_element(driver, CONFIG["ok_xpath"], "ok_button")
            wait_for_page_load(driver)
        
        titles = get_list(driver, CONFIG["titles"], "text")
        prices = get_list(driver, CONFIG["prices"], "text")
        prices = [int(''.join(filter(str.isdigit, price))) for price in prices]
        
        # Добавляем в общий список как объекты
        for title, price in zip(titles, prices):
            item = {
                "name": title,
                "price": price
            }
            all_data.append(item)
        
        logging.info(f"Добавлено {len(titles)} товаров из {category.split('/')[-1]}")
    
    # Сохраняем все данные в один файл
    with open('menu.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    logging.info(f"Всего товаров: {len(all_data)}")
    logging.info("Все данные сохранены в menu.json")
    driver.quit()
    logging.info("Браузер закрыт")

if __name__ == "__main__":
    main()