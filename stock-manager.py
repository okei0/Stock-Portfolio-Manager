import requests
import datetime
import sys
import csv
from tabulate import tabulate

api_key = "141c9a48e97a478eb2c1b8685bc38f03"


def display_menu_options(stock_list, totals, current_index):
    print("1. Buy stock")
    print("2. Sell Stock")
    print("3. Refresh portfolio")
    print("4. Save and quit\n")
    while True:
        try:
            user_input = int(input("Choose option (1-4): "))
            if 1 <= user_input <= 4:
                break
            else:
                print("Please enter a number between 1 and 4")
        except ValueError:
            print("Please enter a number between 1 and 4")

    match user_input:
        case 1:
            stock_list, totals, current_index = add_stock(stock_list, totals, current_index)
        case 2:
            stock_list, totals, current_index = sell_stock(stock_list, totals, current_index)
        case 3:
            stock_list, totals = update_stock_info(stock_list, totals)
        case 4:
            save_totals(totals)
            save_stock_list(stock_list)
            sys.exit()

    return stock_list, totals, current_index


def sell_stock(stock_list, totals, current_index):
    indexes = list(int(stock["Index"]) for stock in stock_list)
    # checks to see if there are stocks available to sell, returns to menu if none to sell
    if len(indexes) == 0:
        input("There are no stocks available to sell, press enter to continue: ")
        return stock_list, totals, current_index

    while True:
        try:
            stock_to_sell = int(input("Type the index of the stock to sell: "))
            if stock_to_sell in indexes:
                break
            else:
                print("Stock does not exist, please enter a valid index.")

        except ValueError:
            print("Please enter a valid integer index.")

    for stock in stock_list[stock_to_sell - 1:]:
        stock["Index"] = int(stock["Index"]) - 1

    total_cash = float(totals["Total Cash"][1:])
    total_invested = float(totals["Total Invested"][1:])

    # adds cash of stock being sold to total cash and removes stock's value from invested money
    current_stock_price = float(stock_list[stock_to_sell - 1]["Price (USD)"])
    totals["Total Cash"] = f"${'{:.2f}'.format(total_cash + current_stock_price)}"
    totals["Total Invested"] = f"${'{:.2f}'.format(total_invested - current_stock_price)}"

    input(f"{stock_list[stock_to_sell - 1]['Stock Name']} has been sold, press enter to continue: ")
    del stock_list[stock_to_sell - 1]
    current_index -= 1

    return stock_list, totals, current_index


# gets list of previously added stocks from saved file or creates a new file if it doesn't exist
def get_stock_list():
    stock = []
    while True:
        try:
            with open("stock_list.csv", "r") as f:
                reader = csv.DictReader(f)
                for line in reader:
                    stock.append(line)
            return stock

        except FileNotFoundError:
            with open("stock_list.csv", "w") as f:
                f.write("Ticker,Stock Name,Quantity,Price (USD),%Chng,Date Added,Purchased@,Current Price,Index\n")


def get_totals() -> dict:
    while True:
        try:
            with open("totals.csv", "r") as f:
                reader = csv.DictReader(f)
                line: dict
                for line in reader:
                    return line

        except FileNotFoundError:
            with open("totals.csv", "w") as f:
                f.write("Total Cash,Total Invested\n$10000,$0")


def print_table(stock_list):
    print(tabulate(stock_list, headers="keys", tablefmt="rounded_outline", numalign="center"))


# prints table with headers in first column and data to right
def get_totals_table(totals: dict):
    formatted_data = [[header, values] for header, values in totals.items()]
    return tabulate(formatted_data, tablefmt="rounded_outline", numalign="center")


def save_stock_list(stock_list):
    with open("stock_list.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Ticker", "Stock Name", "Quantity", "Price (USD)", "%Chng",
                                               "Date Added", "Purchased@", "Current Price", "Index"])
        writer.writeheader()
        for row in stock_list:
            writer.writerow(row)


def save_totals(totals: dict):
    with open("totals.csv", "w") as f:
        writer = csv.DictWriter(f, fieldnames=["Total Cash", "Total Invested"])
        writer.writeheader()
        writer.writerow(totals)


def update_stock_info(stock_list, totals):
    seen = set()
    new_invested_amount = 0

    # stores prices that have already been retrieved via the API
    found_stock_prices = {}

    for stock in stock_list:
        # checks to see if a request for the price of the stock has been sent already, and we have its current price
        # It will update the price of the stock from within the list of already requested prices of stocks
        if stock["Ticker"] in seen:
            current_stock_price = found_stock_prices[stock["Ticker"]]
            total_price = current_stock_price * float(stock["Quantity"])
            stock["Price (USD)"] = f"{total_price:.2f}"
            # Will send a request for the current price of the stock and update the stock_list

            stock["Current Price"] = current_stock_price
            stock["%Chng"] = calculate_perc_change(current_stock_price, float(stock["Purchased@"]))

            new_invested_amount += total_price
        else:
            try:
                current_stock_price = get_current_stock_price(stock["Ticker"], api_key)
            except KeyError:
                return
            found_stock_prices.update({stock["Ticker"]: current_stock_price})  # saves for use in case a duplicate is
            # found so that another request doesn't have to be made
            total_price = current_stock_price * float(stock["Quantity"])
            stock["Price (USD)"] = f"{total_price:.2f}"

            stock["Current Price"] = current_stock_price
            stock["%Chng"] = calculate_perc_change(current_stock_price, float(stock["Purchased@"]))
            seen.add(stock["Ticker"])

            new_invested_amount += total_price

    totals["Total Invested"] = f"${new_invested_amount:.2f}"
    return stock_list, totals


# writes new stock to file and returns original stock list with new stock appended
def add_stock(stock_list, totals: dict, current_index):
    user_input_tckr = input("Enter ticker symbol: ").upper().strip()

    while True:
        try:
            current_price = get_current_stock_price(user_input_tckr, api_key)
            break
        except ValueError:
            user_input_tckr = input("Enter a valid ticker symbol: ").upper().strip()
        except KeyError:
            return stock_list, totals, current_index

    while True:
        try:
            user_input_quantity = float(input("Enter quantity: "))
            break
        except ValueError:
            print("Enter valid quantity")

    total_cost = float(f"{current_price * user_input_quantity:.2f}")
    total_cash_available = float(totals["Total Cash"][1:])
    total_invested_already = float(totals["Total Invested"][1:])
    remaining_cash = total_cash_available - total_cost

    if remaining_cash < 0:
        print("You have insufficient funds to perform this transaction.")
        input("Press enter to continue: ")
        print()
        return stock_list, totals, current_index
    else:
        # updates values in totals to after transaction is completed
        totals["Total Cash"] = f"${remaining_cash:.2f}"
        totals["Total Invested"] = f"${total_invested_already + total_cost:.2f}"

        try:
            stock_name = get_stock_name(user_input_tckr, api_key)
        except KeyError:
            return stock_list, totals, current_index

        current_index += 1

        with open("stock_list.csv", "a", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["Ticker", "Stock Name", "Quantity", "Price (USD)", "%Chng",
                                                   "Date Added", "Purchased@", "Current Price", "Index"])

            new_info = {"Ticker": user_input_tckr, "Stock Name": stock_name, "Quantity": user_input_quantity,
                        "Price (USD)": total_cost, "%Chng": "0.00%", "Date Added": datetime.date.today(),
                        "Purchased@": current_price, "Current Price": current_price, "Index": current_index}

            writer.writerow(new_info)

            stock_list.append(new_info)
            input("Stock has been added, press enter to continue: ")

            return stock_list, totals, current_index


# calculates percentage difference from when stock was purchased to current price
def calculate_perc_change(current_price, purchased_price):
    change = ((current_price - purchased_price) / purchased_price) * 100
    change_formatted = "{:,.2f}".format(change)
    return f"{change_formatted}%"


def get_current_stock_price(ticker, api):
    url = f"https://api.twelvedata.com/price?symbol={ticker}&apikey={api}"
    response = requests.get(url).json()

    if "code" in response.keys():
        if response["code"] == 400:
            print("Stock does not exist")
            raise ValueError
        elif response["code"] == 429:
            print("Maximum API credits within the minute have been used")
            print("Please wait 60 seconds for API reset")
            input("Press enter to continue, data will not be refreshed: ")
            raise KeyError
    else:
        current_price = response["price"][:-3]
        return float(current_price)


def get_stock_name(ticker, api):
    url = f"https://api.twelvedata.com/quote?symbol={ticker}&apikey={api}"
    response = requests.get(url).json()

    if "code" in response.keys():
        if response["code"] == 429:
            print("Maximum API credits within the minute have been used")
            print("Please wait 60 seconds for API reset")
            input("Press enter to continue: ")
            raise KeyError
    else:
        return response["name"]


def update_totals(total_cash, total_invested):
    new_info = {"Total Cash": f"${total_cash}", "Total Invested": f"${total_invested}"}

    with open("totals.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Total Cash", "Total Invested"])
        writer.writerow(new_info)

    return new_info


def main():
    totals: dict = get_totals()
    stocks: list = get_stock_list()
    if len(stocks) != 0:
        current_index = int(stocks[-1]["Index"])
    else:
        current_index = 0

    stocks, totals = update_stock_info(stocks, totals)

    while True:
        print()
        print(get_totals_table(totals))
        print_table(stocks)

        stocks, totals, current_index = display_menu_options(stocks, totals, current_index)


if __name__ == '__main__':
    main()
