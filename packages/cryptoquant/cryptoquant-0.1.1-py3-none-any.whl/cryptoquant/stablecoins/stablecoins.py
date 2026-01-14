# -*- coding: utf-8 -*-
"""
Created on Mon Oct 20 09:15:55 2025

@author: lauta
"""

from cryptoquant.request_handler_class import RequestHandler

class StableCoins(RequestHandler):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        
        # Entity List
        self.SC_ENTITY_LIST = "stablecoin/status/entity-list"
        # Exchange Flows
        self.SC_EXCH_RESERVE = "stablecoin/exchange-flows/reserve"
        self.SC_EXCH_NETFLOW = "stablecoin/exchange-flows/netflow"
        self.SC_EXCH_INFLOW = "stablecoin/exchange-flows/inflow"
        self.SC_EXCH_OUTFLOW = "stablecoin/exchange-flows/outflow"
        self.SC_EXCH_TRANSACTIONS_COUNT = "stablecoin/exchange-flows/transactions-count"
        self.SC_EXCH_ADDRESSES_COUNT = "stablecoin/exchange-flows/addresses-count"
        # Flow Indicator
        self.SC_FLOW_EXCHANGE_SUPPLY_RATIO = "stablecoin/flow-indicator/exchange-supply-ratio"
        # Price OHLCV
        self.SC_MARKET_OHLCV = "stablecoin/market-data/price-ohlcv"
        self.SC_MARKET_CAPITALIZATION = "stablecoin/market-data/capitalization"
        # Network Data
        self.SC_NETWORK_SUPPLY = "stablecoin/network-data/supply"
        self.SC_NETWORK_EVENTS_COUNT = "stablecoin/network-data/events-count"
        self.SC_NETWORK_TOKENS_TRANSFERRED = "stablecoin/network-data/tokens-transferred"
        self.SC_NETWORK_ADDRESSES_COUNT = "stablecoin/network-data/addresses-count"
        
    # -----------------------------
    # Entity List
    # -----------------------------
    
    def get_stable_entity_list(self, **query_params):
        """
        This endpoint returns entity list to serve data. Please note that 
        all_token will return bad request for this endpoint. Make sure to use a
        specific stablecoin symbol. The meaning of the market_type value of the
        exchange object is as follows. For exchange objects, the market_type 
        field tells whether the exchange is a spot exchange or a derivative 
        exchange. Entities without a market type, such as miners or banks, will 
        return 0 for market_type.

        Parameters
        ----------
        **query_params : TYPE
            token (str, required): A stablecoin from the table that CQ support.
            type (str, required): A type from the entity exchange.
            format (str, optional): A format type about return message type. 
                                    Supported formats are json, csv.

        Returns
        -------
        dict
            Entity list on a given type.

        """
        return super().handle_request(self.SC_ENTITY_LIST, query_params)
    
    # -----------------------------
    # Exchange Flows
    # -----------------------------
    
    def get_stable_exch_reserve(self, **query_params):
        """
        This endpoint returns the full historical on-chain balance of 
        Stablecoin exchanges.

        Parameters
        ----------
        **query_params : TYPE
            token (str, required): A stablecoin from the table that CQ support.
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
            The amount of Stablecoin on a given exchange on this window.

        """
        return super().handle_request(self.SC_EXCH_RESERVE, query_params)
    
    def get_stable_exch_netflow(self, **query_params):
        """
        The difference between coins flowing into exchanges and flowing out of 
        exchanges. Netflow usually helps us to figure out an increase of idle 
        coins waiting to be traded in a certain time frame.

        Parameters
        ----------
        **query_params : TYPE
            token (str, required): A stablecoin from the table that CQ support.
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
        return super().handle_request(self.SC_EXCH_NETFLOW, query_params)
    
    def get_stable_exch_inflow(self, **query_params):
        """
        This endpoint returns the inflow of Stablecoin into exchange wallets 
        for as far back as we track. The average inflow is the average 
        transaction value for transactions flowing into exchange wallets on a 
        given day.

        Parameters
        ----------
        **query_params : TYPE
            token (str, required): A stablecoin from the table that CQ support.
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
            Inflwo statistics for stablecoins inflows.

        """
        return super().handle_request(self.SC_EXCH_INFLOW, query_params)
    
    def get_stable_exch_outflow(self, **query_params):
        """
        This endpoint returns the outflow of Stablecoin into exchange wallets 
        for as far back as we track. The average outflow is the average 
        transaction value for transactions flowing into exchange wallets on a
        given day.

        Parameters
        ----------
        **query_params : TYPE
            token (str, required): A stablecoin from the table that CQ support.
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
            Inflwo statistics for stablecoins outflows.

        """
        return super().handle_request(self.SC_EXCH_OUTFLOW, query_params)
    
    def get_stable_exch_trx_count(self, **query_params):
        """
        This endpoint returns the number of transactions flowing in/out of 
        Stablecoin exchanges.

        Parameters
        ----------
        **query_params : TYPE
            token (str, required): A stablecoin from the table that CQ support.
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
            Transaction count inflows and outflows.

        """
        return super().handle_request(self.SC_EXCH_TRANSACTIONS_COUNT, query_params)
    
    def get_stable_exch_addrs_count(self, **query_params):
        """
        This endpoint returns the number of addresses involved in 
        inflow/outflow transactions.

        Parameters
        ----------
        **query_params : TYPE
            token (str, required): A stablecoin from the table that CQ support.
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
        return super().handle_request(self.SC_EXCH_ADDRESSES_COUNT, query_params)
    
    # -----------------------------
    # Flow Indicator
    # -----------------------------
    
    def get_stable_flow_exch_supply_ratio(self, **query_params):
        """
        Exchange Supply Ratio is calculated as exchange reserve divided by 
        total supply. The metric measures how much tokens are reserved in the 
        exchange relative to total supply of the token.

        Parameters
        ----------
        **query_params : TYPE
            token (str, required): A stablecoin from the table that CQ support.
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
            Ratio of reserved token in the exchange relative to the total 
            supply.

        """
        return super().handle_request(self.SC_FLOW_EXCHANGE_SUPPLY_RATIO, query_params)
    
    # -----------------------------
    # Market Data
    # -----------------------------
    
    def get_stable_mkt_ohlcv(self, **query_params):
        """
        This endpoint returns metrics related to Stablecoin's Index Price.
        Price OHLCV data consists of five metrics.  open, the opening price at 
        the beginning of the window, close, USD closing price at the end of the 
        window,  high, the highest USD price in a given window, low, the lowest 
        USD price in a given window, and volume, the total token volume traded 
        in a given window.
        
        At this endpoint, metrics are calculated by Minute, Hour and Day.
        Stablecoin Index Price is calculated by taking VWAP(Volume Weighted 
        Average Price) of Stablecoin price data aggregated from global
        exchanges. 

        Parameters
        ----------
        **query_params : TYPE
            token (str, required): A stablecoin from the table that CQ support.
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
        return super().handle_request(self.SC_MARKET_OHLCV, query_params)
    
    def get_stable_mkt_capitalization(self, **query_params):
        """
        This endpoint returns metrics related to market capitalization. We 
        currently provide market_cap, which is total market capitalization of 
        the token, calculated by multiplying the circulating supply with its 
        USD price(circulating_supply * price_usd_close).

        Parameters
        ----------
        **query_params : TYPE
            token (str, required): A stablecoin from the table that CQ support.
            window (str, optional): day and block.
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
            Market capitalization of the stable coin, calculated by total
            supply times price close.

        """
        return super().handle_request(self.SC_MARKET_CAPITALIZATION, query_params)
    
    # -----------------------------
    # Network Data
    # -----------------------------
    
    def get_stable_ntx_supply(self, **query_params):
        """
        This end point returns metrics related to token supply, i.e. the amount 
        of tokens in existence. CQ currently provide six metrics. supply_total 
        is the total amount of tokens in existence, and supply_circulating is
        an approximation of the amount of tokens that are circulating in the 
        market(e.g. excluding tokens owned by the issuing company's treasury 
        address). supply_minted and supply_burned represents how many tokens 
        were added/subtracted from supply_total. supply_issued and 
        supply_redeemed represents how many tokens were added/subtracted from 
        supply_circulating. For some tokens, mint and issue(or redeem and burn)
        occurs simultaneously, and for others this does not. For further 
        information, please refer to the section 'Stablecoin Issuing Mechanism'.
        
        https://cryptoquant.com/docs#tag/Stablecoin-Network-Data

        Parameters
        ----------
        **query_params : TYPE
            token (str, required): A stablecoin from the table that CQ support.
            window (str, optional): day and block.
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
            Supply stablecoins statistics.

        """
        return super().handle_request(self.SC_NETWORK_SUPPLY, query_params)
    
    def get_stable_ntx_events_count(self, **query_params):
        """
        This endpoint returns metrics related to the number of events. CQ
        provide several metrics. events_mint_count, events_issue_count, 
        events_burn_count and events_redeem_count are metrics that represent 
        the number of events related to each actions (mint, issue, burn, 
        redeem). For further information about the actions, please refer to the
        section Stablecoin Issuing Mechanism.

        Parameters
        ----------
        **query_params : TYPE
            token (str, required): A stablecoin from the table that CQ support.
            window (str, optional): day and block.
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
            Transfer, mint, issue, burn and redeem.

        """
        return super().handle_request(self.SC_NETWORK_EVENTS_COUNT, query_params)
    
    def get_stable_trx_tokens_transferred(self, **query_params):
        """
        This endpoint returns metrics related to the number of tokens 
        transferred, i.e transaction volume. We provide several metrics, 
        tokens_transferred_total, the total number of transferred tokens, and
        tokens_transferred_mean, the mean tokens transferred per transaction.

        Parameters
        ----------
        **query_params : TYPE
            token (str, required): A stablecoin from the table that CQ support.
            window (str, optional): day and block.
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
            Total tokens transferred and mean.

        """
        return super().handle_request(self.SC_NETWORK_TOKENS_TRANSFERRED, query_params)
    
    def get_stable_trx_addrs_count(self, **query_params):
        """
        This endpoint returns metrics relating to the number of used addresses
        to transfer the token. CQ provide several metrics, 
        addresses_active_count, the total number of unique addresses that were 
        active (either sender or receiver) on the blockchain in a given window,
        addresses_active_sender_count, the number of addresses that were active
        as a sender, addresses_active_receiver_count, the number of addresses 
        that were active as a receiver.

        Parameters
        ----------
        **query_params : TYPE
            token (str, required): A stablecoin from the table that CQ support.
            window (str, optional): day and block.
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
            Statistics for counting addresses.

        """
        return super().handle_request(self.SC_NETWORK_ADDRESSES_COUNT, query_params)