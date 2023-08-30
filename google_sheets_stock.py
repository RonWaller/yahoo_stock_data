"""Update to Google Sheets from JSON files"""
import json
import time
from datetime import date

import gspread
import xlsxwriter
from gspread.exceptions import WorksheetNotFound
from rich import print

# //TODO:
# * Check for stock sheet. If true,
# * Update summary data by date column
# * If false create new sheet with stock symbol.
# * Create "Profile" only list to only run first time sheet created
# * Create Summary "Keys" list to run with "Profile" setup
# * Add profile data and summary Keys & Values
# * Create "Summary" only list to run everytime


def main():
    """summary"""
    # * List of stocks
    stocks = ["AAPL", "AMC", "AMZN", "F", "GOOGL", "MSFT"]
    today = str(date.today())

    for stock in stocks:
        google_sheets(today, stock)
        time.sleep(15)


def google_sheets(today, stock):
    """summary"""
    print(stock)
    sheet = open_workbook()
    results = open_json_file(stock)

    # * Get data items from results dictionary
    # * create profile & summary dictionaries
    # * check if sheet named "stock" is present
    # * if present add new date column and only summary data values
    try:
        update_summary_data(stock, sheet, results, today)
        print("Sending data to Google Sheets....")
    # * Exception if worksheet isn't found and creates new sheet
    except WorksheetNotFound:
        setup_new_sheet(stock, sheet, results, today)


def open_workbook():
    """open google sheets workbook"""
    google_creds = gspread.service_account(filename="client_secret.json")
    sheet = google_creds.open("Stock Data")
    return sheet


def open_json_file(stock):
    """open json files to get data"""
    # * read stock json file to get dictionary data
    path = f"./json_data/{stock}.json"
    with open(f"{path}", "r", encoding="utf-8") as file:
        results = json.load(file)
        file.close()
    return results


def update_summary_data(stock, sheet, results, today):
    """summary"""
    data_list = []
    summary_items = results[1][today][0]["summary"]
    worksheet = sheet.worksheet(f"{stock}")
    print("This sheet is found.....")
    for item in results:
        for key in item:
            data_list.append(key)

    # * set row of spreadshet
    row = 7
    # * get the row vaules do determine next empty column
    row_values = worksheet.row_values(row)

    # * check if date already in sheet
    for dates in data_list:
        if dates in row_values:
            return

    # * get first empty column in row
    col = len(row_values)
    # * sets the column letter
    col_letter = xlsxwriter.utility.xl_col_to_name(col)
    print(col_letter)

    # * set today's date for when data was grabbed
    worksheet.update_acell(f"{col_letter}{row}", today)
    row += 1

    # * update column with summary values
    # * loop through summary_items get values
    try:
        for key, val in summary_items.items():
            skip_list = [
                "stock_symbol",
                "market_price",
                "market_change",
                "market_percent",
            ]
            if key not in skip_list:
                # worksheet.update_acell(f"{col_letter}{row}", key)
                worksheet.update_acell(f"{col_letter}{row}", val)
                row += 1
            else:
                continue
    except Exception:
        print("problem occured....")

    print("Sheet updated...")


def setup_new_sheet(stock, sheet, results, today):
    """summary"""
    # * if sheet not present create and add profile information and all summary data
    print("Nope not here....")
    # * create new sheet with stock symbol
    worksheet = sheet.add_worksheet(title=f"{stock}", rows=1000, cols=26)
    print("New sheet created.....")
    # * set profile information
    # * Get company info from company_items, sector_items, summary_items dictionaries
    # * Build profile section of sheet (A1 - E5)
    print("Creating Profile Section.....")
    set_summary_items(worksheet, results, today)
    set_company_items(worksheet, results, today)
    set_sector_items(worksheet, results, today)
    worksheet.update_acell("A1", stock)
    worksheet.update_acell("A7", "Summary")
    worksheet.update_acell("D7", today)

    print("Sheet Updated...")


def set_summary_items(worksheet, results, today):
    """summary"""
    print("Creating Summary Section....")
    summary_items = results[today][1]["summary"]
    worksheet.update_acell("B1", summary_items["market_price"])
    worksheet.update_acell("C1", summary_items["market_change"])
    worksheet.update_acell("D1", summary_items["market_percent"])
    row = 8
    for key, val in summary_items.items():
        skip_list = [
            "stock_symbol",
            "market_price",
            "market_change",
            "market_percent",
        ]
        if key not in skip_list:
            worksheet.update_acell(f"A{row}", key)
            worksheet.update_acell(f"D{row}", val)
            row += 1

        else:
            continue


def set_company_items(worksheet, results, today):
    """summary"""
    print("Creating Company Section....")
    company_items = results[today][0]["profile"]["company"]
    worksheet.update_acell("A2", company_items["name"])
    worksheet.update_acell("A3", company_items["address"])
    worksheet.update_acell("A4", company_items["citystatezip"])
    worksheet.update_acell("A5", company_items["site"])


def set_sector_items(worksheet, results, today):
    """summary"""
    print("Creating Sector Section....")
    sector_items = results[today][0]["profile"]["sector"]
    row = 3
    for key, val in sector_items.items():
        worksheet.update_acell(f"D{row}", key)
        worksheet.update_acell(f"E{row}", val)
        row += 1


if __name__ == "__main__":
    main()
