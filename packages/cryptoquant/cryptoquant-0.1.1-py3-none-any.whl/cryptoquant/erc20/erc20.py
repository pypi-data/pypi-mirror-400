# -*- coding: utf-8 -*-
"""
Created on Wed Oct 22 12:57:13 2025

@author: lauta
"""

from cryptoquant.request_handler_class import RequestHandler

class Erc20(RequestHandler):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        
        # Entity list
        self.ERC20_ENTITY_LIST = "erc20/status/entity-list"
        # Exchange flows
        self.ERC20_EXCHANGE_FLOWS_RESERVE = "erc20/exchange-flows/reserve"
        self.ERC20_EXCHANGE_FLOWS_NETFLOW = "erc20/exchange-flows/netflow"
        self.ERC20_EXCHANGE_FLOWS_INFLOW = "erc20/exchange-flows/inflow"
        self.ERC20_EXCHANGE_FLOWS_OUTFLOW = "erc20/exchange-flows/outflow"
        self.ERC20_EXCHANGE_FLOWS_TRANSACTIONS_COUNT = "erc20/exchange-flows/transactions-count"
        self.ERC20_EXCHANGE_FLOWS_ADDRESSES_COUNT = "erc20/exchange-flows/addresses-count"
        # Flow Indicator
        self.ERC20_EXCHANGE_FLOWS_SUPPLY_RATIO = "erc20/flow-indicator/exchange-supply-ratio"
        # Market data
        self.ERC20_MARKET_OHLCV = "erc20/market-data/price-ohlcv"
        # Network data
        self.ERC20_NETWORK_SUPPLY = "erc20/network-data/supply"
        self.ERC20_NETWORK_VELOCITY = "erc20/network-data/velocity"
        self.ERC20_NETWORK_TRANSACTIONS_COUNT = "erc20/network-data/transactions-count"
        self.ERC20_NETWORK_TOKENS_TRANSFERRED_COUNT = "erc20/network-data/tokens-transferred-count"
        self.ERC20_NETWORK_TOKENS_TRANSFERRED = "erc20/network-data/tokens-transferred"
        self.ERC20_NETWORK_ADDRESSES_COUNT = "erc20/network-data/addresses-count"
        
    # -------------------------------
    # Entity list
    # -------------------------------
    
    def get_erc20_entity_list(self, **query_params):
        """
        This endpoint returns entity list to serve data. The meaning of the 
        market_type value of the exchange object is as follows. For exchange 
        objects, the market_type field tells whether the exchange is a spot 
        exchange or a derivative exchange. Entities without a market type, such 
        as miners or banks, will return 0 for market_type.

        Exchange Market Type	Description
        0	                    Undefined
        1	                    Spot Exchange
        2	                    Derivative Exchange

        Parameters
        ----------
        **query_params : TYPE
            token (str, required): A ERC20 token from the table that CQ support.
            type_ (str, required): A type from the entity in exchange.
            format (str, optional): A format type about return message type. 
                                    Supported formats are json, csv.

        Returns
        -------
        dict
            Entity list on a given type.

        """
        return super().handle_request(self.ERC20_ENTITY_LIST, query_params)
    
    # -------------------------------
    # Exchange Flows
    # -------------------------------
    
    def get_erc20_exch_reserve(self, **query_params):
        """
        This endpoint returns the full historical on-chain ERC20 token balance 
        of exchanges.

        Parameters
        ----------
        **query_params : TYPE
            token (str, required): A ERC20 token from the table that CQ support.
            exchange (str, required): An exchange supported by CryptoQuant.
            window (str, optional): day, hour, and block.
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
            The amount of ERC 20 token on a given exchange on this window.

        """
        return super().handle_request(self.ERC20_EXCHANGE_FLOWS_RESERVE, query_params)
    
    def get_erc20_exch_netflow(self, **query_params):
        """
        The difference between coins flowing into exchanges and flowing out of 
        exchanges. Netflow usually helps us to figure out an increase of idle 
        coins waiting to be traded in a certain time frame.

        Parameters
        ----------
        **query_params : TYPE
            token (str, required): A ERC20 token from the table that CQ support.
            exchange (str, required): An exchange supported by CryptoQuant.
            window (str, optional): day, hour, and block.
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
            Total netflow.

        """
        return super().handle_request(self.ERC20_EXCHANGE_FLOWS_NETFLOW, query_params)
    
    def get_erc20_exch_inflow(self, **query_params):
        """
        This endpoint returns the inflow of ERC20 token into exchange wallets 
        for as far back as we track. The average inflow is the average 
        transaction value for transactions flowing into exchange wallets on a 
        given day.

        Parameters
        ----------
        **query_params : TYPE
            token (str, required): A ERC20 token from the table that CQ support.
            exchange (str, required): An exchange supported by CryptoQuant.
            window (str, optional): day, hour, and block.
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
            Inflow statistics.

        """
        return super().handle_request(self.ERC20_EXCHANGE_FLOWS_INFLOW, query_params)
    
    def get_erc20_exch_outflow(self, **query_params):
        """
        This endpoint returns the outflow of ERC20 token into exchange wallets
        for as far back as we track. The average outflow is the average 
        transaction value for transactions flowing into exchange wallets on a 
        given day.

        Parameters
        ----------
        **query_params : TYPE
            token (str, required): A ERC20 token from the table that CQ support.
            exchange (str, required): An exchange supported by CryptoQuant.
            window (str, optional): day, hour, and block.
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
            outflow statistics.

        """
        return super().handle_request(self.ERC20_EXCHANGE_FLOWS_OUTFLOW, query_params)
    
    def get_erc20_exch_trx_count(self, **query_params):
        """
        This endpoint returns the number of transactions flowing in/out of 
        ERC20 token exchanges.

        Parameters
        ----------
        **query_params : TYPE
            token (str, required): A ERC20 token from the table that CQ support.
            exchange (str, required): An exchange supported by CryptoQuant.
            window (str, optional): day, hour, and block.
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
            Transactions in and out.

        """
        return super().handle_request(self.ERC20_EXCHANGE_FLOWS_TRANSACTIONS_COUNT, query_params)
    
    def get_erc20_exch_addrs_count(self, **query_params):
        """
        This endpoint returns the number of addresses involved in 
        inflow/outflow transactions.

        Parameters
        ----------
        **query_params : TYPE
            token (str, required): A ERC20 token from the table that CQ support.
            exchange (str, required): An exchange supported by CryptoQuant.
            window (str, optional): day, hour, and block.
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
            The number of addresses evoking inflow/outflow transactions to
            exchange wallets.

        """
        return super().handle_request(self.ERC20_EXCHANGE_FLOWS_ADDRESSES_COUNT, query_params)
    
    # -------------------------------
    # Flow indicators
    # -------------------------------
    
    def get_erc20_exch_supply_ratio(self, **query_params):
        """
        Exchange Supply Ratio is calculated as exchange reserve divided by 
        total supply. The metric measures how much tokens are reserved in the
        exchange relative to total supply of the token.

        Parameters
        ----------
        **query_params : TYPE
            token (str, required): A ERC20 token from the table that CQ support.
            exchange (str, required): An exchange supported by CryptoQuant.
            window (str, optional): day, hour, and block.
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
            Ratio of reserved token in the exchange relative to total supply.

        """
        return super().handle_request(self.ERC20_EXCHANGE_FLOWS_SUPPLY_RATIO, query_params)
    
    # -------------------------------
    # Market data
    # -------------------------------
    
    def get_erc20_mkt_ohlcv(self, **query_params):
        """
        This endpoint returns metrics related to ERC20 Token's Index Price.
        Price OHLCV data consists of five metrics.  open, the opening price at
        the beginning of the window, close, USD closing price at the end of the
        window,  high, the highest USD price in a given window, low, the lowest
        USD price in a given window, and volume, the total token volume traded 
        in a given window.
        
        At this endpoint, metrics are calculated by Minute, Hour and Day. ERC20 
        Token Index Price is calculated by taking VWAP(Volume Weighted Average 
        Price) of ERC20 Token price data aggregated from global exchanges.

        Parameters
        ----------
        **query_params : TYPE
            token (str, required): A ERC20 token from the table that CQ support.
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
        return super().handle_request(self.ERC20_MARKET_OHLCV, query_params)
    
    # -------------------------------
    # Network data
    # -------------------------------
    
    def get_erc20_ntx_supply(self, **query_params):
        """
        This endpoint returns metrics related to the supply of ERC20 tokens, 
        i.e. the amount of ERC20s tokens in existence. CQ currently provide 
        three metrics, supply_total, the total amount of ERC20 tokens in 
        existence, supply_minted, the amount of newly issued tokens, and 
        supply_burned, the amount of newly burnt tokens in a given window.

        Parameters
        ----------
        **query_params : TYPE
            token (str, required): A ERC20 token from the table that CQ support.
            window (str, optional): day, hour, 10min, and block.
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
            Supply statistics.

        """
        return super().handle_request(self.ERC20_NETWORK_SUPPLY, query_params)
    
    def get_erc20_ntx_velocity(self, **query_params):
        """
        This endpoint returns metrics related to the velocity of ERC20 tokens. 
        Velocity is calculated by dividing the trailing 1 year estimated 
        transaction volume(the cumulated sum of transferred tokens) by current 
        supply. Velocity is a metric that explains how actively is money 
        circulating in the market.

        Parameters
        ----------
        **query_params : TYPE
            token (str, required): A ERC20 token from the table that CQ support.
            window (str, optional): day, hour, 10min, and block.
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
            Estimated transaction volume in the trailing 1 year divided by
            current total supply.

        """
        return super().handle_request(self.ERC20_NETWORK_VELOCITY, query_params)
    
    def get_erc20_ntx_trx_count(self, **query_params):
        """
        This endpoint returns metrics related to the number of transactions. CQ
        provide several metrics, transactions_count_total, the total number of 
        transactions, transactions_count_mean, the mean number of transactions.
        Note all events executed by the ERC20 contract are counted.

        Parameters
        ----------
        **query_params : TYPE
            token (str, required): A ERC20 token from the table that CQ support.
            window (str, optional): day, hour, 10min, and block.
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
            Statistics for transactions count.

        """
        return super().handle_request(self.ERC20_NETWORK_TRANSACTIONS_COUNT, query_params)
    
    def get_erc20_ntx_tokens_transferred_count(self, **query_params):
        """
        This endpoint returns metrics related to the number of tokens 
        transferred executed. We provide several metrics, 
        tokens_transferred_count_total, the total number of executed tokens 
        transferred, and tokens_transferred_count_mean, the mean number of 
        executed tokens transferred. Note only successful transfers (value > 0)
        are counted.

        Parameters
        ----------
        **query_params : TYPE
            token (str, required): A ERC20 token from the table that CQ support.
            window (str, optional): day, hour, 10min, and block.
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
            token transferred statistics.

        """
        return super().handle_request(self.ERC20_NETWORK_TOKENS_TRANSFERRED_COUNT, query_params)
    
    def get_erc20_ntx_tokens_transferred(self, **query_params):
        """
        This endpoint returns metrics related to the number of tokens 
        transferred, i.e transaction volume. We provide several metrics, 
        tokens_transferred_total, the total number of transferred tokens in 
        that window, tokens_transferred_mean, the mean of transferred tokens 
        per transaction in that window, and tokens_transferred_median, the
        median of tokens transferred per transaction.

        Parameters
        ----------
        **query_params : TYPE
            token (str, required): A ERC20 token from the table that CQ support.
            window (str, optional): day, hour, 10min, and block.
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
            Token transferred statistics (different that only counts).

        """
        return super().handle_request(self.ERC20_NETWORK_TOKENS_TRANSFERRED, query_params)
    
    def get_erc20_ntx_addrs_count(self, **query_params):
        """
        This endpoint returns metrics relating to the number of used to 
        transfer the tokens. CQ provide several metrics, addresses_count_active, 
        the total number of unique addresses that were active (either sender or
        receiver) on the blockchain in a given window, addresses_count_sender, 
        the number of addresses that were active as a sender, and 
        addresses_count_receiver, the number of addresses that were active as a
        receiver.

        Parameters
        ----------
        **query_params : TYPE
            token (str, required): A ERC20 token from the table that CQ support.
            window (str, optional): day, hour, 10min, and block.
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
            Statistics for addresses in the network of the token.

        """
        return super().handle_request(self.ERC20_NETWORK_ADDRESSES_COUNT, query_params)