# -*- coding: utf-8 -*-
"""
Created on Wed Oct 22 14:31:39 2025

@author: lauta
"""

from cryptoquant.request_handler_class import RequestHandler

class AltCoins(RequestHandler):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        
        # Market Data
        self.ALT_MARKET_OHLCV = "alt/market-data/price-ohlcv"
        
    # -------------------------------
    # Market Data
    # -------------------------------
    
    def get_alts_mkt_ohlcv(self, **query_params):
        """
        This endpoint returns metrics related to Alt Token's Index Price. Price
        OHLCV data consists of five metrics.  open, the opening price at the
        beginning of the window, close, USD closing price at the end of the 
        window,  high, the highest USD price in a given window, low, the lowest 
        USD price in a given window, and volume, the total token volume traded 
        in a given window.
        
        At this endpoint, metrics are calculated by Minute, Hour and Day. Alt 
        Token Index Price is calculated by taking VWAP(Volume Weighted Average
        Price) of Alt Token price data aggregated from global exchanges.

        Parameters
        ----------
        **query_params : TYPE
            token (str, required): An Alt token from the table that CQ support.
            window (str, optional): day, hour, and min.
            from_ (any, optional): This defines the starting time for which data
                                will be gathered, formatted as YYYYMMDDTHHMMSS 
                                (indicating YYYY-MM-DDTHH:MM:SS, UTC time). 
                                If window=day is used, it can also be formatted 
                                as YYYYMMDD (date). If window=block is used, you
                                can also specify the exact block height (e.g. 510000). 
                                If this field is not specified, response will 
                                include data from the earliest time.
           to_ (any, optinal): This defines the ending time for which data will
                               be gathered, formatted as YYYYMMDDTHHMMSS 
                               (indicating YYYY-MM-DDTHH:MM:SS, UTC time). 
                               If window=day is used, it can also be formatted 
                               as YYYYMMDD (date). If window=block is used, you
                               can also specify the exact block height (e.g. 510000).
                               If this field is not specified, response will 
                               include data from the latest time
           limit (int, optional): The maximum number of entries to return before
                                  the latest data point (or before to if specified).
                                  This field ranges from 1 to 100,000.
           format (str, optional): A format type about return message type. 
                                   Supported formats are json, csv

        Returns
        -------
        dict
            Price OHLCV data.


        """
        return super().handle_request(self.ALT_MARKET_OHLCV, query_params)