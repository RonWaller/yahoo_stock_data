"""Playwright scrape Yahoo Finance. Selectorlax to parse HTML. Create JSON files"""
import json
import re
from datetime import date
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright
from rich import print
from selectolax.parser import HTMLParser

# //TODO:

stock_results = []
stock_data = []


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
        # * single stock
        # stocks = ["AAPL"]
        # * make list of stocks
        stocks = ["AAPL", "AMC", "AMZN", "F", "GOOGL", "MSFT"]
        today = str(date.today())
        for stock in stocks:
            print(stock)
            stock_results.clear()
            stock_data.clear()
            # * if "stock.json" exsists skip profile function but run others
            path = Path("json_data", f"{stock}.json")

            if not path.is_file():
                profile(page, stock)  # data from profile tab

            summary(page, stock)  # data from summary tab
            stats(page, stock)  # data from statistics tab
            financials(page, stock)  # data financials tab
            json_data(today, path)  # save data to json file
        # * close browswer
        page.close()


def profile(page, stock):
    """summary"""
    print("Scraping Profile Data....")
    try:
        profile_dict = {}
        url_profile = "https://finance.yahoo.com/quote/{}/profile?p={}"
        page.goto(url_profile.format(stock, stock), timeout=0)
        html = page.inner_html("div[data-test='qsp-profile']")
        data = HTMLParser(html)
        info = company_details(data)
        profile_dict.update({"company": info})
        company_profile_data = data.css("p:nth-child(2)")
        sector = company_sector_data(company_profile_data)
        profile_dict.update({"sector": sector})

    except PlaywrightTimeoutError:
        print("Timeout")

    stock_results.append({"profile": profile_dict})


def company_details(data) -> dict:
    """summary"""
    company_name = data.css_first("h3").text()
    company_info = data.css_first("p").text(separator="*")
    company_list = company_info.split("*")
    if len(company_list) > 5:
        company_list.pop(0)

    company_address = company_list[0]
    company_citystatezip = company_list[1]
    company_country = company_list[2]
    company_phone = company_list[3]
    company_site = company_list[4]

    company = {
        "name": company_name,
        "address": company_address,
        "citystatezip": company_citystatezip,
        "country": company_country,
        "phone": company_phone,
        "site": company_site,
    }

    return company


def company_sector_data(company_profile_data) -> dict:
    """summary"""
    for item in company_profile_data:
        sector_key = item.css("span")[0].text()
        sector_value = item.css("span")[1].text()
        industry_key = item.css("span")[2].text()
        industry_value = item.css("span")[3].text()
        employees_key = item.css("span")[4].text()
        employees_value = item.css("span")[5].text()

        sector = {
            sector_key: sector_value,
            industry_key: industry_value,
            employees_key: employees_value,
        }

        return sector


def summary(page, stock):
    """summary"""
    print("Scraping Summary Data....")
    try:
        stock_dict = {}

        url_summary = "https://finance.yahoo.com/quote/{}?p={}"
        page.goto(url_summary.format(stock, stock), timeout=0)
        html = page.inner_html("div#quote-header-info")
        data = HTMLParser(html)
        stock_name = data.css_first("h1").text()
        stock_symbol = re.search(r"\(([^)]+)", stock_name).group(1)
        market_price = data.css_first(
            "fin-streamer[data-test='qsp-price']"
        ).text()
        market_price_change = data.css_first(
            "fin-streamer[data-test='qsp-price-change']"
        ).text()
        market_price_regchange = data.css_first(
            "fin-streamer[data-field='regularMarketChangePercent']"
        ).attrs["value"]
        stock_dict.update({"stock_symbol": stock_symbol})
        stock_dict.update({"market_price": market_price})
        stock_dict.update({"market_change": market_price_change})
        stock_dict.update({"market_percent": market_price_regchange})

        html = page.inner_html("div#quote-summary")
        data = HTMLParser(html)
        table = data.css("table tr")
        for row in table:
            key = row.css("td")[0].text()
            value = row.css("td")[1].text()
            stock_dict.update({key: value})

    except PlaywrightTimeoutError:
        print("Timeout")

    stock_data.append({"summary": stock_dict})


def stats(page, stock):
    """summary"""
    print("Scraping Statistics Data....")
    try:
        stats_dict = {}
        url_stats = "https://finance.yahoo.com/quote/{}/key-statistics?p={}"
        page.goto(url_stats.format(stock, stock), timeout=0)
        html = page.inner_html("div#Main")
        data = HTMLParser(html)
        stats_info = data.css_first("table")
        stats_table = stats_info.css("tbody tr")
        for row in stats_table:
            key = row.css_first("td").text().strip()
            value = row.css("td")[1].text()
            stats_dict.update({key: value})

    except PlaywrightTimeoutError:
        print("Timeout")

    stock_data.append({"stats": stats_dict})


def financials(page, stock):
    """summary"""
    print("Scraping Financials Data....")

    financial_dict = {}
    income_data = income(page, stock)
    balance_data = balance(page, stock)
    cash_data = cash(page, stock)

    financial_dict.update({"income": income_data})
    financial_dict.update({"balance": balance_data})
    financial_dict.update({"cash": cash_data})

    stock_data.append({"financials": financial_dict})


def income(page, stock) -> dict:
    """summary"""
    print("Scraping Income Data....")
    try:
        income_dict = {}
        url_financials = "https://finance.yahoo.com/quote/{}/financials?p={}"
        page.goto(url_financials.format(stock, stock), timeout=0)
        html = page.inner_html("div#Main")
        data = HTMLParser(html)
        income_info = data.css("div[data-test='fin-row']")
        for item in income_info:
            key = item.css_first("span").text()
            value = item.css_first("div[data-test='fin-col']").text()
            income_dict.update({key: value})

    except PlaywrightTimeoutError:
        print("Timeout")

    return income_dict


def balance(page, stock) -> dict:
    """summary"""
    print("Scraping Balance Data....")
    try:
        balance_dict = {}
        url_financials = (
            "https://finance.yahoo.com/quote/{}/balance-sheet?p={}"
        )
        page.goto(url_financials.format(stock, stock), timeout=0)
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
    """summary"""
    print("Scraping Cash Flow Data....")
    try:
        cash_dict = {}
        url_financials = "https://finance.yahoo.com/quote/{}/cash-flow?p={}"
        page.goto(url_financials.format(stock, stock), timeout=0)
        html = page.inner_html("div#Main")
        data = HTMLParser(html)
        cash_info = data.css("div[data-test='fin-row']")
        for item in cash_info:
            key = item.css_first("span").text()
            value = item.css_first("div[data-test='fin-col']").text()
            cash_dict.update({key: value})

    except PlaywrightTimeoutError:
        print("Timeout")

    return cash_dict


def json_data(today, path):
    """summary"""
    print("Creating JSON data files....")
    # path = f"./json_data/{stock}.json"
    # file_in_folder = os.path.isfile(path)
    results = []

    # * check for json file and get previous data

    if path.is_file():
        with path.open(mode="r", encoding="utf-8") as file:
            # * place json data in results list
            results = json.load(file)
            file.close()

        date_list = []

        # * get date keys from saved data
        for item in results:
            for key in item:
                date_list.append(key)

        # * check if todays date in saved data. true skip false add new data
        if today not in date_list:
            # * insert data into list at index#
            results.insert(1, {today: stock_data})
            # * write data to json file
            with path.open(mode="w", encoding="utf-8") as file:
                file.write(json.dumps(results))
                file.close()
        else:
            print("No New Data....")

    else:
        # * append new stock data to list
        stock_results.append({today: stock_data})
        # * write data to json file
        with path.open(mode="w", encoding="utf-8") as file:
            file.write(json.dumps(stock_results))
            file.close()


if __name__ == "__main__":
    main()
