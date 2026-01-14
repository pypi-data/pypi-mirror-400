# -*- coding: utf-8 -*-
"""
Created on Wed Oct 22 11:53:22 2025

@author: lauta
"""

from cryptoquant.request_handler_class import RequestHandler

class TRX(RequestHandler):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        
        # Market data
        self.TRX_MARKET_OHLCV = "trx/market-data/price-ohlcv"
        self.TRX_MARKET_CAPITALIZATION = "trx/market-data/capitalization"
        # Network data
        self.TRX_NETWORK_SUPPLY = "trx/network-data/supply"
        self.TRX_NETWORK_TRANSACTIONS_COUNT = "trx/network-data/transactions-count"
        self.TRX_NETWORK_ADDRESSES_COUNT = "trx/network-data/addresses-count"
        self.TRX_NETWORK_TOKENS_TRANSFERRED = "trx/network-data/tokens-transferred"
        self.TRX_NETWORK_BLOCK_COUNT = "trx/network-data/block-count"
        self.TRX_NETWORK_FEES = "trx/network-data/fees"
        self.TRX_NETWORK_TPS = "trx/network-data/tps"
        self.TRX_NETWORK_TOTAL_VALUE_STAKED = "trx/network-data/total-value-staked"
        self.TRX_NETWORK_ENERGY_STAKE = "trx/network-data/energy-stake"
        # DEFI
        self.TRX_DEFI_SUNPUMP_TOKENS = "trx/defi/sunpump-tokens"
        self.TRX_DEFI_SUNSWAP_ACTIVITY = "trx/defi/sunswap-activity"
        
    # -----------------------------
    # Market Data
    # -----------------------------
    
    def get_trx_mkt_ohlcv(self, **query_params):
        """
        This endpoint returns metrics related to TRX's Price, Price OHLCV data 
        consists of five metrics.
        
        full documentation: https://cryptoquant.com/docs#tag/TRX-Market-Data/operation/getPriceOHLCV

        Parameters
        ----------
        **query_params : TYPE
            market (str, optional): A market type from the tbale that CQ
                                    support.
            exchange (str, optional): An exchange supported by CryptoQuant.
            symbol (str, optional): A XRP pair symbol from the table that CQ
                                    support.
            window (str, optional): day.
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
                                   Supported formats are json, csv.

        Returns
        -------
        dict
            Price OHLCV data for trx.

        """
        return super().handle_request(self.TRX_MARKET_OHLCV, query_params)
    
    def get_trx_mkt_capitalization(self, **query_params):
        """
        CQ provide market_cap, which is total market capitalization of TRX, 
        calculated by multiplying the total supply with its USD price.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day.
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
                                   Supported formats are json, csv.

        Returns
        -------
        dict
            Market cap in usd.

        """
        return super().handle_request(self.TRX_MARKET_CAPITALIZATION, query_params)
    
    # -----------------------------
    # Network Data
    # -----------------------------
    
    def get_trx_ntx_supply(self, **query_params):
        """
        This endpoint returns the metrics related to the supply of TRX.

        Metric	            Description
        supply_total	    The total amount of tokens in existence.
        supply_circulating	The amount of tokens that are circulating in the market.
        supply_minted	    The amount of tokens minted in the given window.
        supply_burned	    The amount of tokens burned in the given window.
        supply_staked	    The amount of tokens staked in Tron Super Representative members.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day.
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
                                   Supported formats are json, csv.

        Returns
        -------
        dict
            Supply statistics.

        """
        return super().handle_request(self.TRX_NETWORK_SUPPLY, query_params)
    
    def get_trx_ntx_trx_count(self, **query_params):
        """
        This endpoint returns metrics related to the number of transactions.

        Metric	                    Description
        transactions_count_total	The total number of transactions.
        transactions_count_mean	    The mean number of transactions.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day.
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
                                   Supported formats are json, csv.

        Returns
        -------
        dict
            Transaction statistics.

        """
        return super().handle_request(self.TRX_NETWORK_TRANSACTIONS_COUNT, query_params)
    
    def get_trx_ntx_addrs_count(self, **query_params):
        """
        This endpoint returns metrics relating to the number of used TRX 
        addresses.
        
        full doc: https://cryptoquant.com/docs#tag/TRX-Network-Data/operation/getAddressesCount

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day.
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
                                   Supported formats are json, csv.

        Returns
        -------
        dict
            addresses statistics.

        """
        return super().handle_request(self.TRX_NETWORK_ADDRESSES_COUNT, query_params)
    
    def get_trx_ntx_tokens_transferred(self, **query_params):
        """
        This endpoint returns metrics related to the number of tokens 
        transferred.
        
        full doc: https://cryptoquant.com/docs#tag/TRX-Network-Data/operation/getTokensTransferred

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day.
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
                                   Supported formats are json, csv.

        Returns
        -------
        dict
            tokens transferred statistics.

        """
        return super().handle_request(self.TRX_NETWORK_TOKENS_TRANSFERRED)
    
    def get_trx_ntx_block_count(self, **query_params):
        """
        The number of blocks generated in a given window.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day.
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
                                   Supported formats are json, csv.

        Returns
        -------
        dict
            blocks generated.

        """
        return super().handle_request(self.TRX_NETWORK_BLOCK_COUNT, query_params)
    
    def get_trx_ntx_fees(self, **query_params):
        """
        This endpoint returns the statistics related to fees paid from 
        executing transactions.
        
        Metric	            Description
        fees_total	        The sum of all fees paid from executing transactions.
        fees_total_usd	    The sum of all fees paid from executing transactions, calculated in USD.
        fees_block_mean	    The average fee per block.
        fees_block_mean_usd	The average fee per block, calculated in USD.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day.
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
                                   Supported formats are json, csv.

        Returns
        -------
        dict
            Fees.

        """
        return super().handle_request(self.TRX_NETWORK_FEES, query_params)
    
    def get_trx_ntx_tps(self, **query_params):
        """
        This endpoint returns the statistics related to the number of 
        transactions per second.

        Metric	Description
        tps	    The number of transactions per second.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day.
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
                                   Supported formats are json, csv.

        Returns
        -------
        dict
            Transactions per second.

        """
        return super().handle_request(self.TRX_NETWORK_TPS, query_params)
    
    def get_trx_ntx_total_value_staked(self, **query_params):
        """
        This endpoint returns the total amount of TRX staked by staking model.
        (Stake 1.0, Stake 2.0) This metric reflects how much TRX has been 
        locked to secure the network and obtain resources or staking rewards.

        Metric	            Description
        v1_staking_amount	The amount of TRX staked under Stake 1.0. (The legacy staking model on TRON)
        v2_staking_amount	The amount of TRX staked under Stake 2.0. (The newer staking model on TRON)

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day.
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
                                   Supported formats are json, csv.

        Returns
        -------
        dict
            total value stacked.

        """
        return super().handle_request(self.TRX_NETWORK_TOTAL_VALUE_STAKED, query_params)
    
    def get_trx_ntx_enery_stake(self, **query_params):
        """
        This endpoint returns the statistics related to the amount of TRX 
        staked for Energy.

        Metric	            Description
        total_energy_weight	The total amount of TRX staked for Energy.
        energy_rate	        The percentage of TRX staked for Energy.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day.
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
                                   Supported formats are json, csv.

        Returns
        -------
        dict
            energy staked.

        """
        return super().handle_request(self.TRX_NETWORK_ENERGY_STAKE, query_params)
    
    # -----------------------------
    # DEFI Data
    # -----------------------------
    
    def get_trx_defi_sunpump_tokens(self, **query_paramas):
        """
        This endpoint returns metrics related to SunPump token creation on TRON.

        Metric	                        Description
        token_create_event_count	    The total number of tokens that have been created on the SunPump platform.
        cumulative_count_create_events	The cumulative number of token creation events on SunPump over time.

        Parameters
        ----------
        **query_paramas : TYPE
            window (str, optional): day.
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
                                   Supported formats are json, csv.

        Returns
        -------
        dict
            SunPump token creation in Tron.

        """
        return super().handle_request(self.TRX_DEFI_SUNPUMP_TOKENS, query_paramas)
    
    def get_trx_defi_sunswap_activity(self, **query_paramas):
        """
        This endpoint returns metrics related to Sunswap activity on TRON.

        Metric	                Description
        total_transaction_count	The total number of transactions on Sunswap.
        wtrx_transaction_count	The number of transactions involving WTRX in the given window.
        other_transaction_count	The number of transactions involving other tokens in the given window.
        wtrx_dominance	        The dominance of WTRX in the total transaction volume in the given window.
        wtrx_amount	            The total amount of WTRX traded in the given window.
        wtrx_amount_usd	        The total amount of WTRX traded in USD in the given window.

        Parameters
        ----------
        **query_paramas : TYPE
            window (str, optional): day.
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
                                   Supported formats are json, csv.

        Returns
        -------
        dict
            SunSwap activity.

        """
        return super().handle_request(self.TRX_DEFI_SUNSWAP_ACTIVITY, query_paramas)