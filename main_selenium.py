import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
import datetime
from selenium.webdriver.common.by import By
import time
import os.path

def scrap_swedbank(driver, result_names, result_prices):
    driver.get('https://www.swedbank.lt/private/investor/funds/allFunds')
    
    content = driver.page_source
    soup = BeautifulSoup(content, 'html.parser')

    for element in soup.find_all(id=lambda x: x and x.startswith('tableRow')):
        name = element.find('a')
        price = element.findAll('td')[4:5]
        if "Swedbank Savings Fund 100" in name.text:
            result_prices.append(price[0].get_text())
            result_names.append(name.text)

    return result_names, result_prices

def scrap_binance(url, driver, result_names, result_prices):
    # cryptocurrency prices scraping. io.net
    driver.get(url)

    # change currency to euro from usd
    driver.find_element(By.CLASS_NAME, "css-1cda2ax").click()
    driver.find_element(By.ID, "EUR_USD").click()

    # Add the page source to the variable `content`.
    content = driver.page_source
    # Load the contents of the page, its source, into BeautifulSoup 
    # class, which analyzes the HTML as a nested data structure and allows to select
    # its elements by using various selectors.
    soup = BeautifulSoup(content, 'html.parser')

    price = soup.find(attrs={'class': 'css-1bwgsh3'})
    result_prices.append(price.text)
    if "io" in url:
        result_names.append('io.net')
    else:
        result_names.append('bitcoin')

    return result_names, result_prices

def main():
    start_time = time.time()

    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)

    while True:
        result_names = []
        result_prices = []
        scrap_swedbank(driver, result_names, result_prices)
        scrap_binance("https://www.binance.com/en/price/io-net", driver, result_names, result_prices)
        scrap_binance("https://www.binance.com/en/price/bitcoin", driver, result_names, result_prices)

        #print output of scraping
        current_time = time.strftime('%H:%M')
        result_time = []
        for i in range(0, len(result_names)):
            print(f"{result_names[i]}: {result_prices[i]}")
            result_time.append(current_time)

        filename = f"{datetime.date.today()}"
        series0 = pd.Series(result_time, name="Time")
        series1 = pd.Series(result_names, name='Names')
        series2 = pd.Series(result_prices, name='Prices')
        df = pd.DataFrame({'Times': series0,'Names': series1, 'Prices': series2})
            
        if os.path.isfile(filename):
            df.to_csv(filename, mode='a', index=False, header=False)
        else:
            df.to_csv(filename, index=False, encoding='utf-8')

        time_difference = time.time() - start_time
        print(f'Scraping time: %.2f seconds.' % time_difference)
        time.sleep(600) #every 10min

    driver.quit()
main()

