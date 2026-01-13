from datetime import datetime
from .utils import normalise_ticker

import yfinance as yf
import lxml
from lxml import html
import requests
import numpy as np
import pandas as pd
import bs4
""" 

    To get the name of symbol/ticker of the stocks for which you want information you can
    look it up on https://finance.yahoo.com/ and from there you can pass the scrip name
    in the parameter where required. 

"""

def get_balance_sheet(symbol):

    """ 

        Used to obtain the balance sheet of the specified ticker

        Parameters
        --------------------------------

        symbol :    It is used to specify the symbol/ticker for which the 
                    balance sheet has to be fetched

        Returns
        --------------------------------
        
        A dataframe that contains the balance sheet of the company
    
    """
    symbol = normalise_ticker(symbol)
    ticker = yf.Ticker(symbol)

    bal_sheet = ticker.get_balance_sheet()
    return bal_sheet

def get_cash_flow(symbol, quarterly: bool = True):

    """ 

        Used to obtain the cash flow statement of the specified ticker

        Parameters
        --------------------------------

        symbol : str
        The stock symbol/ticker for which the cash flow statement is required.

        quarterly : bool, optional (default=True)
        If True, returns the quarterly cash flow statement.
        If False, returns the annual cash flow statement.

        Returns
        --------------------------------
        
        A dataframe that contains the cash flow statement of the company
    
    """

    symbol = normalise_ticker(symbol)
    ticker = yf.Ticker(symbol)

    if quarterly:
        return ticker.quarterly_cashflow
    else:
        return ticker.get_cashflow()

def get_income_statement(symbol, quarterly: bool = True):

    """ 

        Used to obtain the income statement of the specified ticker

        Parameters
        --------------------------------

        symbol : str
        The stock symbol/ticker for which the income statement is required.

        quarterly : bool, optional (default=False)
        If True, returns the quarterly income statement.
        If False, returns the annual income statement.

        Returns
        --------------------------------
        
        A dataframe that contains the income statement of the company
    
    """
    symbol = normalise_ticker(symbol)
    ticker = yf.Ticker(symbol)

    if quarterly:
        return ticker.quarterly_income_stmt
    else:
        return ticker.get_income_stmt()
