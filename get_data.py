from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
from selenium import webdriver
import time
import os

def configure_firefox():
    stock_download_dir = os.path.join(os.getcwd(), "get_data")
    os.makedirs(stock_download_dir, exist_ok=True)

    geckodriver_path = "driver/geckodriver.exe"
    options = Options()
    options.add_argument("--incognito")
    options.add_argument("--headless")
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/vnd.ms-excel,text/csv")
    options.set_preference("browser.download.dir", stock_download_dir)

    service = Service(executable_path=geckodriver_path)
    driver = webdriver.Firefox(service=service, options=options)

    url = 'https://www.idx.co.id/id/data-pasar/ringkasan-perdagangan/ringkasan-saham'
    driver.get(url)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    driver.execute_script("document.body.style.transform = 'scale(0.5)';")
    driver.execute_script("document.body.style.transformOrigin = '0 0';")

    return driver

def select_date(driver, year, month, day):
    input_date = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="app"]/div[2]/main/div/div[1]/div[1]/div[2]/div[1]/div/input')
        )
    )
    input_date.click()

    year_button = driver.find_element(By.XPATH, '//button[contains(@class, "mx-btn-text mx-btn-current-year")]')
    year_button.click()

    year_dropdown = driver.find_element(By.XPATH, '//table[@class="mx-table mx-table-year"]')
    year_option = year_dropdown.find_element(By.XPATH, f'//td[@data-year="{year}"]')
    year_option.click()

    month_table = driver.find_element(By.XPATH, '//table[@class="mx-table mx-table-month"]')
    month_option = month_table.find_element(By.XPATH, f'//td[@data-month="{month-1}"]')
    month_option.click()

    date_str = f"{year}-{month:02d}-{day:02d}"
    date_xpath = f'//td[@title="{date_str}" and not(@class="disabled")]'
    selected_date = driver.find_element(By.XPATH, date_xpath)
    selected_date.click()

def download_data_for_dates(driver, start_date, end_date):
    current_date = start_date
    while current_date <= end_date:
        year, month, day = current_date.year, current_date.month, current_date.day
        try:
            select_date(driver, year, month, day)
            time.sleep(5)
            download_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="app"]/div[2]/main/div/div[1]/div[1]/div[2]/div[2]/button')
                )
            )

            download_button.click()
            print(f"Data for {year}-{month:02d}-{day:02d} downloaded")
            time.sleep(4)
        except Exception as e:
            print(f"No data available for {year}-{month:02d}-{day:02d}. Skipping...")

        current_date += timedelta(days=1)

# Buka browser dan konfigurasi Firefox
driver = configure_firefox()

# Input tanggal mulai dan akhir
start_date_input = input("Enter the start date (day/month/year): ")
start_day, start_month, start_year = map(int, start_date_input.split('/'))

end_date_input = input("Enter the end date (day/month/year): ")
end_day, end_month, end_year = map(int, end_date_input.split('/'))

start_date = datetime(start_year, start_month, start_day)
end_date = datetime(end_year, end_month, end_day)

# Unduh data untuk rentang tanggal yang diberikan
download_data_for_dates(driver, start_date, end_date)

# Tutup browser
driver.quit()
