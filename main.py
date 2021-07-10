import numpy as np
import pandas as pd
from pandas_datareader import data as wb
import matplotlib.pyplot as plt
from datetime import datetime

sig_figs = 4
annual_market_days = 365


# Get the user to enter the ticker symbols from their portfolio
def get_tickers():
    user_input = 'Y'
    sentinel = '<DONE>'
    tickers = []

    while user_input != sentinel:
        temp = input('Please enter a ticker symbol (enter "<DONE>" when done): ')
        if temp == sentinel:
            print("Your stock ticker's: ", tickers)
            return tickers
        user_input = temp.upper()
        tickers.append(user_input)

    print('Your stock tickers: ', tickers)
    return tickers


# Get the percentage weights of each stock in the users portfolio
def get_weights(tickers):
    weights = []
    logic_satisfied = False

    while logic_satisfied == False:

        for i in range(len(tickers)):
            weight = abs(float(input('Please enter the portfolio weight of ' + str(tickers[i]) + ' (as a decimal): ')))
            weights.append(weight)

        if sum(weights) == 1.0:
            logic_satisfied = True
            print("Weight's Accepted")
            return weights
        else:
            print("Weight's Invalid, sum of weights must equal 1.0")
            weights = []

    print('Your portfolio weights: ', weights)
    return weights


# Get the adjusted close price for each stock. All data pulled from Yahoo's API
def get_stock_data(stocks_list):
    tickers = stocks_list
    stock_data = pd.DataFrame()
    start_date = str(input('Enter Start Date (ex:2019-1-1): '))
    end_date = str(input('Enter End Date (ex:2020-1-1): '))

    try:
        for t in tickers:
            stock_data[t] = wb.DataReader(t, data_source='yahoo', start=datetime.strptime(start_date, "%Y-%m-%d"),
                                          end=datetime.strptime(end_date, "%Y-%m-%d"))['Adj Close']
        return stock_data
    except RemoteDataError:
        print('RemoteDataError')
        return stock_data
    except KeyError:
        print('KeyError')
        return stock_data


# Generate a plot displaying the change in stock price for each stock in the portfolio
def generate_plot(stock_data):
    # Normalization to 100
    (stock_data / stock_data.iloc[0] * 100).plot(figsize=(15, 6))
    plt.ylabel('Adj Close')
    plt.show()
    return


# Calculate the portfolio return
def calculate_return(stock_data, weights):
    daily_returns = np.log(stock_data/stock_data.shift(1))
    annual_returns = daily_returns.mean() * annual_market_days
    portfolio_return = str(round(np.dot(annual_returns, weights), sig_figs) * 100) + ' %'
    print('The portfolio return is: ' + portfolio_return)
    return portfolio_return


# Calculate the portfolio risk
def calculate_risk(weights, stock_data):
    weights = np.array(weights)
    daily_returns = np.log(stock_data/stock_data.shift(1))
    annual_returns = daily_returns * annual_market_days
    portfolio_variance = np.dot(weights.T, np.dot(annual_returns.cov(), weights))
    portfolio_risk = str(round(portfolio_variance ** 0.5, sig_figs) * 100) + ' %'
    print('The portfolio risk is: ' + portfolio_risk)
    return portfolio_risk


# Optimize portfolio's in regards to stock weights and portfolio return
def optimize_portfolio(tickers, stock_data):
    tickers = np.array(tickers)
    daily_returns = np.log(stock_data/stock_data.shift(1))
    num_tickers= len(tickers)
    new_portfolio_returns = []
    new_portfolio_volatility = []

    # Loop through 1000 iterations of random weights
    for x in range(1000):
        weights = np.random.random(num_tickers)
        weights /= np.sum(weights)  # Done to ensure the random weights sum to 1.0
        new_portfolio_returns.append(np.sum(weights * daily_returns.mean()) * annual_market_days)
        new_portfolio_volatility.append(np.sqrt(np.dot(weights.T, np.dot(daily_returns.cov() * annual_market_days, weights))))

    new_portfolio_returns = np.array(new_portfolio_returns)
    new_portfolio_volatility = np.array(new_portfolio_volatility)
    portfolios = pd.DataFrame({'Return': new_portfolio_returns, 'Volatility': new_portfolio_volatility})
    portfolios.plot(x='Volatility', y='Return', kind='scatter', figsize=(10, 6))
    plt.xlabel('Expected Volatility')
    plt.ylabel('Expected Return')
    plt.show()
    return


tickers = get_tickers()
weights = get_weights(tickers)
stock_data = get_stock_data(tickers)
generate_plot(stock_data)
portfolio_return = calculate_return(stock_data, weights)
calculate_risk(weights, stock_data)
optimize_portfolio(tickers, stock_data)