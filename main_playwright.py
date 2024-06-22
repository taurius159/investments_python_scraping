import pandas as pd
from bs4 import BeautifulSoup
import datetime
import time
import os.path
import asyncio
from playwright.async_api import async_playwright

async def save_entry(result_names, result_prices):
    current_time = time.strftime('%H:%M')
    result_time = []
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

async def scrap_binance(url):
    print(f"Scrapping url: {url}...")
    result_names = []
    result_prices = []
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=False)
        page = await browser.new_page()
        await page.goto(url, timeout=50000)
        
        # change currency from usd to euro 
        await page.locator(".css-1es5582").first.click() #search by class
        await page.get_by_role("option", name="EUR - €").click()

        # Add the page source to the variable `content`
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')

        price = soup.find(attrs={'class': 'css-1bwgsh3'})
        result_prices.append(price.text)
        if "io" in url:
            result_names.append('io.net')
        else:
            result_names.append('bitcoin')

        await save_entry(result_names, result_prices)

        await browser.close()

async def main():
    while True:
        start_time = time.time()
        
        print("Main scrapping loop started...")
        tasks = []
        #scrap_swedbank(driver, result_names, result_prices)
        task = asyncio.create_task(scrap_binance("https://www.binance.com/en/price/io-net"))
        tasks.append(task)
        task = asyncio.create_task(scrap_binance("https://www.binance.com/en/price/bitcoin"))
        tasks.append(task)

        await asyncio.gather(*tasks)

        time_difference = time.time() - start_time
        print(f'Scraping time: %.2f seconds.' % time_difference)
        time.sleep(600) #every 10min

    # driver.quit() never runs as its outside infinite loop

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
