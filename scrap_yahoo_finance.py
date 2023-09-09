"""Playwright scrape Yahoo Finance. Selectorlax to parse HTML.
Create JSON files"""
import json
from datetime import date
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright
from rich import print
from selectolax.parser import HTMLParser

# //TODO:

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
    """Get all of the stock data from Yahoo Finance"""
    # * if "stock.json" exsists skip profile function but run others
    # * change path to new stock_data and stock folder
    path = Path(f"stock_data/{stock}", f"{stock}.json")
    stock_results = []

    # * if no .json file run profile & quarterly_info
    if not path.is_file():
        path.parent.mkdir(exist_ok=True, parents=True)
        stock_results.append(profile(page, stock))  # data from profile tab

    summary_data = summary(page, stock)  # data from summary tab

    # *  save data to json file
    json_data(path, stock_results, summary_data)


def profile(page, stock):
    """Get stock profile data on yahoo finance"""
    print("Scraping Profile Data....")
    try:
        url_profile = "https://finance.yahoo.com/quote/{}/profile?p={}"
        page.goto(url_profile.format(stock, stock), timeout=0)
        html = page.inner_html("div[data-test='qsp-profile']")
        data = HTMLParser(html)
        info = company_details(data)
        sector = company_sector_data(data)
        company = info | sector

    except PlaywrightTimeoutError:
        print("Timeout")

    return {"company": company}


def company_details(data) -> dict:
    """Parse html to gather company info"""
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


def company_sector_data(data) -> dict:
    """Parse html to gather company sector data"""
    company_profile_data = data.css("p:nth-child(2)")
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
    """Get stock summary data on yahoo finance"""
    print("Scraping Summary Data....")
    try:
        stock_dict = {}

        url_summary = "https://finance.yahoo.com/quote/{}?p={}"
        page.goto(url_summary.format(stock, stock), timeout=0)
        html = page.inner_html("div#quote-header-info")
        data = HTMLParser(html)
        # stock_name = data.css_first("h1").text()
        # stock_symbol = re.search(r"\(([^)]+)", stock_name).group(1)
        market_price = data.css_first(
            "fin-streamer[data-test='qsp-price']"
        ).text()
        market_price_change = data.css_first(
            "fin-streamer[data-test='qsp-price-change']"
        ).text()
        market_price_regchange = data.css_first(
            "fin-streamer[data-field='regularMarketChangePercent']"
        ).attrs["value"]
        stock_dict.update({"stock_symbol": stock})
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

    return {"summary": stock_dict}


def json_data(path, stock_results, summary_data):
    """Parse the stock data, save to json file"""
    print("Creating JSON data files....")

    results = []
    today = str(date.today())
    # * insert new quarterly data
    # * results[1]["quarterly"][0]
    # * insert {date & data} to quarterly list
    # * insert quarterly list into results list
    # results.insert(1, quarterly_data)

    # * check for json file and get previous data

    if path.is_file():
        with path.open(mode="r", encoding="utf-8") as file:
            # * place json data in results list
            results = json.load(file)

        date_list = []

        # * get date keys from saved data
        for item in results:
            for key in item:
                date_list.append(key)

        # * check if todays date in saved data. true skip false add new data
        if today not in date_list:
            # * insert data into list at index#
            results.insert(2, {today: summary_data})
            # * write data to json file
            with path.open(mode="w", encoding="utf-8") as file:
                file.write(json.dumps(results))

        else:
            print("No New Data....")

    else:
        # * append new stock data to list
        stock_results.append({today: summary_data})
        # * write data to json file
        with path.open(mode="w", encoding="utf-8") as file:
            file.write(json.dumps(stock_results))


if __name__ == "__main__":
    main()
