Thanks for your help before. I got it working the way I hoped. I used somee global variables. Please anyone look this over give feedback. I really want to get better at this. Hope ok to post this code its only `main()`.

```py
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
            path = f"./json_data/{stock}.json"
            file_in_folder = os.path.isfile(path)
            if not file_in_folder:
                profile(page, stock)  # data from profile tab

            summary(page, stock)  # data from summary tab
            stats(page, stock)  # data from statistics tab
            financials(page, stock)  # data financials tab
            json_data(today, stock)
        # * close browswer
        context.close()
```

```json
[
  {
    "profile": {}
  },
  {
    "2023-08-29": []
  },
  {
    "2023-08-28": []
  },
  {
    "2023-08-27": []
  },
  {
    "2023-08-26": []
  }
]
```
