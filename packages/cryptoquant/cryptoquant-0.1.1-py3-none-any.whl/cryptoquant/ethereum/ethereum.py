# -*- coding: utf-8 -*-
"""
Created on Tue Oct 14 10:30:02 2025

@author: lauta
"""

from cryptoquant.request_handler_class import RequestHandler

class Ethereum(RequestHandler):
    def __init__(self, api_key: str):
        
        #Entity List
        self.ETH_ENTITY_STATUS = "eth/status/entity-list"
        # ETH Exchange Flows
        self.ETH_EXCH_FLOWS_RESERVE = "eth/exchange-flows/reserve"
        self.ETH_EXCH_FLOWS_NETFLOW = "eth/exchange-flows/netflow"
        self.ETH_EXCH_FLOWS_INFLOW = "eth/exchange-flows/inflow"
        self.ETH_EXCH_FLOWS_OUTFLOW = "eth/exchange-flows/outflow"
        self.ETH_EXCH_FLOWS_TRANSACTIONS_COUNT = "eth/exchange-flows/transactions-count"
        self.ETH_EXCH_FLOWS_ADDRESES_COUNT = "eth/exchange-flows/addresses-count"
        # Exchange Supply Ratio
        self.ETH_FLOW_IDX_EXCHNAGE_SUPPLY_RATIO = "eth/flow-indicator/exchange-supply-ratio"
        # ETH Market Indicator
        self.ETH_MARKET_IDX_ESTIMATED_LEVERAGE_RATIO = "eth/market-indicator/estimated-leverage-ratio"
        # ETH 2.0
        self.ETH_ETH_2_TOTAL_VALUE_STAKED = "eth/eth2/total-value-staked"
        self.ETH_ETH_2_STAKING_INFLOW_TOTAL = "eth/eth2/staking-inflow-total"
        self.ETH_ETH_2_STAKING_TRX_COUNT = "eth/eth2/staking-transaction-count"
        self.ETH_ETH_2_STAKING_VALIDATOR_TOTAL = "eth/eth2/staking-validator-total"
        self.ETH_ETH_2_DEPOSITOR_COUNT_TOTAL = "eth/eth2/depositor-count-total"
        self.ETH_ETH_2_DEPOSITOR_COUNT_NEW = "eth/eth2/depositor-count-new"
        self.ETH_ETH_2_STAKING_RATE = "eth/eth2/staking-rate"
        self.ETH_ETH_2_PHASE_0_SUCCESS_RATE = "eth/eth2/phase0-success-rate"
        # ETH Fund Data
        self.ETH_FUND_MARKET_PRICE = "eth/fund-data/market-price-usd"
        self.ETH_FUND_MARKET_VOLUME = "eth/fund-data/market-volume"
        self.ETH_FUND_MARKET_PREMIUM = "eth/fund-data/market-premium"
        self.ETH_FUND_MARKET_DIGITAL_HOLDINGS = "eth/fund-data/digital-asset-holdings"
        # Market Data
        self.ETH_MARKET_PRICE_OHLCV = "eth/market-data/price-ohlcv"
        self.ETH_MARKET_OPEN_INTEREST = "eth/market-data/open-interest"
        self.ETH_MARKET_FUNDING_RATES = "eth/market-data/funding-rates"
        self.ETH_MARKET_TAKER_BUY_SELL_STATS = "eth/market-data/taker-buy-sell-stats"
        self.ETH_MARKET_LIQUIDATIONS = "eth/market-data/liquidations"
        self.ETH_MARKET_COINBASE_PREMIUM_INDEX = "eth/market-data/coinbase-premium-index"
        self.ETH_MARKET_CAPITALIZATION = "eth/market-data/capitalization"
        # ETH Network Data
        self.ETH_NETWORK_SUPPLY = "eth/network-data/supply"
        self.ETH_NETWORK_VELOCITY = "eth/network-data/velocity"
        self.ETH_NETWORK_CONTRACTS_COUNT = "eth/network-data/contracts-count"
        self.ETH_NETWORK_TRANSACTIONS_COUNT = "eth/network-data/transactions-count"
        self.ETH_NETWORK_TRANSACTIONS_COUNT_BETWEEN_EOA = "eth/network-data/transactions-count-between-eoa"
        self.ETH_NETWORK_CONTRACT_CALLS_EXTERNAL = "eth/network-data/contract-calls-count-external"
        self.ETH_NETWORK_CONTRACT_CALLS_INTERNAL = "eth/network-data/contract-calls-count-internal"
        self.ETH_NETWORK_CONTRACT_CALLS_COUNT = "eth/network-data/contract-calls-count"
        self.ETH_NETWORK_TRANSACTIONS_COUNT_ALL = "eth/network-data/transactions-count-all"
        self.ETH_NETWORK_ADDRESSES_COUNT = "eth/network-data/addresses-count"
        self.ETH_NETWORK_ADDRESSES_COUNT_ALL = "eth/network-data/addresses-count-all"
        self.ETH_NETWORK_TOKENS_TRANSFERRED_COUNT = "eth/network-data/tokens-transferred-count"
        self.ETH_NETWORK_TOKENS_TRANSFERRED_COUNT_BETWEEN_EOA = "eth/network-data/tokens-transferred-count-between-eoa"
        self.ETH_NETWORK_TOKENS_TRANSFERRED_COUNT_BY_CONTRACT_CALLS_EXTERNAL = "eth/network-data/tokens-transferred-count-by-contract-calls-external"
        self.ETH_NETWORK_TOKENS_TRANSFERRED_COUNT_BY_CONTRACT_CALLS_INTERNAL = "eth/network-data/tokens-transferred-count-by-contract-calls-internal"
        self.ETH_NETWORK_TOKENS_TRANSFERRED_COUNT_BY_CONTRACT_CALLS = "eth/network-data/tokens-transferred-count-by-contract-calls"
        self.ETH_NETWORK_TOKENS_TRANSFERRED_COUNT_ALL = "eth/network-data/tokens-transferred-count-all"
        self.ETH_NETWORK_TOKENS_TRANSFERRED = "eth/network-data/tokens-transferred"
        self.ETH_NETWORK_TOKENS_TRANSFERRED_BETWEEN_EOA = "eth/network-data/tokens-transferred-between-eoa"
        self.ETH_NETWORK_TOKENS_TRANSFERRED_BY_CONTRACT_CALLS_EXTERNAL = "eth/network-data/tokens-transferred-by-contract-calls-external"
        self.ETH_NETWORK_TOKENS_TRANSFERRED_BY_CONTRACT_CALLS_INTERNAL = "eth/network-data/tokens-transferred-by-contract-calls-internal"
        self.ETH_NETWORK_TOKENS_TRANSFERRED_BY_CONTRACT_CALLS = "eth/network-data/tokens-transferred-by-contract-calls"
        self.ETH_NETWORK_TOKENS_TRANSFERRED_ALL = "eth/network-data/tokens-transferred-all"
        self.ETH_NETWORK_FAILED_TRANSACTIONS_COUNT = "eth/network-data/failed-transactions-count"      
        self.ETH_NETWORK_FAILED_TOKENS_TRANSFERRED_COUNT = "eth/network-data/failed-tokens-transferred-count"
        self.ETH_NETWORK_BLOCK_BYTES = "eth/network-data/block-bytes"
        self.ETH_NETWORK_BLOCK_COUNT = "eth/network-data/block-count"
        self.ETH_NETWORK_BLOCK_INTERVAL = "eth/network-data/block-interval"
        self.ETH_NETWORK_FEES = "eth/network-data/fees"
        self.ETH_NETWORK_FEES_BURNT = "eth/network-data/fees-burnt"
        self.ETH_NETWORK_FEES_TIPS = "eth/network-data/fees-tips"
        self.ETH_NETWORK_FEES_TRANSACTION = "eth/network-data/fees-transaction"
        self.ETH_NETWORK_FEES_TRANSACTION_BURNT = "eth/network-data/fees-burnt-transaction"
        self.ETH_NETWORK_FEES_TRANSACTION_TIPS = "eth/network-data/fees-tips-transaction"
        self.ETH_NETWORK_BLOCKREWARD = "eth/network-data/blockreward"
        self.ETH_NETWORK_BLOCKREWARD_EXCEPT_UNCLE = "eth/network-data/blockreward-except-uncle"
        self.ETH_NETWORK_GAS = "eth/network-data/gas"
        self.ETH_NETWORK_BASE_FEE = "eth/network-data/base-fee"
        self.ETH_NETWORK_MAX_FEE = "eth/network-data/max-fee"
        self.ETH_NETWORK_MAX_PRIOTITY_FEE = "eth/network-data/max-priority-fee"
        self.ETH_NETWORK_DIFFICULTY = "eth/network-data/difficulty"
        self.ETH_NETWORK_HASHRATE = "eth/network-data/hashrate"
        self.ETH_NETWORK_UNCLE_BLOCK_COUNT = "eth/network-data/uncle-block-count"
        self.ETH_NETWORK_UNCLE_BLOCKREWARD = "eth/network-data/uncle-blockreward"
        
        super().__init__(api_key)
        
    # -------------------------------
    # Entity list
    # -------------------------------
    
    def get_eth_entity_list(self, **query_params):
        """
        This endpoint returns entity list to serve data. The meaning of the 
        market_type value of the exchange object is as follows. For exchange 
        objects, the market_type field tells whether the exchange is a spot 
        exchange or a derivative exchange. Entities without a market type, 
        such as miners or banks, will return 0 for market_type.

        Exchange Market Type	Description
                            0	Undefined
                            1	Spot Exchange
                            2	Derivative Exchange

        Parameters
        ----------
        **query_params :
            type_ (str, required): A type from the entity in exchange.
            format_ (str:optional): A format type about return message type. 
                            Supported formats are json, csv. Default is json

        Returns
        -------
        dict
            Entity list on a given type.

        """
        return super().handle_request(self.ETH_ENTITY_STATUS, query_params)
    
    # -------------------------------
    # ETH Exchange Flows
    # -------------------------------
    
    def get_eth_exch_reserve(self, **query_params):
        """
        Returns the full historical on-chain balance of Ethereum exchanges.

        Parameters
        ----------
        **query_params : TYPE
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
            The amount of eth on a given exchange on this window.

        """
        return super().handle_request(self.ETH_EXCH_FLOWS_RESERVE, query_params)
    
    def get_eth_exch_netflow(self, **query_params):
        """
        The difference between coins flowing into exchanges and flowing out of
        exchanges. Netflow usually helps us to figure out an increase of idle
        coins waiting to be traded in a certain time frame.

        Parameters
        ----------
        **query_params : TYPE
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
            total netflow.

        """
        return super().handle_request(self.ETH_EXCH_FLOWS_NETFLOW, query_params)
    
    def get_eth_exch_inflow(self, **query_params):
        """
        This endpoint returns the inflow of ETH into exchange wallets for as 
        far back as CQ track. The average inflow is the average transaction 
        value for transactions flowing into exchange wallets on a given day.

        Parameters
        ----------
        **query_params : TYPE
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
            inflow statistics.

        """
        return super().handle_request(self.ETH_EXCH_FLOWS_INFLOW, query_params)
    
    def get_eth_exch_outflow(self, **query_params):
        """
        This endpoint returns the outflow of ETH into exchange wallets for as
        far back as CQ track. The average outflow is the average transaction 
        value for transactions flowing into exchange wallets on a given day.

        Parameters
        ----------
        **query_params : TYPE
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
            Outflow statistics.

        """
        return super().handle_request(self.ETH_EXCH_FLOWS_OUTFLOW, query_params)
    
    def get_eth_exch_trx_count(self, **query_params):
        """
        This endpoint returns the number of transactions flowing in/out of 
        Ethereum exchanges.

        Parameters
        ----------
        **query_params : TYPE
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
            Transactions count of inflows and outflows of ethereum exchnages.

        """
        return super().handle_request(self.ETH_EXCH_FLOWS_TRANSACTIONS_COUNT, query_params)
    
    def get_eth_exch_addrs_count(self, **query_params):
        """
        This endpoint returns the number of addresses involved in 
        inflow/outflow transactions.

        Parameters
        ----------
        **query_params : TYPE
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
        return super().handle_request(self.ETH_EXCH_FLOWS_ADDRESES_COUNT, query_params)
    
    # -------------------------------
    # Exchange Supply Ratio
    # -------------------------------
    
    def get_eth_flow_exch_supply_ratio(self, **query_params):
        """
        Exchange Supply Ratio is calculated as exchange reserve divided by 
        total supply. The metric measures how much tokens are reserved in the 
        exchange relative to total supply of the token.

        Parameters
        ----------
        **query_params : TYPE
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
        return super().handle_request(self.ETH_FLOW_IDX_EXCHNAGE_SUPPLY_RATIO, query_params)
    
    # -------------------------------
    # ETH Market Indicator
    # -------------------------------
    
    def get_eth_mkt_estimated_leverage_ratio(self, **query_params):
        """
        By dividing the open interest of an exchange by their ETH reserve, you 
        can estimate a relative average user leverage. Whenever the leverage 
        value reaches a high, there is rapid volatility. Similar to Open 
        Interest, but more accurate because it reflects the growth of the 
        exchange itself. This is experimental indicator but it seems this 
        reflects market sentiment. You can see how aggressive people are and
        how conservative they are in terms of investment. For 'In Progress'
        exchanges, estimated leverage ratio is not supported yet even though 
        they provide open interest.

        Parameters
        ----------
        **query_params : TYPE
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
            The amount of open interest of exchnge divided by their 
            ETH reserve.

        """
        return super().handle_request(self.ETH_MARKET_IDX_ESTIMATED_LEVERAGE_RATIO, query_params)
    
    # -------------------------------
    # ETH 2.0
    # -------------------------------
    
    def get_eth_20_total_value_staked(self, **query_params):
        """
        This endpoint returns the valid ETH balance of the deposit contract.

        Parameters
        ----------
        **query_params : TYPE
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
            The valid amount of ETH in the deposit contract on this window.

        """
        return super().handle_request(self.ETH_ETH_2_TOTAL_VALUE_STAKED, query_params)
    
    def get_eth_20_total_inflow_staking(self, **query_params):
        """
        This endpoint returns the valid ETH inflow into the deposit contract.

        Parameters
        ----------
        **query_params : TYPE
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
            The valid amount of ETH in the deposit contract on this window.

        """
        return super().handle_request(self.ETH_ETH_2_STAKING_INFLOW_TOTAL, query_params)
    
    def get_eth_20_staking_trx_count(self, **query_params):
        """
        This endpoint returns the number of valid transactions to the deposit
        contract.

        Parameters
        ----------
        **query_params : TYPE
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
            The valid amount of ETH in the deposit contract on this window.

        """
        return super().handle_request(self.ETH_ETH_2_STAKING_TRX_COUNT, query_params)
    
    def get_eth_20_staking_validator_total(self, **query_params):
        """
        This endpoint returns the number of total validators.

        Parameters
        ----------
        **query_params : TYPE
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
            The number of the number of total validators on this window.

        """
        return super().handle_request(self.ETH_ETH_2_STAKING_VALIDATOR_TOTAL, query_params)
    
    def get_eth_20_depositor_count_total(self, **query_params):
        """
        This endpoint returns the number of unique accounts who deposited over 
        32 ETH to the deposit contract.

        Parameters
        ----------
        **query_params : TYPE
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
            The number of unique accounts who deposited iver 32 ETH on this 
            window.

        """
        return super().handle_request(self.ETH_ETH_2_DEPOSITOR_COUNT_TOTAL, query_params)
    
    def get_eth_20_depositor_count_new(self, **query_params):
        """
        This endpoint returns the number of new unique accounts who deposited 
        over 32 ETH to the deposit contract.

        Parameters
        ----------
        **query_params : TYPE
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
            This endpoint returns the number of new unique accounts who
            deposited over 32 ETH to the deposit contract.

        """
        return super().handle_request(self.ETH_ETH_2_DEPOSITOR_COUNT_NEW, query_params)
    
    def get_eth_20_staking_rate(self, **query_params):
        """
        This endpoint returns the percentage of the balance of the ETH 2.0 
        deposit contract to the total supply.

        Parameters
        ----------
        **query_params : TYPE
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
            The percentage of valid balance of the deposit contract to the
            total supply on this window.

        """
        return super().handle_request(self.ETH_ETH_2_STAKING_RATE, query_params)
    
    def get_eth_20_phase_0_success_rate(self, **query_params):
        """
        This endpoint returns the percentage of the valid ETH balance of the
        deposit contract to 524,288 ETH.

        Parameters
        ----------
        **query_params : TYPE
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
            The percentage of valid balance of the deposit contract to
            524,288 ETH on thi window.

        """
        return super().handle_request(self.ETH_ETH_2_PHASE_0_SUCCESS_RATE, query_params)
    
    # -------------------------------
    # ETH Fund Data
    # -------------------------------
    
    def get_eth_fund_market_price(self, **query_params):
        """
        The price of certain symbol (e.g. ethe) managed by each fund (e.g. 
        Grayscale) reflects sentiment of investors in regulated markets. In
        this specific case, having single share of ETHE means having 
        approximately 0.01 ETH invested to Grayscale. This endpoint returns
        metrics related to the US Dollar(USD) price of fund related stocks 
        (e.g. ethe). CQ provide five metrics, price_usd_open, USD opening price
        at the beginning of the window, price_usd_close, USD closing price at 
        the end of the window, price_usd_high, the highest USD price in a given
        window, price_usd_low, the lowest USD price in a given window, and 
        price_usd_adj_close, USD adjusted closing price at the end of the
        window. All Symbol is not supported.
        
        full symbol list: https://cryptoquant.com/docs#tag/ETH-Fund-Data

        Parameters
        ----------
        **query_params : TYPE
            symbol (str, required): A stock symbol (ticker) from the table that
                                    CQ support
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
                                   Supported formats are json, csv

        Returns
        -------
        dict
            Market price OHLC and adjusted C data in USD.

        """
        return super().handle_request(self.ETH_FUND_MARKET_PRICE, query_params)
    
    def get_eth_fund_market_volumen(self, **query_params):
        """
        The volume of certain symbol (e.g. ethe) managed by each fund
        (e.g. Grayscale) reflects sentiment of investors in regulated markets. 
        This endpoint returns traded volume of fund related stocks (e.g. ethe).
        At this endpoint, metrics are calculated by Day. CQ provide one metric,
        volume, traded volume of the window.

        full symbol list: https://cryptoquant.com/docs#tag/ETH-Fund-Data

        Parameters
        ----------
        **query_params : TYPE
            symbol (str, required): A stock symbol (ticker) from the table that
                                    CQ support
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
                                   Supported formats are json, csv

        Returns
        -------
        dict
            Market volume data.

        """
        return super().handle_request(self.ETH_FUND_MARKET_VOLUME, query_params)
    
    def get_eth_fund_market_premium(self, **query_params):
        """
        The premium of certain symbol (e.g. ethe) is defined as (market price 
        of the symbol - NAV) divided by NAV where NAV (Native Asset Value) is 
        the current value of holdings (e.g. ETH price multiplied by ETH per 
        Share). Higher the premium indicates market bullish, which also
        indicates downside risk. On the other hand, lower the premium indicates 
        market bearish, which also indicates upside risk. All Symbol market 
        premium is calculated by taking VWAP (Volume Weighted Average Ratio) of
        each fund data volume (usd).

        full symbol list: https://cryptoquant.com/docs#tag/ETH-Fund-Data

        Parameters
        ----------
        **query_params : TYPE
            symbol (str, required): A stock symbol (ticker) from the table that
                                    CQ support
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
                                   Supported formats are json, csv

        Returns
        -------
        dict
            Market premium data.

        """
        return super().handle_request(self.ETH_FUND_MARKET_PREMIUM, query_params)
    
    def get_eth_fund_digital_asset_holdings(self, **query_params):
        """
        This endpoint returns digital asset holdings status of each fund. For 
        example, Grayscale ETH Holdings along with ETHE represents how much ETH
        Grayscale is holding for its investment. This metric indicates stock 
        market's sentiment where higher the value means bullish sentiment of 
        investors in stock market.

        full symbol list: https://cryptoquant.com/docs#tag/ETH-Fund-Data

        Parameters
        ----------
        **query_params : TYPE
            symbol (str, required): A stock symbol (ticker) from the table that
                                    CQ support
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
                                   Supported formats are json, csv
        Returns
        -------
        dict
            Digital asset holdings data.

        """
        return super().handle_request(self.ETH_FUND_MARKET_DIGITAL_HOLDINGS, query_params)
    
    # -------------------------------
    # ETH Market Data
    # -------------------------------
    
    def get_eth_mkt_ohlcv(self, **query_params):
        """
        This endpoint returns metrics related to ETH price. We provide two 
        types of price, CryptoQuant's ETH Index Price and USD or USDT price of 
        ETH of global exchanges. Price OHLCV data consists of five metrics.  
        open, the opening price at the beginning of the window, close, USD 
        closing price at the end of the window,  high, the highest USD price in
        a given window, low, the lowest USD price in a given window, and volume,
        the total volume traded in a given window.
        
        At this endpoint, metrics are calculated by Minute, Hour and Day. ETH 
        Index Price is calculated by taking VWAP(Volume Weighted Average Price)
        of ETH price data aggregated from all exchanges CQ provide.
        
        full documentation: https://cryptoquant.com/docs#tag/ETH-Market-Data/operation/getETHPriceOHLCV

        Parameters
        ----------
        **query_params : TYPE
            market (str, optinal): A market type from the table CQ support
            exchange (str, optional): A exchnage from the table CQ support
            symbol (str, required): A stock symbol (ticker) from the table that
                                    CQ support
            window (str, optional): day, hour and minute.
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
            Price OHLCV data.

        """
        return super().handle_request(self.ETH_MARKET_PRICE_OHLCV, query_params)
    
    def get_eth_mkt_open_interest(self, **query_params):
        """
        This endpoint returns ETH Perpetual Open Interest from derivative
        exchanges. Supported exchanges for Open Interest are below. Note CQ
        unify the unit of return value to USD for each exchange where its
        contract specification may vary.
        
        full documentation: https://cryptoquant.com/docs#tag/ETH-Market-Data/operation/ETHgetOpenInterest

        Parameters
        ----------
        **query_params : TYPE
            exchange (str, optional): A exchnage from the table CQ support
            symbol (str, required): A stock symbol (ticker) from the table that
                                    CQ support
            window (str, optional): day, hour and minute.
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
            Open interest in USD.

        """
        return super().handle_request(self.ETH_MARKET_OPEN_INTEREST, query_params)
    
    def get_eth_mkt_funding_rates(self, **query_params):
        """
        Funding rates represents traders' sentiments of which position they bet
        on in perpetual swaps market. Positive funding rates implies that many
        traders are bullish and long traders pay funding to short traders. 
        Negative funding rates implies many traders are bearish and short 
        traders pay funding to long traders.
        
        full documentation: https://cryptoquant.com/docs#tag/ETH-Market-Data/operation/ETHgetFundingRates

        Parameters
        ----------
        **query_params : TYPE
            exchange (str, optional): A exchnage from the table CQ support
            symbol (str, required): A stock symbol (ticker) from the table that
                                    CQ support
            window (str, optional): day, hour and minute.
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
            funding rates in percentage.

        """
        return super().handle_request(self.ETH_MARKET_FUNDING_RATES, query_params)
    
    def get_eth_mkt_taker_buy_sell_stats(self, **query_params):
        """
        Taker Buy/Sell Stats represent takers' sentiment of which position they
        are taking in the market. This metric is calculated with perpetual swap
        trades in each exchange. taker_buy_volume is volume that takers buy. 
        taker_sell_volume is volume that takers sell. taker_total_volume is the
        sum of taker_buy_volume and taker_sell_volume. taker_buy_ratio is the 
        ratio of taker_buy_volume divided by taker_total_volume. 
        taker_sell_ratio is the ratio of taker_sell_volume divided by 
        taker_total_volume. taker_buy_sell_ratio is the ratio of 
        taker_buy_volume divided by taker_sell_volume. Note CQ unify the unit 
        of return value to USD for each exchange where its contract 
        specification may vary.
        
        full documentation: https://cryptoquant.com/docs#tag/ETH-Market-Data/operation/ETHgetTakerBuySellStats

        Parameters
        ----------
        **query_params : TYPE
            exchange (str, optional): A exchnage from the table CQ support
            symbol (str, required): A stock symbol (ticker) from the table that
                                    CQ support
            window (str, optional): day, hour and minute.
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
            Taker buy, sell volume and ratio.

        """
        return super().handle_request(self.ETH_MARKET_TAKER_BUY_SELL_STATS, query_params)
    
    def get_eth_mkt_liquidations(self, **query_params):
        """
        Liquidations are sum of forced market orders to exit leveraged 
        positions caused by price volatility. Liquidations indicate current 
        price volatility and traders' sentiment which side they had been 
        betting. Note that Binance's liquidation data collection policy has 
        changed since 2021-04-27, which makes the distribution of the data has 
        changed after that.
        
        full documentatio: https://cryptoquant.com/docs#tag/ETH-Market-Data/operation/ETHgetLiquidations

        Parameters
        ----------
        **query_params : TYPE
            exchange (str, optional): A exchnage from the table CQ support
            symbol (str, required): A stock symbol (ticker) from the table that
                                    CQ support
            window (str, optional): day, hour and minute.
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
            Amount of long/short liquidations orders.

        """
        return super().handle_request(self.ETH_MARKET_LIQUIDATIONS, query_params)
    
    def get_eth_mkt_coinbase_premium_index(self, **query_params):
        """
        Coinbase Premium Index is calculated as percent difference from Binance
        price(ETHUSDT) to Coinbase price(ETHUSD). Coinbase Premium Gap is 
        calculated as gap between Coinbase price(ETHUSD) and Binance 
        price(ETHUSDT). The higher the premium, the stronger the spot buying 
        pressure from Coinbase.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour and minute.
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
            Coinbase premium index in percentage and coinbase premium gap.

        """
        return super().handle_request(self.ETH_MARKET_COINBASE_PREMIUM_INDEX, query_params)
    
    def get_eth_mkt_capitalization(self, **query_params):
        """
        This endpoint returns metrics related to market capitalization. CQ
        provide market_cap, which is total market capitalization of ETH, 
        calculated by multiplying the circulating supply with its USD price.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour and minute.
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
            Market capitalization of Ethereum calculated by total supply
            times price usd close.

        """
        return super().handle_request(self.ETH_MARKET_CAPITALIZATION, query_params)
    
    # -------------------------------
    # ETH Network Data
    # -------------------------------
    
    def get_eth_ntx_supply(self, **query_params):
        """
        This endpoint returns metrics related to Ethereum supply, i.e. the 
        amount of Ethereum in existence. CQ currently provide two metrics, 
        supply_total, the total amount of Ethereum in existence (sum of all 
       Ethereum issued by the block rewards), and supply_new, the amount of 
        newly issued tokens in a given window.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            Total and new supply.

        """
        return super().handle_request(self.ETH_NETWORK_SUPPLY, query_params)
    
    def get_eth_ntx_velocity(self, **query_params):
        """
        This endpoint returns metrics related to the velocity of Ethereum. 
        Ethereum's velocity is calculated by dividing the trailing 1 year 
        estimated transaction volume(the cumulated sum of transferred tokens) 
        by current supply. Velocity is a metric that explains how actively is 
        money circulating in the market.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            Ethereum transaction volume in the trailing 1 year divided by
            current total supply.

        """
        return super().handle_request(self.ETH_NETWORK_VELOCITY, query_params)
    
    def get_eth_ntx_contracts_count(self, **query_params):
        """
        This endpoint returns metrics related to the number of contracts. CQ
        provide contracts_created_new representing the number of contracts 
        created, contracts_destroyed_new representing the number of contracts 
        destroyed, and contracts_count_total representing the unique number of
        contracts.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            new, destrpyed and total contracts on the ethereum netwok.

        """
        return super().handle_request(self.ETH_NETWORK_CONTRACTS_COUNT, query_params)
    
    def get_eth_ntx_trx_count(self, **query_params):
        """
        This endpoint returns metrics related to the number of transactions. CQ
        provide several metrics, transactions_count_total, the total number of 
        transactions, transactions_count_mean, the mean number of transactions.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            Transactions count total and mean.

        """
        return super().handle_request(self.ETH_NETWORK_TRANSACTIONS_COUNT, query_params)
    
    def get_eth_ntx_trx_eoa(self, **query_params):
        """
        This endpoint returns metrics related to the number of transactions 
        between externally owned accounts (EOAs).

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            Transactions count total and mean.

        """
        return super().handle_request(self.ETH_NETWORK_TRANSACTIONS_COUNT_BETWEEN_EOA, query_params)
    
    def get_eth_ntx_trx_contract_calls_external(self, **query_params):
        """
        This endpoint returns metrics related to the number of external 
        contract calls.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            Contract call count total and mean.

        """
        return super().handle_request(self.ETH_NETWORK_CONTRACT_CALLS_EXTERNAL, query_params)
    
    def get_eth_ntx_trx_contract_calls_internal(self, **query_params):
        """
        This endpoint returns metrics related to the number of internal 
        contract calls.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            Contract call count total and mean.

        """
        return super().handle_request(self.ETH_NETWORK_CONTRACT_CALLS_INTERNAL, query_params)
    
    def get_eth_ntx_trx_contract_calls_count(self, **query_params):
        """
        This endpoint returns metrics related to the number of contract calls 
        including both internal and external calls.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            Contract call count total and mean.

        """
        return super().handle_request(self.ETH_NETWORK_CONTRACT_CALLS_COUNT, query_params)
    
    def get_eth_ntx_trx_count_all(self, **query_params):
        """
        This endpoint returns metrics related to the number of transactions 
        including internal contract calls.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            Trasactions count total and mean.

        """
        return super().handle_request(self.ETH_NETWORK_TRANSACTIONS_COUNT_ALL, query_params)
    
    def get_eth_ntx_addr_count(self, **query_params):
        """
        This endpoint returns metrics relating to the number of used Ethereum 
        addresses. CQ provide several metrics, addresses_count_active, the 
        total number of unique addresses that were active (either sender or 
        receiver) on the blockchain in a given window, addresses_count_sender, 
        the number of addresses that were active as a sender, and 
        addresses_count_receiver, the number of addresses that were active as a
        receiver.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            addresses count active, sender and receiver.

        """
        return super().handle_request(self.ETH_NETWORK_ADDRESSES_COUNT, query_params)
    
    def get_eth_ntx_addr_count_all(self, **query_params):
        return super().handle_request(self.ETH_NETWORK_ADDRESSES_COUNT_ALL, query_params)
    
    def get_eth_ntx_tokens_transferred_count(self, **query_params):
        """
        This endpoint returns metrics related to the number of tokens
        transferred executed. CQ provide several metrics, 
        tokens_transferred_count_total, the total number of executed tokens 
        transferred, and tokens_transferred_count_mean, the mean number of 
        executed tokens transferred.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            Tokens transferred count and mean.

        """
        return super().handle_request(self.ETH_NETWORK_TOKENS_TRANSFERRED_COUNT, query_params)
    
    def get_eth_ntx_tokens_transferred_count_eoa(self, **query_params):
        """
        This endpoint returns metrics related to the number of tokens 
        transferred executed between externally owned accounts (EOAs).

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            Tokens transferred count and mean.

        """
        return super().handle_request(self.ETH_NETWORK_TOKENS_TRANSFERRED_COUNT_BETWEEN_EOA, query_params)
    
    def get_eth_ntx_tokens_transferred_count_calls_external(self, **query_params):
        """
        This endpoint returns metrics related to the number of tokens 
        transferred executed by external contract calls.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            Tokens transferred count and mean.

        """
        return super().handle_request(self.ETH_NETWORK_TOKENS_TRANSFERRED_COUNT_BY_CONTRACT_CALLS_EXTERNAL, query_params)
    
    def get_eth_ntx_tokens_transferred_count_calls_internal(self, **query_params):
        """
        This endpoint returns metrics related to the number of tokens 
        transferred executed by internal contract calls.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            Tokens transferred count and mean.

        """
        return super().handle_request(self.ETH_NETWORK_TOKENS_TRANSFERRED_COUNT_BY_CONTRACT_CALLS_INTERNAL, query_params)
    
    def get_eth_ntx_tokens_transferred_count_calls(self, **query_params):
        """
        This endpoint returns metrics related to the number of tokens 
        transferred executed by contract calls including both internal and 
        external calls.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            Tokens transferred count and mean.

        """
        return super().handle_request(self.ETH_NETWORK_TOKENS_TRANSFERRED_COUNT_BY_CONTRACT_CALLS, query_params)
    
    def get_eth_ntx_tokens_transferred_count_all(self, **query_params):
        """
        This endpoint returns metrics related to the number of tokens
        transferred executed including internal contract calls.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            Tokens transferred count and mean.

        """
        return super().handle_request(self.ETH_NETWORK_TOKENS_TRANSFERRED_COUNT_ALL, query_params)
    
    def get_eth_ntx_tokens_transferred(self, **query_params):
        """
        This endpoint returns metrics related to the number of tokens 
        transferred, i.e transaction volume. We provide several metrics, 
        tokens_transferred_total, the total number of transferred tokens in 
        that window, tokens_transferred_mean, the mean of transferred tokens 
        per transaction in that window, and tokens_transferred_median, the 
        median of tokens transferred per transaction. We also provide this 
        value in USD units.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            metrics related to the number of tokens transferred.

        """
        return super().handle_request(self.ETH_NETWORK_TOKENS_TRANSFERRED, query_params)
    
    def get_eth_ntx_tokens_transferred_eoa(self, **query_params):
        """
        This endpoint returns metrics related to the number of tokens 
        transferred, i.e transaction volume. Note these metrics include 
        transactions with tokens transferred between externally owned accounts 
        (EOAs).

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            metrics related to the number of tokens transferred, between 
            externally owned accounts .

        """
        return super().handle_request(self.ETH_NETWORK_TOKENS_TRANSFERRED_BETWEEN_EOA, query_params)
    
    def get_eth_ntx_tokens_transferred_calls_external(self, **query_params):
        """
        This endpoint returns metrics related to the number of tokens 
        transferred by external contract calls, i.e transaction volume.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            metrics related to the number of tokens transferred calls.

        """
        return super().handle_request(self.ETH_NETWORK_TOKENS_TRANSFERRED_BY_CONTRACT_CALLS_EXTERNAL, query_params)
    
    def get_eth_ntx_tokens_transferred_calls_internal(self, **query_params):
        """
        This endpoint returns metrics related to the number of tokens 
        transferred by internal contract calls, i.e transaction volume.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            metrics related to the number of tokens transferred calls.

        """
        return super().handle_request(self.ETH_NETWORK_TOKENS_TRANSFERRED_BY_CONTRACT_CALLS_INTERNAL, query_params)
    
    def get_eth_ntx_tokens_transferred_calls(self, **query_params):
        """
        This endpoint returns metrics related to the number of tokens 
        transferred by contract calls including both internal and external 
        calls, i.e transaction volume.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            metrics related to the number of tokens transferred calls.

        """
        return super().handle_request(self.ETH_NETWORK_TOKENS_TRANSFERRED_BY_CONTRACT_CALLS, query_params)
    
    def get_eth_ntx_tokens_transferred_all(self, **query_params):
        """
        This endpoint returns metrics related to the number of tokens 
        transferred, i.e transaction volume. Note these metrics include 
        internal contract calls.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            metrics related to the number of tokens transferred calls.

        """
        return super().handle_request(self.ETH_NETWORK_TOKENS_TRANSFERRED_ALL, query_params)
    
    def get_eth_ntx_failed_trx_count(self, **query_params):
        """
        This endpoint returns metrics related to the number of failed 
        transactions. We provide failed_transactions_count_total metric, the
        total number of failed transactions.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            The number of failed transactions count.

        """
        return super().handle_request(self.ETH_NETWORK_FAILED_TRANSACTIONS_COUNT, query_params)
    
    def get_eth_ntx_failed_tokens_transferred_count(self, **query_params):
        """
        This endpoint returns metrics related to the number of failed 
        transactions with tokens transferred. We provide 
        failed_tokens_transferred_count_total metric, the total number of 
        failed transactions with tokens transferred.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            The number of failed transactions count.

        """
        return super().handle_request(self.ETH_NETWORK_FAILED_TOKENS_TRANSFERRED_COUNT, query_params)
    
    def get_eth_ntx_block_bytes(self, **query_params):
        """
        The mean size(in bytes) of all blocks generated.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            The mean size (in bytes) of all blocks generated.

        """
        return super().handle_request(self.ETH_NETWORK_BLOCK_BYTES, query_params)
    
    def get_eth_ntx_block_count(self, **query_params):
        """
        The number of blocks generated in a given window.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            The number of blocks generated in a given window.

        """
        return super().handle_request(self.ETH_NETWORK_BLOCK_COUNT, query_params)
    
    def get_eth_ntx_block_interval(self, **query_params):
        """
        The average time between blocks generated displayed in seconds.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            The average time between blocks generated in seconds.

        """
        return super().handle_request(self.ETH_NETWORK_BLOCK_INTERVAL, query_params)
    
    def get_eth_ntx_fees(self, **query_params):
        """
        This endpoint returns the statistics related to fees paid from 
        executing transactions. CQ provide the following statistics, 
        fees_total, the sum of all fees, fees_block_mean, the average fee per 
        block, and fees_reward_percent, the percentage of fees relative to the 
        total block reward. CQ provide the metrics in both ETH and USD units.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            statistics related to fees paid from executing transactions.

        """
        return super().handle_request(self.ETH_NETWORK_FEES, query_params)
    
    def get_eth_ntx_fees_burnt(self, **query_params):
        """
        This endpoint returns the statistics related to fees burnt in Ethereum 
        chain by executing transactions, introduced after London upgrade. CQ
        provide the total amount of burnt fees as fees_burnt_total in ETH and 
        fees_burnt_total_usd in USD units. These metrics have data entries 
        starting post to London upgrade (block height 12965000, datetime 
        2021-08-05 12:33:42).

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            total burn fees in eth and usd.

        """
        return super().handle_request(self.ETH_NETWORK_FEES_BURNT, query_params)
    
    def get_eth_ntx_fees_tips(self, **query_params):
        """
        This endpoint returns the statistics related to fees directly paid to 
        Ethereum miners, introduced after London upgrade. CQ provide the total
        amount of fees as tips as fees_tips_total in ETH and 
        fees_tips_total_usd in USD units. These metrics have data entries 
        starting post to London upgrade (block height 12965000, datetime 
        2021-08-05 12:33:42).

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            tips in eth and usd.

        """
        return super().handle_request(self.ETH_NETWORK_FEES_TIPS, query_params)
    
    def get_eth_ntx_fees_trx(self, **query_params):
        """
        This endpoint returns the statistics related to fees per transaction 
        that are paid from executing transactions. We provide the following 
        statistics, fees_transaction_mean, the average fee per transaction, 
        fees_transaction_median, the median fee per transaction. CQ provide 
        the metrics in both ETH and USD units.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            transactions fees in eth and usd.

        """
        return super().handle_request(self.ETH_NETWORK_FEES_TRANSACTION, query_params)
    
    def get_eth_ntx_fees_trx_burnt(self, **query_params):
        """
        This endpoint returns the statistics related to fees per transaction 
        burnt in Ethereum chain by executing transactions, introduced after 
        London upgrade. We provide the average amount of burnt fees per 
        transaction as fees_burnt_transaction_mean and the median amount as 
        fees_burnt_transaction_median. CQ provide the metrics in both ETH and 
        USD units. These metrics have data entries starting post to London 
        upgrade (block height 12965000, datetime 2021-08-05 12:33:42).

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            statistics related to fees per transaction burnt in Ethereum chain 
            by executing transactions.

        """
        return super().handle_request(self.ETH_NETWORK_FEES_TRANSACTION_BURNT, query_params)
    
    def get_eth_ntx_fees_trx_tips(self, **query_params):
        """
        This endpoint returns the statistics related to fees per transaction 
        directly paid to Ethereum miners, introduced after London upgrade. CQ
        provide the average amount of fees tips per transaction as 
        fees_tips_transaction_mean and the median amount as 
        fees_tips_transaction_median. We provide the metrics in both ETH and 
        USD units. These metrics have data entries starting post to London 
        upgrade (block height 12965000, datetime 2021-08-05 12:33:42).

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            statistics related to fees per transaction directly paid to 
            Ethereum miners.

        """
        return super().handle_request(self.ETH_NETWORK_FEES_TRANSACTION_TIPS, query_params)
    
    def get_eth_ntx_blockreward(self, **query_params):
        """
        The sum of block rewards (including mining or staking rewards and 
        transaction fees). CQ also provide this value in USD units.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            The sum of block rewards (including or stacking rewards and
            transaction fees), CQ also provide this value in USD units.

        """
        return super().handle_request(self.ETH_NETWORK_BLOCKREWARD, query_params)
    
    def get_eth_ntx_blockreward_except_uncle(self, **query_params):
        """
        The sum of block rewards except uncle blocks. CQ also provide this 
        value in USD units.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            The sum of block rewards except uncle blocks, CQ also provide this
            value in USD units.

        """
        return super().handle_request(self.ETH_NETWORK_BLOCKREWARD_EXCEPT_UNCLE, query_params)
    
    def get_eth_ntx_gas(self, **query_params):
        """
        This endpoint returns the statistics related to gas used in all 
        transactions. We provide the total amount of gas used as 
        gas_used_total, the average amount of gas used as gas_used_mean, the 
        average gas price as gas_price_mean in Gwei per gas, and the average 
        gas limit as gas_limit_mean.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            statistics related to gas used in all transactions.

        """
        return super().handle_request(self.ETH_NETWORK_GAS, query_params)
    
    def get_eth_ntx_base_fee(self, **query_params):
        """
        Base Fee represents the base fee per gas used to burn the fees in 
        Ethereum chain, introduced after London upgrade. base_fee_mean is the 
        average value of the base fee per gas over the blocks in Gwei.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            The average value of the base fee pern gas over the blocks is Gwei.

        """
        return super().handle_request(self.ETH_NETWORK_BASE_FEE, query_params)
    
    def get_eth_ntx_max_fee(self, **query_params):
        """
        Max Fee represents the fee per gas that the user can maximally admit 
        when submitting the transaction, introduced after London upgrade. 
        max_fee_mean is the average value of the max fee per gas over the 
        transactions in Gwei.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            The average value of the max fee per gas over the transactions in 
            Gwei.

        """
        return super().handle_request(self.ETH_NETWORK_MAX_FEE, query_params)
    
    def get_eth_ntx_max_priority_fee(self, **query_params):
        """
        Max Priority Fee represents the fee per gas used to provide tips (fees)
        to the miner, introduced after London upgrade. max_priority_fee_mean is
        the average value of the max priority fee per gas over the transactions
        in Gwei.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            The average valu of the max priority fee per gas over the
            transactions in Gwei.

        """
        return super().handle_request(self.ETH_NETWORK_MAX_PRIOTITY_FEE, query_params)
    
    def get_eth_ntx_difficulty(self, **query_params):
        """
        The mean difficulty of mining a new block.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            The mean difficulty of mining a new block..

        """
        return super().handle_request(self.ETH_NETWORK_DIFFICULTY, query_params)
    
    def get_eth_ntx_hashrate(self, **query_params):
        """
        The mean speed at which miners in the network are solving hash 
        problems. It is displayed as hashes (GigaBytes) per second.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            The mean speed at which problems are being solved across all miners
            in the network. It is displayed as hashes (gigabytes) per second.

        """
        return super().handle_request(self.ETH_NETWORK_HASHRATE, query_params)
    
    def get_eth_ntx_uncle_block_count(self, **query_params):
        """
        The number of uncle blocks generated in a given window.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            The number of uncle blocks generated in a given window.

        """
        return super().handle_request(self.ETH_NETWORK_UNCLE_BLOCK_COUNT, query_params)
    
    def get_eth_ntx_uncle_blockreward(self, **query_params):
        """
        The sum of uncle block rewards (including mining or staking rewards and
        transaction fees). We also provide this value in USD units.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): day, hour, 10minute, and block.
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
            The sum of uncle block rewards (including mining or stacking rewards
            and transaction fees). CQ also provide this value in USD units.

        """
        return super().handle_request(self.ETH_NETWORK_UNCLE_BLOCKREWARD, query_params)