# Stock Portfolio Manager

## Overview

This program allows managing a stock portfolio by providing capabilities to:

- Buy new stocks
- Sell existing stocks
- View current portfolio
- Refresh stock prices and portfolio value
- Save portfolio to file

It uses a simple command-line interface for user input and output.

Under the hood, it uses the [TwelveData API](https://twelvedata.com/) to fetch current stock price data. The portfolio is persisted in CSV files.

## Code Details

The main components of the code are:

### Data Storage

- `stock_list.csv`: Stores portfolio holdings with details like ticker, name, quantity etc.
- `totals.csv`: Stores total cash and invested amount.
- `get_stock_list()`: Loads data from stock_list.csv into a list.
- `get_totals()`: Loads totals from totals.csv into a dict.

### Portfolio Management 

- `add_stock()`: Adds a new stock to portfolio. Validates inputs, checks funds, fetches price, updates totals and list. 
- `sell_stock()`: Removes a stock from portfolio. Updates totals, prints confirmation, decrements indexes.
- `update_stock_info()`: Refreshes prices and percentages for all stocks. Fetches latest data via API.

### Display and Output

- `print_table()`: Prints portfolio stocks in tabular format with details.
- `get_totals_table()`: Formats and prints totals data.
- `display_menu_options()`: Shows menu options and handles user input.

### API and Calculations

- `get_current_stock_price()`: Fetches latest price for a symbol using the TwelveData API.
- `get_stock_name()`: Fetches company name for a symbol.
- `calculate_perc_change()`: Calculates percentage change between current and purchased price.

### Program Flow

- Load data from CSV files
- Display menu
- Handle user choices
  - Buy, sell, refresh, save & quit
- Update data after actions
- Refresh prices from API
- Save data back to files on exit

## Usage

The program is run as:

```
python project.py
```

On startup, existing data is loaded from the CSV files. If running for the first time, sample data is created.

The main menu is displayed. User can choose options like:

1. Buy stock
   - Enter symbol and quantity
   - Check for sufficient funds
   - Fetch current price
   - Update portfolio
2. Sell stock
   - Select stock index
   - Update portfolio
   - Remove stock
3. Refresh portfolio
4. Save and quit

All actions are reflected in the portfolio view and in the CSV files on disk.