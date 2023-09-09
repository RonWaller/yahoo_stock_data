"""Get quarterly data from Yahoo Finance"""
import json
import time
from datetime import datetime
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright
from rich import print
from selectolax.parser import HTMLParser

# * single stock
# STOCKS = ["AAPL"]
# * make list of stocks
STOCKS = ["AAPL", "AMC", "AMZN", "F", "GOOGL", "MSFT"]


def main():
    """main starting point of program"""

    with sync_playwright() as play_wright:
        browser = play_wright.chromium.launch()
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5)"
                " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0"
                " Safari/537.36"
            )
        )
        page = context.new_page()
        page.set_default_timeout(120000)

        for stock in STOCKS:
            print(stock)
            process_stocks(page, stock)

        # * close browswer
        page.close()


def process_stocks(page, stock):
    """Get all of the quarterly data from Yahoo Finance"""

    path = Path(f"stock_data/{stock}", "quarterly.json")
    now = datetime.now()
    month = now.month

    quarter_list = []

    # * if "quarterly.json" doesn't exist create folder and run quarterly_info
    # * if "quarterly.json" exsists check dates to add data or not
    if not path.is_file():
        path.parent.mkdir(exist_ok=True, parents=True)
        quarter_list.append(quarterly_info(page, stock))
        quarterly_data = quarter_list
        # *  save data to json file
        json_data(path, quarterly_data, isdate_quarterly=False)

    else:
        if check_quarterly_date(path, month):
            quarterly_data = quarterly_info(page, stock)
            # *  save data to json file
            json_data(path, quarterly_data, isdate_quarterly=True)

        else:
            print("No new Quarterly data")
            return


def check_quarterly_date(path, month):
    """summary"""
    # //TODO: only run quarterly end of month
    # * if date is 1, 4, 7, 10 run quarterly_info()
    # * else if quarterly date in .json file skip
    quarter_month_list = [1, 4, 7, 10]
    dates = []

    # * if date in quarterly_date_list run code below
    if month in quarter_month_list:
        quarter_date = quarterly_date()
        # * if .json check file quarterly date and compare to currently quarter
        with path.open(mode="r", encoding="utf-8") as file:
            # * place json data in results list
            results = json.load(file)
            quarterly = results[0]["quarterly"]
            for item in quarterly:
                for key in item:
                    dates.append(key)
            if quarter_date not in dates:
                print("Quarterly data being extracted...")
                return True

            else:
                print("Quarterly data is already in .json file")
                return False


def quarterly_info(page, stock):
    """summary"""
    stock_data = []
    stats_dict = stats(page, stock)
    financial_dict = financials(page, stock)
    quarterly_dict = stats_dict | financial_dict
    stock_data.append(quarterly_dict)
    quarterly_data = {quarterly_date(): stock_data}
    # quarter_list.append(quarterly_data)

    return quarterly_data


def stats(page, stock):
    """Get stock statistics data on yahoo finance"""
    print("Scraping Statistics Data....")
    try:
        stats_dict = {}
        url_stats = "https://finance.yahoo.com/quote/{}/key-statistics?p={}"
        page.goto(url_stats.format(stock, stock), timeout=0)
        # * Get quarterly data
        # * Call quarterly date funciton
        html = page.inner_html("div#Main")
        data = HTMLParser(html)
        stats_info = data.css_first("table")
        stats_table = stats_info.css("tbody tr")
        for row in stats_table:
            key = row.css_first("td").text().strip()
            value = row.css("td")[2].text()
            stats_dict.update({key: value})

    except PlaywrightTimeoutError:
        print("Timeout")

    return {"stats": stats_dict}
    # print(stats_dict)


def financials(page, stock):
    """Get stock financal data on yahoo finance"""
    print("Scraping Financials Data....")

    financial_dict = {}

    income_data = income(page, stock)
    balance_data = balance(page, stock)
    cash_data = cash(page, stock)
    # print(income_data)
    # print(balance_data)
    # print(cash_data)
    # //TODO add quarterly date to dictionary
    financial_dict.update({"income": income_data})
    financial_dict.update({"balance": balance_data})
    financial_dict.update({"cash": cash_data})

    return financial_dict


def income(page, stock) -> dict:
    """Get stock income statement data on yahoo finance"""
    print("Scraping Income Data....")
    try:
        income_dict = {}
        url_financials = "https://finance.yahoo.com/quote/{}/financials?p={}"
        page.goto(url_financials.format(stock, stock), timeout=0)
        page.get_by_text("Quarterly").click()
        time.sleep(2)
        html = page.inner_html("div#Main")
        data = HTMLParser(html)
        income_info = data.css("div[data-test='fin-row']")
        for item in income_info:
            key = item.css_first("span").text()
            value = item.css("div[data-test='fin-col']")[1].text()
            income_dict.update({key: value})

    except PlaywrightTimeoutError:
        print("Timeout")

    return income_dict


def balance(page, stock) -> dict:
    """Get stock balance sheet data on yahoo finance"""
    print("Scraping Balance Data....")
    try:
        balance_dict = {}
        url_financials = (
            "https://finance.yahoo.com/quote/{}/balance-sheet?p={}"
        )
        page.goto(url_financials.format(stock, stock), timeout=0)
        page.get_by_text("Quarterly").click()
        time.sleep(2)
        # * click quarterly button
        html = page.inner_html("div#Main")
        data = HTMLParser(html)
        balance_info = data.css("div[data-test='fin-row']")
        for item in balance_info:
            key = item.css_first("span").text()
            value = item.css_first("div[data-test='fin-col']").text()
            balance_dict.update({key: value})

    except PlaywrightTimeoutError:
        print("Timeout")

    return balance_dict


def cash(page, stock) -> dict:
    """Get stock cash flow data on yahoo finance"""
    print("Scraping Cash Flow Data....")
    try:
        cash_dict = {}
        url_financials = "https://finance.yahoo.com/quote/{}/cash-flow?p={}"
        page.goto(url_financials.format(stock, stock), timeout=0)
        # * Click quarterly button
        page.get_by_text("Quarterly").click()
        time.sleep(2)
        html = page.inner_html("div#Main")
        data = HTMLParser(html)
        cash_info = data.css("div[data-test='fin-row']")
        for item in cash_info:
            key = item.css_first("span").text()
            value = item.css("div[data-test='fin-col']")[1].text()
            cash_dict.update({key: value})

    except PlaywrightTimeoutError:
        print("Timeout")

    return cash_dict


def quarterly_date():
    now = datetime.now()
    month = now.month
    year = now.year
    # day = now.day

    quarter_index = {1: "12-31", 2: "3-31", 3: "6-30", 4: "9-30"}
    # quarter_day = {3: 31, 6: 30, 9: 30, 12: 31}
    quarterly_list = [(1, 2, 3), (4, 5, 6), (7, 8, 9), (10, 11, 12)]

    for idx, item in enumerate(quarterly_list):
        for number in item:
            if month == number:
                index_number = idx + 1

    if index_number == 1:
        quarter_daymonth = quarter_index[index_number]
        quarter_date = f"{year - 1}-{quarter_daymonth}"
    else:
        quarter_daymonth = quarter_index[index_number]
        quarter_date = f"{year}-{quarter_daymonth}"

    return quarter_date


def json_data(path, quarterly_data, isdate_quarterly):
    """Parse the stock data, save to json file"""
    print("Creating JSON data files....")

    results = []

    # * if date true get previous data
    if isdate_quarterly:
        with path.open(mode="r", encoding="utf-8") as file:
            # * place json data in results list
            results = json.load(file)

        quarterly = results[0]["quarterly"]
        quarterly.insert(0, quarterly_data)

        results.append(quarterly)
        # * write data to json file
        with path.open(mode="w", encoding="utf-8") as file:
            file.write(json.dumps(results))

    else:
        # * write data to json file
        results.append({"quarterly": quarterly_data})
        with path.open(mode="w", encoding="utf-8") as file:
            file.write(json.dumps(results))


if __name__ == "__main__":
    main()
