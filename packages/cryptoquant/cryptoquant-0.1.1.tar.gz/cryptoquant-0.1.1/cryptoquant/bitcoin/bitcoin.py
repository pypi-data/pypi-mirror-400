# -*- coding: utf-8 -*-
"""
Created on Wed Oct  8 14:19:40 2025

@author: lauta
"""

from cryptoquant.request_handler_class import RequestHandler

class Bitcoin(RequestHandler):
    def __init__(self, api_key: str):
        
        # URLS for exchanges
        self.BTC_EXCH_ENTITY_URL = "btc/status/entity-list"
        self.BTC_EXCH_RESERVES = "btc/exchange-flows/reserve"
        self.BTC_EXCH_NETFLOW = "btc/exchange-flows/netflow"
        self.BTC_EXCH_INFLOW = "btc/exchange-flows/inflow"
        self.BTC_EXCH_OUTFLOW = "btc/exchange-flows/outflow"
        self.BTC_EXCH_TNX_COUNT = "btc/exchange-flows/transactions-count"
        self.BTC_EXCH_ADDRESSES_COUNT = "btc/exchange-flows/addresses-count"
        self.BTC_EXCH_INHOUSE_FLOW = "btc/exchange-flows/in-house-flow"
        # Bitcoin Flow Indicators
        self.BTC_IDX_MPI = "btc/flow-indicator/mpi"
        self.BTC_IDX_EXCHANGE_SHUTDOWN = "btc/flow-indicator/exchange-shutdown-index"
        self.BTC_IDX_EXCHANGE_WHALE_RATIO = "btc/flow-indicator/exchange-whale-ratio"
        self.BTC_IDX_FUND_FLOW_RAIO = "btc/flow-indicator/fund-flow-ratio"
        self.BTC_IDX_STABLECOINS_RATIO = "btc/flow-indicator/stablecoins-ratio"
        self.BTC_IDX_EXCHANGE_INFLOW_AGE_DSTR = "btc/flow-indicator/exchange-inflow-age-distribution"
        self.BTC_IDX_EXCHANGE_INFLOW_SUPPLY_DSTR = "btc/flow-indicator/exchange-inflow-supply-distribution"
        self.BTC_IDX_EXCHANGE_INFLOW_CDD = "btc/flow-indicator/exchange-inflow-cdd"
        self.BTC_IDX_EXCHANGE_SUPPLY_RATIO = "btc/flow-indicator/exchange-supply-ratio"
        self.BTC_IDX_MINER_SUPPLY_RATIO = "btc/flow-indicator/miner-supply-ratio"
        # Bitcoin market indicators
        self.BTC_MKT_ESTIMATED_LEVERAGE_RATIO = "btc/market-indicator/estimated-leverage-ratio"
        self.BTC_MKT_STABLECOIN_SUPPLY_RATIO = "btc/market-indicator/stablecoin-supply-ratio"
        self.BTC_MKT_MVRV = "btc/market-indicator/mvrv"
        self.BTC_MKT_SOPR = "btc/market-indicator/sopr"
        self.BTC_MKT_SOPR_RATIO = "btc/market-indicator/sopr-ratio"
        self.BTC_MKT_REALIZED_PRICE = "btc/market-indicator/realized-price"
        self.BTC_MKT_UTXO_REALIZED_PRICE_AGRE_DIST = "btc/market-indicator/utxo-realized-price-age-distribution"
        # Bitcoin network indicators
        self.BTC_NTW_STOCK_TO_FLOW = "btc/network-indicator/stock-to-flow"
        self.BTC_NTW_NVT = "btc/network-indicator/nvt"
        self.BTC_NTW_NVT_GOLDEN_CROSS = "btc/network-indicator/nvt-golden-cross"
        self.BTC_NTW_NVM = "btc/network-indicator/nvm"
        self.BTC_NTW_PUELL_MULTIPLE = "btc/network-indicator/puell-multiple"
        self.BTC_NTW_COIN_DAYS_DESTROYED = "btc/network-indicator/cdd"
        self.BTC_NTW_MEAN_COIN_AGE = "btc/network-indicator/mca"
        self.BTC_NTW_SUM_COIN_AGE = "btc/network-indicator/sca"
        self.BTC_NTW_SUM_COIN_AGE_DISTRIBUTION = "btc/network-indicator/sca-distribution"
        self.BTC_NTW_NET_UNREALIZED_PNL = "btc/network-indicator/nupl"
        self.BTC_NTW_NET_REALIZED_PNL = "btc/network-indicator/nrpl"
        self.BTC_NTW_PROFIT_AND_LOSS_UTXO = "btc/network-indicator/pnl-utxo"
        self.BTC_NTW_PROFIT_AND_LOSS_SUPPLY = "btc/network-indicator/pnl-supply"
        self.BTC_NTW_DORMANCY = "btc/network-indicator/dormancy"
        self.BTC_NTW_UTXO_AGE_DISTRIBUTION = "btc/network-indicator/utxo-age-distribution"
        self.BTC_NTW_UTXO_REALIZED_AGE_DISTR = "btc/network-indicator/utxo-realized-age-distribution"
        self.BTC_NTW_UTXO_COUNT_AGE_DSTR = "btc/network-indicator/utxo-count-age-distribution"
        self.BTC_NTW_SPENT_OUTPUT_AGE_DSTR = "btc/network-indicator/spent-output-age-distribution"
        self.BTC_NTW_UTXO_SUPPLY_DSTR = "btc/network-indicator/utxo-supply-distribution"
        self.BTC_NTW_UTXO_REALIZED_SUPPLY_DSTR = "btc/network-indicator/utxo-realized-supply-distribution"
        self.BTC_NTW_UTXO_COUNT_SUPPLY_DSTR = "btc/network-indicator/utxo-count-supply-distribution"
        self.BTC_NTW_SPENT_OUTPUT_SUPPLY_DSTR = "btc/network-indicator/spent-output-supply-distribution"
        # Bitcoin Miner Flows
        self.BTC_MINER_RESERVE = "btc/miner-flows/reserve"
        self.BTC_MINER_NETFLOW = "btc/miner-flows/netflow"
        self.BTC_MINER_INFLOW = "btc/miner-flows/inflow"
        self.BTC_MINER_OUTFLOW = "btc/miner-flows/outflow"
        self.BTC_MINER_TRANSACTIONS_COUNT = "btc/miner-flows/transactions-count"
        self.BTC_MINER_ADDRESSES_COUNT = "btc/miner-flows/addresses-count"
        self.BTC_MINER_IN_HOUSE_FLOW = "btc/miner-flows/in-house-flow"
        # Bitcoin Inter Entity Flows
        self.BTC_INTER_EXCHANGE_TO_EXCHANGE = "btc/inter-entity-flows/exchange-to-exchange"
        self.BTC_INTER_MINER_TO_EXCHANGE = "btc/inter-entity-flows/miner-to-exchange"
        self.BTC_INTER_EXCHANGE_TO_MINER = "btc/inter-entity-flows/exchange-to-miner"
        self.BTC_INTER_MINER_TO_MINER = "btc/inter-entity-flows/miner-to-miner"
        # Bitcoin fund data
        self.BTC_FUND_MARKET_PRICE_USD = "btc/fund-data/market-price-usd"
        self.BTC_FUND_MARKET_VOLUME = "btc/fund-data/market-volume"
        self.BTC_FUND_MARKET_PREMIUM = "btc/fund-data/market-premium"
        self.BTC_FUND_DIGITAL_ASSETS_HOLDINGS = "btc/fund-data/digital-asset-holdings"
        # Bitcoin market data
        self.BTC_LIQUIDITY_PRICE_OHLCV = "btc/market-data/price-ohlcv"
        self.BTC_LIQUIDITY_OPEN_INTEREST = "btc/market-data/open-interest"
        self.BTC_LIQUIDITY_FUNDING_RATES = "btc/market-data/funding-rates"
        self.BTC_LIQUIDITY_TAKER_BUY_SELL_STATS = "btc/market-data/taker-buy-sell-stats"
        self.BTC_LIQUIDITY_LIQUIDATIONS = "btc/market-data/liquidations"
        self.BTC_LIQUIDITY_CAPITALIZATION = "btc/market-data/capitalization"
        self.BTC_LIQUIDITY_COINBASE_PREMIUM_INDEX = "btc/market-data/coinbase-premium-index"
        # Bitcoin miner data
        self.BTC_BITCOIN_MINER_DATA = "btc/miner-data/companies"
        # Bitcoin Network Data
        self.BTC_NETWORK_SUPPLY = "btc/network-data/supply"
        self.BTC_NETWORK_VELOCITY = "btc/network-data/velocity"
        self.BTC_NETWORK_TRANSACTIONS_COUNT = "btc/network-data/transactions-count"
        self.BTC_NETWORK_ADDRESSES_COUNT = "btc/network-data/addresses-count"
        self.BTC_NETWORK_TOKENS_TRANSFERRED = "btc/network-data/tokens-transferred"
        self.BTC_NETWORK_BLOCK_BYTES = "btc/network-data/block-bytes"
        self.BTC_NETWORK_BLOCK_COUNT = "btc/network-data/block-count"
        self.BTC_NETWORK_BLOCK_INTERVAL = "btc/network-data/block-interval"
        self.BTC_NETWORK_UTXO_COUNT = "btc/network-data/utxo-count"
        self.BTC_NETWORK_FEES = "btc/network-data/fees"
        self.BTC_NETWORK_FEES_TRANSACTION = "btc/network-data/fees-transaction"
        self.BTC_NETWORK_BLOCKREWARD = "btc/network-data/blockreward"
        self.BTC_NETWORK_DIFFICULTY = "btc/network-data/difficulty"
        self.BTC_NETWORK_HASHRATE = "btc/network-data/hashrate"
        # BTC Mempool Statistics
        self.BTC_MEMPOOL_STATS_BY_RELATIVE_FEE = "btc/mempool/stats-by-relative-fee"
        self.BTC_MEMPOOL_STATS_IN_TOTAL = "btc/mempool/stats-in-total"
        # BTC Lightning Network Statistics
        self.BTC_LIGHTNING_NETWORK = "btc/lightning/stats-in-total"
        
        super().__init__(api_key)
    
    # -------------------------------------
    # Exchange endpoints
    # -------------------------------------
    
    def get_btc_exch_entity(self, **query_params):
        """
        This method returns entity list to serve data. The meaning of the 
        market_type value of the exchange object is as follows:
            For exchange objects, the market_type field tells whether the 
            exchange is a spot exchange or a derivative exchange. Entities 
            without a market type, such as miners, will 
            return 0 for market_type.
        
        Exchange Market Type	Description
                            0	Undefined
                            1	Spot Exchange
                            2	Derivative Exchange

        Parameters
        ----------
        **query_params :
            type_ (str, required): A type from the entity in exchange, bank, 
                                    miner.
            format_ (str:optional): A format type about return message type. 
                            Supported formats are json, csv. Default is json

        Returns
        -------
        dict
            Entity list on a given type.

        """
        return super().handle_request(self.BTC_EXCH_ENTITY_URL, query_params)
    
    def get_btc_exch_reserve(self, **query_params):
        """
        This endpoint returns the full historical on-chain balance 
        of Bitcoin exchanges.

        Parameters
        ----------
        **query_params :
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
            The amount of BTC on a given exchange on this window.

        """
        return super().handle_request(self.BTC_EXCH_RESERVES, query_params)
    
    def get_btc_exch_netflow(self, **query_params):
        """
        The difference between coins flowing into exchanges and flowing out of 
        exchanges. Netflow usually helps us to figure out an increase of idle 
        coins waiting to be traded in a certain time frame.

        Parameters
        ----------
        **query_params :
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
            total netfow.

        """
        return super().handle_request(self.BTC_EXCH_NETFLOW, query_params)
    
    def get_btc_exch_inflow(self, **query_params):
        """
        Inflow of BTC into exchange wallets for as far back as CQ track. 
        The average inflow is the average transaction value for transactions 
        flowing into exchange wallets on a given day.

        Parameters
        ----------
        **query_params :
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
            inflow total, top 10 inflow, mean inflow, and 7 day sma inflow.

        """
        return super().handle_request(self.BTC_EXCH_INFLOW, query_params)
    
    def get_btc_exch_outflow(self, **query_params):
        """
        Outflow of BTC into exchange wallets for as far back as CQ track. 
        The average outflow is the average transaction value for transactions 
        flowing into exchange wallets on a given day.

        Parameters
        ----------
        **query_params :
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
            outflow total, top 10 outflow, mean outflow, and 7 day sma outflow.

        """
        return super().handle_request(self.BTC_EXCH_OUTFLOW, query_params)
    
    def get_btc_exch_txn(self, **query_params):
        """
        This endpoint returns the number of transactions flowing in/out of 
        Bitcoin exchanges.

        Parameters
        ----------
        **query_params :
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
            Transactions count inflows and transactions count outflow

        """
        
        return super().handle_request(self.BTC_EXCH_TNX_COUNT, query_params)
    
    def get_btc_exch_addrs(self, **query_params):
        """
        Number of addresses involved in inflow/outflow transactions.

        Parameters
        ----------
        **query_params :
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
        return super().handle_request(self.BTC_EXCH_ADDRESSES_COUNT, query_params)
    
    def get_btc_exch_inhouseflow(self, **query_params):
        """
        This endpoint returns the in-house flow of BTC within wallets of the 
        same exchange for as far back as CQ track. The average in-house flow is
        the average transaction value for transactions flowing within wallets
        on a given day.

        Parameters
        ----------
        **query_params :
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
            Total flow, mean flow, count transactions flow

        """
        return super().handle_request(self.BTC_EXCH_INHOUSE_FLOW, query_params)
    
    # -------------------------------------
    # BTC Flow Indicator
    # -------------------------------------
    
    def get_btc_idx_mpi(self, **query_params):
        """
        MPI(Miners’ Position Index) is a z score of a specific period. The 
        period range must be 2 days or more and if not, it will return an error.
        mpi is an index to understand miners’ behavior by examining the total 
        outflow of miners. It highlights periods where the value of Bitcoin’s 
        outflow by miners on a daily basis has historically been extremely high 
        or low. MPI values above 2 indicate that most of the miners are selling 
        Bitcoin. MPI values under 0 indicate that there is less selling pressure 
        by miners.

        Parameters
        ----------
        **query_params :
            window (str, optional): Currently, we only support day.
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
            Miners position index

        """
        return super().handle_request(self.BTC_IDX_MPI, query_params)
    
    def get_btc_idx_exchshutdown(self, **query_params):
        """
        Stay Ahead of Exchange Hacks. See hacks as they happen by identifying 
        sudden increases and become zero in exchange outflows and hedge against
        potential risk.

        Parameters
        ----------
        **query_params :
            exchange (str, required): An exchange supported by CryptoQuant.
            window (str, optional): Currently, we only support day.
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
            Exchange Shutdown Index

        """
        return super().handle_request(self.BTC_IDX_EXCHANGE_SHUTDOWN, query_params)
    
    def get_btc_idx_whale(self, **query_params):
        """
        Find Whale Focused Exchanges with Top 10 Inflows. Looking at the relative
        size of the top 10 inflows to total inflows, it is possible to discover
        which exchanges whales use. For example, as Gemini has mostly whales 
        users, it is possible for the price to rise or fall dramatically. This
        has potential risks, but also the possibility of arbitrage.

        Parameters
        ----------
        **query_params :
            exchange (str, required): An exchange supported by CryptoQuant.
            window (str, optional): Currently, we only support day.
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
            The total BTC amount of top 10 inflow amount divided by the total BTC
            amount flowed into exchange.

        """
        return super().handle_request(self.BTC_IDX_EXCHANGE_WHALE_RATIO, query_params)
    
    def get_btc_idx_fundflow(self, **query_params):
        """
        Fund Flow Ratio provides the amount of bitcoins that exchanges occupy 
        among the bitcoins sent underlying the Bitcoin network. Knowing the 
        amount of fund currently involved in trading can help you understand 
        market volatility.

        Parameters
        ----------
        **query_params : TYPE
            exchange (str, required): An exchange supported by CryptoQuant.
            window (str, optional): Currently, we only support day.
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
            The total BTC inflow and outflow of exchange divided by the total
            BTC transferred on the Bitcoin network.

        """
        return super().handle_request(self.BTC_IDX_FUND_FLOW_RAIO, query_params)
    
    def get_btc_idx_stableratio(self, **query_params):
        """
        BTC reserve divided by all stablecoins reserve held by an exchange. 
        This usually indicates potential sell pressure. Supported exchanges are
        determined by the concurrent validity of both BTC and Stablecoins 
        (for at least 1 token).

        Parameters
        ----------
        **query_params : TYPE
            exchange (str, required): An exchange supported by CryptoQuant.
            window (str, optional): Currently, we only support day.
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
            Total BTC reserve divided by all stablecoins reserve held by an
            exchange.

        """
        return super().handle_request(self.BTC_IDX_STABLECOINS_RATIO, query_params)
    
    def get_btc_idx_agedistr(self, **query_params):
        """
        Exchange Inflow Age Distribution is a set of active inflow to exchanges
        with age bands. This indicator summarizes the behaviors of long-term or 
        short-term holders flowed into the exchanges. CQ provide the distribution
        values in native and percent values.

        Parameters
        ----------
        **query_params : TYPE
            exchange (str, required): An exchange supported by CryptoQuant.
            window (str, optional): Currently, we only support day.
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
            Exchange inflow age distribution.

        """
        return super().handle_request(self.BTC_IDX_EXCHANGE_INFLOW_AGE_DSTR, query_params)
    
    def get_btc_idx_supplydstr(self, **query_params):
        """
        Exchange Inflow Supply Distribution is a set of active inflow to 
        exchanges with balance (supply) bands. This indicator summarizes the 
        behaviors of whales or retails flowed into the exchanges, separated by 
        amount of coins they hold along with price actions. We provide the 
        distribution values in native and percent values.

        Parameters
        ----------
        **query_params : TYPE
            exchange (str, required): An exchange supported by CryptoQuant.
            window (str, optional): Currently, we only support day.
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
            Exchange inflow supply distribution.

        """
        return super().handle_request(self.BTC_IDX_EXCHANGE_INFLOW_SUPPLY_DSTR, query_params)
    
    def get_btc_idx_cdd(self, **query_params):
        """
        Exchange Inflow CDD is a subset of Coin Days Destroyed (CDD) where 
        coins are destroyed by flowing into exchanges. This indicator is 
        noise-removed version of CDD with respect to exchange dumping signal.

        Parameters
        ----------
        **query_params : TYPE
            exchange (str, required): An exchange supported by CryptoQuant.
            window (str, optional): Currently, we only support day.
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
            Exchange inflow cdd.

        """
        return super().handle_request(self.BTC_IDX_EXCHANGE_INFLOW_CDD, query_params)
    
    def get_btc_idx_exchsupplyratio(self, **query_params):
        """
        Exchange Supply Ratio is calculated as exchange reserve divided by 
        total supply. The metric measures how much tokens are reserved in the 
        exchange relative to total supply of the token.

        Parameters
        ----------
        **query_params : TYPE
            exchange (str, required): An exchange supported by CryptoQuant.
            window (str, optional): Currently, we only support day.
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
        return super().handle_request(self.BTC_IDX_EXCHANGE_SUPPLY_RATIO, query_params)
    
    def get_btc_idx_minersupplyratio(self, **query_params):
        """
        Miner Supply Ratio is calculated as miner reserve divided by total 
        supply. The metric measures how much tokens are reserved in the miner 
        relative to total supply of the token.

        Parameters
        ----------
        **query_params : TYPE
            exchange (str, required): An exchange supported by CryptoQuant.
            window (str, optional): Currently, we only support day.
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
            Ratio of reserved token in the miner relative to total supply.

        """
        return super().handle_request(self.BTC_IDX_MINER_SUPPLY_RATIO, query_params)
    
    # -------------------------------------
    # BTC Market Indicator
    # -------------------------------------
    
    def get_btc_mkt_leverage(self, **query_params):
        """
        By dividing the open interest of an exchange by their BTC reserve, you
        can estimate a relative average user leverage. Whenever the leverage 
        value reaches a high, there is rapid volatility. Similar to Open Interest,
        but more accurate because it reflects the growth of the exchange itself.
        This is experimental indicator but it seems this reflects market sentiment.
        You can see how aggressive people are and how conservative they are in
        terms of investment. For 'In Progress' exchanges, estimated leverage 
        ratio is not supported yet even though they provide open interest.
        
        Note: This endpoint does not support Point-In-Time (PIT) accuracy due
        to periodic updates to wallet address clustering. Historical data may
        change as new exchange wallets are discovered, added, and validated.

        Parameters
        ----------
        **query_params : TYPE
            exchange (str, required): An exchange supported by CryptoQuant.
            window (str, optional): Currently, we only support day.
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
            The amount of open interest of exchange divided by their BTC reserve

        """
        return super().handle_request(self.BTC_MKT_ESTIMATED_LEVERAGE_RATIO, query_params)
    
    def get_btc_mkt_ssr(self, **query_params):
        """
        SSR(Stablecoin Supply Ratio) is a ratio of stablecoin supply in the 
        whole cryptocurrency market where stablecoin is used as fiat substitute
        for trading. This means that the supply of stablecoin can be used to 
        assess the potential buying pressure for bitcoin. The historical 
        starting point is 2017-11-28 00:00:00.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently, we only support day.
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
            Stablecoin supply ratio.

        """
        return super().handle_request(self.BTC_MKT_STABLECOIN_SUPPLY_RATIO, query_params)
    
    def get_btc_mkt_mvrv(self, **query_params):
        """
        MVRV(Market-Value-to-Realized-Value) is a ratio of market_cap divided
        by realized_cap. It can be interpreted as the relationship between 
        short-term and long-term investors (i.e. speculators vs hodlers). 
        When this value is too high, BTC price may be overvalued, and if it is
        too low, there is a possibility that the price is undervalued.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently, we only support day.
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
            Market-Value-to-Realized-Value

        """
        return super().handle_request(self.BTC_MKT_MVRV, query_params)
    
    def get_btc_mkt_sopr(self, **query_params):
        """
        sopr is abbreviation of Spent Output Profit Ratio. Spent Output Profit Ratio
        evaluates the profit ratio of the whole market participants by comparing
        the value of outputs at spent time to created time. sopr is a ratio 
        that is calculated as the USD value of spent outputs at the spent time
        divided by the USD value of spent outputs at the created time. So you 
        can see the value when UTxO destroyed. In a simple way, you can estimate
        the distribution of spent transaction output are in profit or not.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently, we only support day.
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
            Spent Output Profit Ratio

        """
        return super().handle_request(self.BTC_MKT_SOPR, query_params)
    
    def get_btc_mkt_soprratio(self, **query_params):
        """
        SOPR Ratio is calculated as long term holders' SOPR divided by short 
        term holders' SOPR. Higher value of the ratio means higher spent 
        profit of LTH over STH, which is usually useful for spotting market tops.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently, we only support day.
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
            Long term holders SOPR divided by short term holders SOPR

        """
        return super().handle_request(self.BTC_MKT_SOPR_RATIO, query_params)
    
    def get_btc_mkt_realizedprice(self, **query_params):
        """
        Realized Price is calculated as Realized Cap divided by the total coin 
        supply. It measures the average price weighted by the supply of what 
        the entire market participants paid for their coins. It sometimes can
        be interpreted as the on-chain support or resistance price.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently, we only support day.
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
            Realized cap divided by total supply.

        """
        return super().handle_request(self.BTC_MKT_REALIZED_PRICE, query_params)
    
    def get_btc_mkt_utxo(self, **query_params):
        """
        UTxO Realized Price Age Distribution is a set of realized prices along 
        with age bands. The metrics help us to overview each cohort’s holding
        behavior by overlaying a set of different realized prices.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently, we only support day.
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
            UTxO Realized Price Age Distribution.

        """
        return super().handle_request(self.BTC_MKT_UTXO_REALIZED_PRICE_AGRE_DIST, query_params)
    
    # -------------------------------------
    # BTC Network Indicator
    # -------------------------------------
    
    def get_btc_ntw_stock2flow(self, **query_params):
        """
        Stock to Flow is a metric used to assume bitcoin price based on its 
        scarcity just like gold, silver, and other valuable objects that are 
        limited in amount and costly to earn. The same model for evaluating the
        value of those objects can be adopted to assess the value of bitcoin. 
        The scarcity is calculated by dividing currently circulating coins in 
        the blockchain network to newly supplied coins.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently, we only support day.
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
            Stock to flow and stock to flow reversion.

        """
        return super().handle_request(self.BTC_NTW_STOCK_TO_FLOW, query_params)
    
    def get_btc_ntw_nvt(self, **query_params):
        """
        NVT(Network Value to Transaction) ratio is the network value(supply_total * price_usd)
        divided by tokens_transferred_total. nvt is a metric often used to 
        determine whether Bitcoin price is overvalued or not. The theory behind 
        this indicator is that the value of the token depends on how actively
        transactions take place on the network.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently, we only support day.
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
            Network Value to Transaction ratio.

        """
        return super().handle_request(self.BTC_NTW_NVT, query_params)
    
    def get_btc_ntw_nvtgoldencross(self, **query_params):
        """
        NVT Golden Cross is a modified index of NVT that provides local tops 
        and bottoms. NVT Golden Cross values above 2.2 indicate that downside
        risk goes up. NVT Golden Cross values below -1.6 mean huge upside 
        potential will occur.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently, we only support day.
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
            NVT golden cross.

        """
        return super().handle_request(self.BTC_NTW_NVT_GOLDEN_CROSS, query_params)
    
    def get_btc_ntw_nvm(self, **query_params):
        """
        NVM(Network Value to Metcalfe Ratio) is a metric based on Metcalfe’s law;
        the value of a network is proportional to the square of its nodes or user. 
        NVM is a ratio of market cap divided by daily active address. Based on 
        Metcalfe’s law, the value of bitcoin rises if the daily active addresses
        increase. Therefore, if the NVM value is relatively small, it means that 
        the value of the network is underestimated and if the value is relatively
        high, it means that the value of the network is overestimated.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently, we only support day.
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
            Network Value to Metcalfe Ratio.

        """
        return super().handle_request(self.BTC_NTW_NVM, query_params)
    
    def get_btc_ntw_puell(self, **query_params):
        """
        Puell Multiple is the mining revenue usd divided by MA 365 mining 
        revenue usd. puell_multiple is a metric shows the historically low and 
        high periods of the value of bitcoin issued daily, and at what point 
        investors should buy bitcoin to get high returns. This indicator was 
        created by David Puell.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently, we only support day.
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
            Puell Multiple.

        """
        return super().handle_request(self.BTC_NTW_PUELL_MULTIPLE, query_params)
    
    def get_btc_ntw_cdd(self, **query_params):
        """
        Coin Days Destroyed reflects market participants who have been in the
        bitcoin on-chain for longer. This indicator gives more weight to 
        long-term-holder position. cdd is the sum of products of spent 
        transaction output alive days and its value. sa_cdd is abbreviation of 
        supply-adjusted cdd. Since cdd increases as the newly created block
        mined, we need an indicator which normalize cdd value. sa_cdd is
        calculated by cdd over supply_total. average_sa_cdd is the average
        value of sa_cdd since genesis block. binary_cdd is the signal whether
        current sa_cdd is larger than average_sa_cdd or not. If 
        sa_cdd > average_sa_cdd, then binary_cdd is 1. In conclusion, 
        these indicators help us to estimate how whale's moving.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently, we only support day.
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
            cdd.

        """
        return super().handle_request(self.BTC_NTW_COIN_DAYS_DESTROYED, query_params)
    
    def get_btc_ntw_mca(self, **query_params):
        """
        Mean Coin Age is the mean value of products of bitcoin unspent 
        transaction output alive days and its value. It is basically similar to
        cdd. But mca focuses on unspent transaction output. Mean Coin Dollar 
        Age is the sum value of products of bitcoin unspent transaction output 
        alive days, value, and price at the created time.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently, we only support day.
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
            mca.

        """
        return super().handle_request(self.BTC_NTW_MEAN_COIN_AGE, query_params)
    
    def get_btc_ntw_sca(self, **query_params):
        """
        Sum Coin Age is the sum value of products of bitcoin unspent
        transaction output alive days and its value. It is basically similar to 
        cdd. But sca focuses on unspent transaction output. Sum Coin Dollar Age
        is the sum value of products of bitcoin unspent transaction output 
        alive days, value, and price at the created time.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently, we only support day.
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
            Sum Coin age.

        """
        return super().handle_request(self.BTC_NTW_SUM_COIN_AGE, query_params)
    
    def get_btc_ntw_scad(self, **query_params):
        """
        This indicator shows the distribution of long-term holder and
        short-term holder with UTxO data. It is similar to UTxO distribution,
        but weighted by alive days to highlight long-term holder's distribution
        in different ranges. Each field is calculated as the sum of the 
        products of bitcoin unspent transaction output alive days and its 
        value in a given period, divided by their sum. If long-term SCA 
        distribution ratio increases, then we can interpret this as one of 
        bullish moment.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently, we only support day.
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
            Sum Coin Age Distribution.

        """
        return super().handle_request(self.BTC_NTW_SUM_COIN_AGE_DISTRIBUTION, query_params)
    
    def get_btc_ntw_nupl(self, **query_params):
        """
        Net Unrealized Profit and Loss shows how different between market_cap 
        and realized_cap. nupl is calculated as difference between market_cap 
        and realized_cap divided by market_cap. If market_cap > realized_cap, 
        then nupl > 0, which means bitcoin on-chain expected value is less than
        what they actually have. So this value will give selling pressure. nup 
        is net unrealized profit, which is calculated as sum of products of 
        UTxO's value and price difference between created and destroyed, 
        divided by market_cap. nup only contains UTxOs in profit. nul is net
        unrealized loss. This is opposite indicator of nup. It only contains
        UTxOs in loss.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently, we only support day.
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
            Net unrealized profit and loss.

        """
        return super().handle_request(self.BTC_NTW_NET_UNREALIZED_PNL, query_params)
    
    def get_btc_ntw_nrpl(self, **query_params):
        """
        Net Realized Profit/Loss metric presenting the net magnitude of profit,
        or loss realized by all holders spending coins. Realized Profit/Loss is 
        assessed relative to the price when a coin last moved.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently, we only support day.
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
            Net realized profit and loss.

        """
        return super().handle_request(self.BTC_NTW_NET_REALIZED_PNL, query_params)
    
    def get_btc_ntw_pnlutxo(self, **query_params):
        """
        Profit and Loss (UTxO) evaluates the number of UTxOs being in profit or 
        not by comparing the price between created and destroyed. When the 
        price at destroyed time is higher than created, this transaction is in
        profit.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently, we only support day.
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
            Profit and Loss UTxO.

        """
        return super().handle_request(self.BTC_NTW_PROFIT_AND_LOSS_UTXO, query_params)
    
    def get_btc_ntw_pnlsupply(self, **query_params):
        """
        Profit and Loss (Supply) evaluates the sum of UTxOs being in profit or 
        not by comparing the price between created and destroyed. These metrics
        are similar to the ones in Profit and Loss (UTxO) but differ from 
        putting more weight on each UTxO with its value. Sometimes we want to 
        know the exact alive bitcoin transaction output value in profit. 
        pnl-supply will show it accuretely. pnl-supply is calculated as the sum
        of UTxO value.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently, we only support day.
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
            Profit and Loss (Supply).

        """
        return super().handle_request(self.BTC_NTW_PROFIT_AND_LOSS_SUPPLY, query_params)
    
    def get_btc_ntw_dormancy(self, **query_params):
        """
        Average Dormancy (average_dormancy) is the average number of days 
        destroyed per coin transacted. Supply-Adjusted Average Dormancy 
        (sa_average_dormancy) is the average dormancy normalized by supply 
        total, where supply total increases as more blocks mined.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently, we only support day.
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
            Te average number of days destroyed per coin transacted.

        """
        return super().handle_request(self.BTC_NTW_DORMANCY, query_params)
    
    def get_btc_ntw_utxo_age_distr(self, **query_params):
        """
        UTxO Age Distribution is a set of active supply with age bands. This 
        indicator summarizes the behaviors of long-term or short-term holders
        along with price actions. We provide the distribution values in native,
        USD, and percent values.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently, we only support day.
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
            UTxO Age Distribution.

        """
        return super().handle_request(self.BTC_NTW_UTXO_AGE_DISTRIBUTION, query_params)
    
    def get_btc_ntw_utxo_realized_age_dstr(self, **query_params):
        """
        UTxO Realized Age Distribution is a set of active supply with age bands
        weighted by the price at UTxO created time. Similar to Realized Cap, 
        this indicator summarizes the capitalization held by long-term or 
        short-term holders (each band). We provide the distribution values in 
        native, USD, and percent values.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently, we only support day.
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
            UTxO Realized Age Distribution.

        """
        return super().handle_request(self.BTC_NTW_UTXO_REALIZED_AGE_DISTR, query_params)
    
    def get_btc_ntw_utxo_count_age_dstr(self, **query_params):
        """
        UTxO Count Age Distribution is a set of active number of holders with 
        age bands. This indicator summarizes how many long-term or short-term
        holders exist by each band. We provide the distribution values in 
        native, and percent values.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently, we only support day.
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
            UTxO Count Age Distribution.

        """
        return super().handle_request(self.BTC_NTW_UTXO_COUNT_AGE_DSTR, query_params)
    
    def get_btc_ntw_spent_output_age_dstr(self, **query_params):
        """
        Spent Output Age Distribution is a set of active sum of spent outputs
        with age bands. This indicator summarizes how much UTxOs are destroyed
        by long-term or short-term holders (each band). We provide the 
        distribution values in native, USD, and percent values.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently, we only support day.
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
            Spent Output Age Distribution.

        """
        return super().handle_request(self.BTC_NTW_SPENT_OUTPUT_AGE_DSTR, query_params)
    
    def get_btc_ntw_utxo_supply_dstr(self, **query_params):
        """
        UTxO Supply Distribution is a set of active supply with balance 
        (supply) bands. This indicator summarizes the behaviors of whales or
        retails separated by amount of coins they hold along with price 
        actions. We provide the distribution values in native, and percent
        values.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently, we only support day.
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
            UTxO Supply Distribution.

        """
        return super().handle_request(self.BTC_NTW_UTXO_SUPPLY_DSTR, query_params)
    
    def get_btc_ntw_utxo_realized_supply_dstr(self, **query_params):
        """
        UTxO Realized Supply Distribution is a set of active supply with 
        balance (supply) bands weighted by the price at UTxO created time. 
        Similar to Realized Cap, this indicator summarizes the capitalization 
        held by whales or retails (each band). We provide the distribution 
        values in USD, and percent values.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently, we only support day.
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
            UTxO Realized Supply Distribution.

        """
        return super().handle_request(self.BTC_NTW_UTXO_REALIZED_SUPPLY_DSTR, query_params)
    
    def get_btc_ntw_utxo_count_supply_dstr(self, **query_params):
        """
        UTxO Count Supply Distribution is a set of active number of holders
        with balance (supply) bands. This indicator summarizes how many whales 
        and retails exist by each band. We provide the distribution values in
        native, and percent values.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently, we only support day.
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
            UTxO Count Supply Distribution.

        """
        return super().handle_request(self.BTC_NTW_UTXO_COUNT_SUPPLY_DSTR, query_params)
    
    def get_btc_ntw_spent_output_supply_dstr(self, **query_params):
        """
        Spent Output Supply Distribution is a set of active sum of spent 
        outputs with balance (supply) bands. This indicator summarizes how much
        UTxOs are destroyed by whales or retails (each band). We provide the 
        distribution values in native, USD, and percent values.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently, we only support day.
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
            Spent Output Supply Distribution.

        """
        return super().handle_request(self.BTC_NTW_SPENT_OUTPUT_SUPPLY_DSTR, query_params)
    
    # -------------------------------------
    # BTC Miner Flows
    # -------------------------------------
    
    def get_btc_miner_reserve(self, **query_params):
        """
        This endpoint returns the full historical on-chain balance of Bitcoin 
        mining pools.

        Parameters
        ----------
        **query_params : TYPE
            miner (str, required): A mining pool from the table that CQ support
            window (str, optional): Currently, we only support day.
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
            The amount of BTC on the given miner on this window.

        """
        return super().handle_request(self.BTC_MINER_RESERVE, query_params)
    
    def get_btc_miner_netflow(self, **query_params):
        """
        The difference between coins flowing into mining pools and flowing out
        of mining pools. Netflow usually helps us to figure out an increase of
        idle coins waiting to be traded in a certain time frame.

        Parameters
        ----------
        **query_params : TYPE
            miner (str, required): A mining pool from the table that CQ support
            window (str, optional): Currently, we only support day.
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
            Total netflow.

        """
        return super().handle_request(self.BTC_MINER_NETFLOW, query_params)
    
    def get_btc_miner_inflow(self, **query_params):
        """
        This endpoint returns the inflow of BTC into mining pool wallets for as
        far back as CQ track. The average inflow is the average transaction 
        value for transactions flowing into mining pool wallets on a given day.

        Parameters
        ----------
        **query_params : TYPE
            miner (str, required): A mining pool from the table that CQ support
            window (str, optional): Currently, we only support day.
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
            Miner inflows.

        """
        return super().handle_request(self.BTC_MINER_INFLOW, query_params)
    
    def get_btc_miner_outflow(self, **query_params):
        """
        This endpoint returns the outflow of BTC into mining pool wallets for
        as far back as we track. The average outflow is the average transaction
        value for transactions flowing out of mining pool wallets on a given 
        day.

        Parameters
        ----------
        **query_params : TYPE
            miner (str, required): A mining pool from the table that CQ support
            window (str, optional): Currently, we only support day.
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
            Miner outflows.

        """
        return super().handle_request(self.BTC_MINER_OUTFLOW, query_params)
    
    def get_btc_miner_txn_count(self, **query_params):
        """
        Transactions flowing in/out of Bitcoin miners.

        Parameters
        ----------
        **query_params : TYPE
            miner (str, required): A mining pool from the table that CQ support
            window (str, optional): Currently, we only support day.
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
            Miner transactions, in and out.

        """
        return super().handle_request(self.BTC_MINER_TRANSACTIONS_COUNT, query_params)
    
    def get_btc_miner_addr_count(self, **query_params):
        """
        Number of addresses involved in inflow/outflow transactions.

        Parameters
        ----------
        **query_params : TYPE
            miner (str, required): A mining pool from the table that CQ support
            window (str, optional): Currently, we only support day.
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
            Miner addresses count, in and out.

        """
        return super().handle_request(self.BTC_MINER_ADDRESSES_COUNT, query_params)
    
    def get_btc_miner_inhouse_flow(self, **query_params):
        """
        This endpoint returns the in-house flow of BTC within wallets of the 
        same miner for as far back as CQ track. The average in-house flow is 
        the average transaction value for transactions flowing within wallets 
        on a given day.

        Parameters
        ----------
        **query_params : TYPE
            miner (str, required): A mining pool from the table that CQ support
            window (str, optional): Currently, we only support day.
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
            Miner in house inflows.

        """
        return super().handle_request(self.BTC_MINER_IN_HOUSE_FLOW, query_params)
    
    # -------------------------------------
    # BTC Inter Entity Flows
    # -------------------------------------
    
    def get_btc_inter_exch_2_exch(self, **query_params):
        """
        Metrics related to token flows between exchanges. CQ provide several 
        metrics, flow_total, the total number of tokens transferred from one 
        exchange to another, flow_mean, the mean of tokens transferred, and 
        transactions_count_flow, the number of transactions between exchanges.

        Parameters
        ----------
        **query_params : TYPE
            from_exchange (str, required): An exchange that CQ support.
            to_exchange (str, required): An exchange that CQ support. This one
                                        should not be the same as from_exchange
            window (str, optional): Currently CQ support day, hour, and block.
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
            from and to exchange flow.

        """
        return super().handle_request(self.BTC_INTER_EXCHANGE_TO_EXCHANGE, query_params)
    
    def get_btc_inter_miner_2_exch(self, **query_params):
        """
        Metrics related to token flows from mining pools to exchanges. CQ 
        provide several metrics, flow_total, the total number of tokens 
        transferred from a mining pool to an exchange, flow_mean, the mean of 
        tokens transferred, and transactions_count_flow, the number of 
        transactions from a mining pool to an exchange.

        Parameters
        ----------
        **query_params : TYPE
            from_miner (str, required): A miner that CQ support.
            to_exchange (str, required): An exchange that CQ support. This one
                                        should not be the same as from_entity
            window (str, optional): Currently CQ support day, hour, and block.
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
            from miner to exchange flow.

        """
        return super().handle_request(self.BTC_INTER_MINER_TO_EXCHANGE, query_params)
    
    def get_btc_inter_exch_2_miner(self, **query_params):
        """
        Metrics related to token flows from exchanges to mining pools. CQ
        provide several metrics, flow_total, the total number of tokens 
        transferred from a mining pool to an exchange, flow_mean, the mean of 
        tokens transferred, and transactions_count_flow, the number of
        transactions from an exchange to a mining pool.

        Parameters
        ----------
        **query_params : TYPE
            from_exchange (str, required): An exchange that CQ support.
            to_miner (str, required): A miner that CQ support.
            window (str, optional): Currently CQ support day, hour, and block.
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
            exchange to miner flow.

        """
        return super().handle_request(self.BTC_INTER_EXCHANGE_TO_MINER, query_params)
    
    def get_btc_inter_miner_2_miner(self, **query_params):
        """
        Metrics related to token flows between mining pools. Cq provide several
        metrics, flow_total, the total number of tokens transferred from one 
        mining pool to another, flow_mean, the mean of tokens transferred, and 
        transactions_count_flow, the number of transactions between mining
        pools.

        Parameters
        ----------
        **query_params : TYPE
            from_miner (str, required): An miner that CQ support.
            to_miner (str, required): A miner that CQ support.
            window (str, optional): Currently CQ support day, hour, and block.
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
            miner to miner flows of Bitcoin.

        """
        return super().handle_request(self.BTC_INTER_MINER_TO_MINER, query_params)
    
    # -------------------------------------
    # BTC Fund Data
    # -------------------------------------
    
    def get_btc_fund_mkt_price(self, **query_params):
        """
        The price of certain symbol (e.g. gbtc) managed by each fund 
        (e.g. Grayscale) reflects sentiment of investors in regulated markets. 
        In this specific case, having single share of GBTC means having 
        approximately 0.001 BTC invested to Grayscale. This endpoint returns 
        metrics related to the US Dollar(USD) price of fund related stocks 
        (e.g. gbtc). We provide five metrics, price_usd_open, USD opening price
        at the beginning of the window, price_usd_close, USD closing price at 
        the end of the window, price_usd_high, the highest USD price in a given 
        window, price_usd_low, the lowest USD price in a given window, and 
        price_usd_adj_close, USD adjusted closing price at the end of the 
        window. All Symbol is not supported.
        
        supoorted symbols: https://cryptoquant.com/docs#tag/BTC-Fund-Data

        Parameters
        ----------
        **query_params : TYPE
            symbol (str, required): A stock symbol (ticker)
            window (str, optional): Currently CQ only support day.
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
            Market price OHLC and adjusted C data in usd.

        """
        return super().handle_request(self.BTC_FUND_MARKET_PRICE_USD, query_params)
    
    def get_btc_fund_mkt_volume(self, **query_params):
        """
        The volume of certain symbol (e.g. gbtc) managed by each fund 
        (e.g. Grayscale) reflects sentiment of investors in regulated markets. 
        This endpoint returns traded volume of fund related stocks (e.g. gbtc).
        At this endpoint, metrics are calculated by Day. CQ provide one metric,
        volume, traded volume of the window.

        supoorted symbols: https://cryptoquant.com/docs#tag/BTC-Fund-Data

        Parameters
        ----------
        **query_params : TYPE
            symbol (str, required): A stock symbol (ticker)
            window (str, optional): Currently CQ only support day.
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
            market volume for selected bitcoin fund.

        """
        return super().handle_request(self.BTC_FUND_MARKET_VOLUME, query_params)
    
    def get_btc_fund_mkt_premium(self, **query_params):
        """
        The premium of certain symbol (e.g. gbtc) is defined as (market price 
        of the symbol - NAV) divided by NAV where NAV (Native Asset Value) is 
        the current value of holdings (e.g. BTC price multiplied by BTC per 
        Share). Higher the premium indicates market bullish, which also
        indicates downside risk. On the other hand, lower the premium indicates 
        market bearish, which also indicates upside risk. All Symbol market 
        premium is calculated by taking VWAP (Volume Weighted Average Ratio)
        of each fund data volume (usd).

        supoorted symbols: https://cryptoquant.com/docs#tag/BTC-Fund-Data

        Parameters
        ----------
        **query_params : TYPE
            symbol (str, required): A stock symbol (ticker)
            window (str, optional): Currently CQ only support day.
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
            Fund market premium or discount.

        """
        return super().handle_request(self.BTC_FUND_MARKET_PREMIUM, query_params)
    
    def get_btc_fund_digital_assets_holdings(self, **query_params):
        """
        This endpoint returns digital asset holdings status of each fund. For 
        example, Grayscale BTC Holdings along with GBTC represents how much BTC 
        Grayscale is holding for its investment. This metric indicates stock 
        market's sentiment where higher the value means bullish sentiment of 
        investors in stock market.

        Parameters
        ----------
        **query_params : TYPE
            symbol (str, required): A stock symbol (ticker)
            window (str, optional): Currently CQ only support day.
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
            Digital assets holdings for the fund.

        """
        return super().handle_request(self.BTC_FUND_DIGITAL_ASSETS_HOLDINGS, query_params)
    
    # -------------------------------------
    # BTC market/liquidity data
    # -------------------------------------
    
    def get_btc_liq_ohlcv(self, **query_params):
        """
        This endpoint returns metrics related to BTC price. We provide two 
        types of price, CryptoQuant's BTC Index Price and USD or USDT price of
        BTC of global exchanges.
        
        Price OHLCV data consists of five metrics.  open, the opening price at
        the beginning of the window, close, USD closing price at the end of the 
        window,  high, the highest USD price in a given window, low, the lowest 
        USD price in a given window, and volume, the total volume traded in a
        given window.
        
        At this endpoint, metrics are calculated by Minute, Hour and Day.
        BTC Index Price is calculated by taking VWAP(Volume Weighted Average 
        Price) of BTC price data aggregated from all exchanges we provide. The 
        exchanges we provide are as follows.
        
        full documentation: https://cryptoquant.com/docs#tag/BTC-Market-Data/operation/getBTCPriceOHLCV

        Parameters
        ----------
        **query_params : TYPE
            market (str, optional): A market type from the table CQ support.
                                    default is spot.
            exchange (str, optional): A exchange from the table that CQ support
                                    default is all_exchange.
            symbol (str, required): A stock symbol (ticker)
            window (str, optional): Currently CQ only support day.
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
            price ohlcv data.

        """
        return super().handle_request(self.BTC_LIQUIDITY_PRICE_OHLCV, query_params)
    
    def get_btc_liq_open_interest(self, **query_params):
        """
        BTC Perpetual Open Interest from derivative exchanges. Supported 
        exchanges for Open Interest are below. Note we unify the unit of return
        value to USD for each exchange where its contract specification may 
        vary.
        
        full documentation: https://cryptoquant.com/docs#tag/BTC-Market-Data/operation/BTCgetOpenInterest

        Parameters
        ----------
        **query_params : TYPE
            exchange (str, required): A derivative exchange that CQ support.
            window (str, optional): Currently CQ only support day.
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
        TYPE
            DESCRIPTION.

        """
        return super().handle_request(self.BTC_LIQUIDITY_OPEN_INTEREST, query_params)
    
    def get_btc_liq_funding_rates(self, **query_params):
        """
        Funding rates represents traders' sentiments of which position they bet
        on in perpetual swaps market. Positive funding rates implies that many
        traders are bullish and long traders pay funding to short traders. 
        Negative funding rates implies many traders are bearish and short 
        traders pay funding to long traders.
        
        full documentation: https://cryptoquant.com/docs#tag/BTC-Market-Data/operation/BTCgetFundingRates

        Parameters
        ----------
        **query_params : TYPE
            exchange (str, required): A derivative exchange that CQ support.
            window (str, optional): Currently CQ only support day.
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
        TYPE
            DESCRIPTION.

        """
        return super().handle_request(self.BTC_LIQUIDITY_FUNDING_RATES, query_params)
    
    def get_btc_liq_taker_stats(self, **query_params):
        """
        Taker Buy/Sell Stats represent takers' sentiment of which position they
        are taking in the market. This metric is calculated with perpetual swap
        trades in each exchange. taker_buy_volume is volume that takers buy. 
        taker_sell_volume is volume that takers sell. taker_total_volume is the
        sum of taker_buy_volume and taker_sell_volume. taker_buy_ratio is the 
        ratio of taker_buy_volume divided by taker_total_volume. 
        taker_sell_ratio is the ratio of taker_sell_volume divided by 
        taker_total_volume. taker_buy_sell_ratio is the ratio of 
        taker_buy_volume divided by taker_sell_volume. Note we unify the unit 
        of return value to USD for each exchange where its contract
        specification may vary.
        
        full documentation: https://cryptoquant.com/docs#tag/BTC-Market-Data/operation/BTCgetTakerBuySellStats

        Parameters
        ----------
        **query_params : TYPE
            exchange (str, required): A derivative exchange that CQ support.
            window (str, optional): Currently CQ only support day.
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
            Taker buy and sell volume ratio.

        """
        return super().handle_request(self.BTC_LIQUIDITY_TAKER_BUY_SELL_STATS, query_params)
    
    def get_btc_liq_liquidations(self, **query_params):
        """
        Liquidations are sum of forced market orders to exit leveraged 
        positions caused by price volatility. Liquidations indicate current 
        price volatility and traders' sentiment which side they had been 
        betting. Note that Binance's liquidation data collection policy has 
        changed since 2021-04-27, which makes the distribution of the data has
        changed after that.
        
        full documentation: https://cryptoquant.com/docs#tag/BTC-Market-Data/operation/getLiquidations

        Parameters
        ----------
        **query_params : TYPE
            exchange (str, required): A derivative exchange that CQ support.
            window (str, optional): Currently CQ only support day.
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
        return super().handle_request(self.BTC_LIQUIDITY_LIQUIDATIONS, query_params)
    
    def get_btc_liq_capitalization(self, **query_params):
        """
        This endpoint returns metrics related to market capitalization. First, 
        CQ provide market_cap, which is total market capitalization of BTC, 
        calculated by multiplying the total supply with its USD price. 
        Moreover, we provide several adjusted capitalization metrics which are 
        used for further fundamental analysis. realized_cap is the sum of each 
        UTXO * last movement price. Since cryptocurrencies can be lost, 
        unclaimed, or unreachable through various bugs, realized_cap is 
        introduced to discount those coins which have remained unmoved for a 
        long period. It is one way to attempt to measure the value of Bitcoin. 
        This can be described as an on-chain version of volume weighted average
        price(VWAP). average_cap is forever moving average, calculated by 
        dividing the cumulated sum of daily market cap with the age of market.
        Instead of using fixed time for calculating the moving average 
        (e.g. 50 days, 100days ...), this serves as the true mean. Both 
        realized_cap and average_cap are used to calculate delta_cap 
        (realized_cap-average_cap). delta_cap is often used to spot market 
        bottoms. Moreover, by analyzing the movement of delta_cap which 
        oscillates between realized_cap and average_cap, we could notice that 
        market tops are reached when delta_cap is near realized_cap(in a log 
        scaled chart). Another metric that can be used to spot market bottoms 
        is thermo_cap which is the weighted cumulative sum of the mined 
        cryptocurrency price. This metric provides the total amount of funds in
        the blockchain network and also helps to evaluate whether market_cap is
        overvalued or not.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently CQ only support day.
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
            market cap, realized cap, average cap, delta cap, and thermo cap.

        """
        return super().handle_request(self.BTC_LIQUIDITY_CAPITALIZATION, query_params)
    
    def get_btc_liq_coinbase_idx(self, **query_params):
        """
        Coinbase Premium Index is calculated as percent difference from Binance
        price(BTCUSDT) to Coinbase price(BTCUSD). Coinbase Premium Gap is 
        calculated as gap between Coinbase price(BTCUSD) and Binance 
        price(BTCUSDT). The higher the premium, the stronger the spot buying 
        pressure from Coinbase.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently CQ only support day.
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
        return super().handle_request(self.BTC_LIQUIDITY_COINBASE_PREMIUM_INDEX, query_params)
    
    # -------------------------------------
    # BTC Miner data
    # -------------------------------------
    
    def get_btc_miner_company_data(self, **query_params):
        """
        This endpoint returns BTC mining company data. Company data consists of
        statistical metrics based on rewards and production data for each 
        mining company. coinbase_rewards, The daily amount of Bitcoin mined 
        directly from a coinbase transaction. And coinbase_rewards will only be
        added to mara. other_mining_rewards, The daily amount of Bitcoin 
        received as payment from a mining pool. Tipically, mining pools pay 
        miners with Bitcoin from a coinbase transaction. total_rewards, The 
        daily sum of coinbase rewards and other mining rewards (in number of 
        Bitcoin). accumulated_monthly_rewards, The daily running sum of total 
        rewards in each month (in number of Bitcoin). unique_txn, The total 
        number of Bitcoin transactions involving a mining reward. 
        active_address_count, The number of addresses from a company that 
        received a block reward each day. reported_production, The company's 
        reported total monthly production (in number of Bitcoin). 
        report_accuracy, The ratio of accumulated monthly rewards to reported 
        production times 100. It represents the % of total reported production 
        captured by On-chain transactions. closing_usd, The daily closing price
        of Bitcoin in USD. total_daily_rewards_closing_usd, Daily total rewards
        in USD using the closing usd price. 
        accumulated_monthly_rewards_closing_usd, accumulated monthly rewards in
        usd using the closing usd price.
        
        full documentation: https://cryptoquant.com/docs#tag/BTC-Miner-Data/operation/getCompanies

        Parameters
        ----------
        **query_params : TYPE
            miner (str, required): A mining company from the table CQ support
            window (str, optional): Currently CQ only support day.
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
        TYPE
            DESCRIPTION.

        """
        return super().handle_request(self.BTC_BITCOIN_MINER_DATA, query_params)
    
    # -------------------------------------
    # BTC Network Data
    # -------------------------------------
    
    def get_btc_net_supply(self, **query_params):
        """
        This end point returns metrics related to bitcoin supply, i.e. the 
        amount of bitcoin in existence. We currently provide two metrics, 
        supply_total , the total amount of bitcoins in existence (sum of all 
        bitcoins issued by the coinbase reward), and supply_new, the amount of
        newly issued tokens in a given window.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently CQ support day, hour, block.
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
            supply total and new.

        """
        return super().handle_request(self.BTC_NETWORK_SUPPLY, query_params)
    
    def get_btc_net_velocity(self, **query_params):
        """
        This endpoint returns metrics related to the velocity of bitcoin. 
        Bitcoin's velocity is calculated by dividing the trailing 1 year 
        estimated transaction volume(the cumulated sum of transferred tokens) 
        by current supply. Velocity is a metric that explains how actively is 
        money circulating in the market.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently CQ support day, hour, block.
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
            Estimated transaction volume in the trailing 1 year divided by
            current total supply.

        """
        return super().handle_request(self.BTC_NETWORK_VELOCITY, query_params)
    
    def get_btc_net_trx_count(self, **query_params):
        """
        This endpoint returns metrics related to the number of transactions.
        CQ provide several metrics, transactions_count_total, the total number
        of transactions, and transactions_count_mean, the mean number of 
        transactions.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently CQ support day, hour, block.
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
            total transactions and mean.

        """
        return super().handle_request(self.BTC_NETWORK_TRANSACTIONS_COUNT, query_params)
    
    def get_btc_net_addr_count(self, **query_params):
        """
        This endpoint returns metrics relating to the number of used bitcoin 
        addresses. We provide several metrics, addresses_count_active, the 
        total number of unique addresses that were active (either sender or 
        receiver) on the blockchain, addresses_count_sender, the number of 
        addresses that were active as a sender, and addresses_count_receiver, 
        the number of addresses that were active as a receiver.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently CQ support day, hour, block.
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
            Count of active, sender and receiver.

        """
        return super().handle_request(self.BTC_NETWORK_ADDRESSES_COUNT, query_params)
    
    def get_btc_net_tokens_transferred(self, **query_params):
        """
        This endpoint returns metrics related to the number of tokens 
        transferred, i.e transaction volume. We provide several metrics, 
        tokens_transferred_total, the total number of transferred tokens, 
        tokens_transferred_mean, the mean of number of transferred tokens per
        transaction, and tokens_transferred_median, the median of tokens 
        transferred per transaction.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently CQ support day, hour, block.
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
            transferred, mean trensfered and median transferred tokens.

        """
        return super().handle_request(self.BTC_NETWORK_TOKENS_TRANSFERRED, query_params)
    
    def get_btc_net_block_bytes(self, **query_params):
        """
        The mean size(in bytes) of all blocks generated.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently CQ support day, hour, block.
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
        return super().handle_request(self.BTC_NETWORK_BLOCK_BYTES, query_params)
    
    def get_btc_net_block_count(self, **query_params):
        """
        The number of blocks generated in a given window.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently CQ support day and hour.
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
        return super().handle_request(self.BTC_NETWORK_BLOCK_COUNT, query_params)
    
    def get_btc_net_block_interval(self, **query_params):
        """
        The average time between blocks generated displayed in seconds.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently CQ support day, hour, and block.
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
        return super().handle_request(self.BTC_NETWORK_BLOCK_INTERVAL, query_params)
    
    def get_btc_net_utxo_count(self, **query_params):
        """
        The number of total number of unspent transaction outputs existing at 
        the specified point.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently CQ support day, hour, and block.
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
            Number of total number of unspent transaction output at a given 
            period.

        """
        return super().handle_request(self.BTC_NETWORK_UTXO_COUNT, query_params)
    
    def get_btc_net_fees(self, **query_params):
        """
        This endpoint returns the statistics related to fees that are paid to 
        bitcoin miners. In general, fees are calculated by subtracting the 
        newly issued bitcoin from the total block reward of each blocks. We
        provide three statistics, fees_total, the sum of all fees, 
        fees_block_mean, the average fee per block, and fees_reward_percent, 
        the percentage of fees relative to the total block reward. 
        Additionally, these can be viewed in terms of USD.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently CQ support day, hour, and block.
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
            Fees in the bitcoin network.

        """
        return super().handle_request(self.BTC_NETWORK_FEES, query_params)
    
    def get_btc_net_fees_trx(self, **query_params):
        """
        This endpoint returns the statistics related to fees per transaction 
        that are paid to bitcoin miners. In general, fees are calculated by 
        subtracting the newly issued bitcoin from the total block reward of 
        each blocks, and this is divided by the number of transactions to 
        calculate the average fee per transaction in each block. We provide two
        statistics, fees_transaction_mean, the average fee per transaction, 
        fees_transaction_median, the median fee per transaction. Additionally, 
        these values can be calculated in USD.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently CQ support day, hour, and block.
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
            statistics related to fees per transaction that are paid to bitcoin
            miners.

        """
        return super().handle_request(self.BTC_NETWORK_FEES_TRANSACTION, query_params)
    
    def get_btc_net_blockreward(self, **query_params):
        """
        The sum of block rewards (including mining or staking rewards and 
        transaction fees). CQ also provide this value in usd.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently CQ support day, hour, and block.
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
            The sum of block rewards (including mining or stacking rewards and
            transaction fees). CQ al provides this value in usd.

        """
        return super().handle_request(self.BTC_NETWORK_BLOCKREWARD, query_params)
    
    def get_btc_net_difficulty(self, **query_params):
        """
        Difficulty of mining a new block.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently CQ support day, hour, and block.
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
        TYPE
            DESCRIPTION.

        """
        return super().handle_request(self.BTC_NETWORK_DIFFICULTY, query_params)
    
    def get_btc_net_hashrate(self, **query_params):
        """
        The mean speed at which miners in the network are solving hash 
        problems. It is displayed as hashes (Gigabytes) per second.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently CQ support day, hour, and block.
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
            The mean speed at which hash problems are being solved across all
            miners in the network. It is displayed as hash(bytes) per second.

        """
        return super().handle_request(self.BTC_NETWORK_HASHRATE, query_params)
    
    # -------------------------------------
    # BTC Mempool Statistics
    # -------------------------------------
    
    def get_btc_mem_stats_by_relative_fee(self, **query_params):
        """
        Mempool Statistics contains three metrics related to transactions
        waiting to be confirmed. You can see metrics for the number of 
        transactions, the total amount of fees, and the aggregate size in bytes
        of transactions. Each metric was calculated based on fee level.
        
        full doc: https://cryptoquant.com/docs#tag/BTC-Mempool-Statistics/operation/getBTCMempoolStatsByRelativeFee

        Parameters
        ----------
        **query_params : TYPE
            metric_type (str, required): A metric type derived from statistics.
                                        Supported metrics are:
            Metric Type	Description
            tx_count*	The total number of unconfirmed transactions (Number)
            total_size	The aggregated size in bytes of transactions (Megabyte)
            total_fee	The total fee of unconfirmed transactions (BTC)
            
            window (str, optional): Currently CQ support day and hour.
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
            Bitcoin mempool stats by relative fee.

        """
        return super().handle_request(self.BTC_MEMPOOL_STATS_BY_RELATIVE_FEE, query_params)
    
    def get_btc_mem_stats_in_total(self, **query_params):
        """
        Mempool Statistics contains three metrics related to transactions 
        waiting to be confirmed. You can see metrics for the number of 
        transactions, the total amount of fees, and the aggregate size in bytes
        of transactions.

        full doc: https://cryptoquant.com/docs#tag/BTC-Mempool-Statistics/operation/getBTCMempoolStatsInTotal

        Parameters
        ----------
        **query_params : TYPE
            metric_type (str, required): A metric type derived from statistics.
                                        Supported metrics are:
            Metric Type	Description
            tx_count*	The total number of unconfirmed transactions (Number)
            total_size	The aggregated size in bytes of transactions (Megabyte)
            total_fee	The total fee of unconfirmed transactions (BTC)
            
            window (str, optional): Currently CQ support day and hour.
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
            Bitcoin mempool stats (sum).

        """
        return super().handle_request(self.BTC_MEMPOOL_STATS_IN_TOTAL, query_params)
    
    # -------------------------------------
    # BTC Lightning Network Statistics
    # -------------------------------------
    
    def get_btc_light_stats(self, **query_params):
        """
        Lightning Network Statistics contains various metrics which are 
        calculated from lightning network.

        Parameters
        ----------
        **query_params : TYPE
            window (str, optional): Currently CQ support day and hour.
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
            BTC Lightning network stats.

        """
        return super().handle_request(self.BTC_LIGHTNING_NETWORK, query_params)