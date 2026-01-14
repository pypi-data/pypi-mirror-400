import akshare as ak  # type: ignore
import pandas as pd

from ..cache import cache
from .base import OptionsDataProvider


class SinaOptionsProvider(OptionsDataProvider):
    """Adapter for Sina/EastMoney options data API

    Note: Options data from akshare may have limited availability.
    The API structure varies by data source and expiration.
    """

    @cache(
        "options_chain_cache",
        key=lambda self: f"sina_options_chain_{self.underlying_symbol}",
    )
    def get_options_chain(self) -> pd.DataFrame:
        """Fetches options chain data

        Returns:
            pd.DataFrame:
            - underlying: 标的代码
            - symbol: 期权代码
            - name: 期权名称
            - option_type: 期权类型 (call/put)
            - strike: 行权价
            - expiration: 到期日
            - price: 最新价
            - change: 涨跌额
            - pct_change: 涨跌幅(%)
            - volume: 成交量
            - open_interest: 持仓量
            - implied_volatility: 隐含波动率
        """
        try:
            # Use the correct akshare API function for options
            raw_data = ak.option_sse_list_sina(
                symbol=self.underlying_symbol, exchange="null"
            )
            # Handle both DataFrame and list return types
            if isinstance(raw_data, list):
                if not raw_data:
                    return pd.DataFrame(
                        columns=[
                            "underlying",
                            "symbol",
                            "name",
                            "option_type",
                            "strike",
                            "expiration",
                            "price",
                            "change",
                            "pct_change",
                            "volume",
                            "open_interest",
                            "implied_volatility",
                        ]
                    )
                raw_df = pd.DataFrame(raw_data)
            else:
                raw_df = raw_data
            return self._clean_options_chain(raw_df)
        except Exception as e:
            raise ValueError(f"Failed to fetch options chain: {str(e)}") from e

    @cache(
        "options_realtime_cache",
        key=lambda self, symbol: f"sina_options_realtime_{symbol}",
    )
    def get_options_realtime(self, symbol: str) -> pd.DataFrame:
        """Fetches realtime options quote data

        Args:
            symbol: 期权代码 (e.g., '10004005')

        Returns:
            pd.DataFrame:
            - symbol: 期权代码
            - underlying: 标的代码
            - price: 最新价
            - change: 涨跌额
            - pct_change: 涨跌幅(%)
            - timestamp: 时间戳
            - volume: 成交量
            - open_interest: 持仓量
            - iv: 隐含波动率
        """
        try:
            if not symbol:
                # Return all options if no specific symbol provided
                raw_df = ak.option_sse_list_sina(
                    symbol=self.underlying_symbol, exchange="null"
                )
                df = self._clean_options_realtime(raw_df)
                return df

            # Get specific option data
            raw_df = self._get_single_option_data(symbol)
            return self._clean_single_option(raw_df)
        except Exception as e:
            raise ValueError(f"Failed to fetch options realtime data: {str(e)}") from e

    def get_options_expirations(self, underlying_symbol: str) -> list[str]:
        """Fetches available expiration dates for options

        Args:
            underlying_symbol: 标的代码

        Returns:
            list[str]: 可用的到期日列表
        """
        try:
            raw_df = ak.option_sse_list_sina(symbol=underlying_symbol, exchange="null")
            if "到期日" in raw_df.columns:
                expirations = raw_df["到期日"].unique().tolist()
                return sorted(expirations)
            elif "期日" in raw_df.columns:
                expirations = raw_df["期日"].unique().tolist()
                return sorted(expirations)
            return []
        except Exception as e:
            raise ValueError(f"Failed to fetch options expirations: {str(e)}") from e

    def get_options_history(
        self,
        symbol: str,
        start_date: str = "1970-01-01",
        end_date: str = "2030-12-31",
    ) -> pd.DataFrame:
        """Fetches options historical data

        Args:
            symbol: 期权代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            pd.DataFrame:
            - timestamp: 时间戳
            - symbol: 期权代码
            - open: 开盘价
            - high: 最高价
            - low: 最低价
            - close: 收盘价
            - volume: 成交量
            - open_interest: 持仓量
            - settlement: 结算价
        """
        start_date = start_date.replace("-", "")
        end_date = end_date.replace("-", "")

        try:
            raw_df = ak.option_sina_hist_sina(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
            )
            return self._clean_options_history(raw_df, symbol)
        except Exception as e:
            raise ValueError(f"Failed to fetch options history: {str(e)}") from e

    def _get_single_option_data(self, symbol: str) -> pd.DataFrame:
        """Get single option data from all options chain"""
        raw_df: pd.DataFrame = ak.option_sse_list_sina(
            symbol=self.underlying_symbol, exchange="null"
        )
        if "代码" in raw_df.columns:
            result: pd.DataFrame = raw_df[raw_df["代码"] == symbol]
            return result
        elif "code" in raw_df.columns:
            result = raw_df[raw_df["code"] == symbol]
            return result
        return pd.DataFrame()

    def _clean_options_chain(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and standardizes options chain data"""
        column_map = {
            "代码": "symbol",
            "名称": "name",
            "行权价": "strike",
            "到期日": "expiration",
            "最新价": "price",
            "涨跌额": "change",
            "涨跌幅": "pct_change",
            "成交量": "volume",
            "持仓量": "open_interest",
        }

        available_columns = {
            src: target for src, target in column_map.items() if src in raw_df.columns
        }

        if not available_columns:
            raise ValueError("Expected columns not found in options chain data")

        df = raw_df.rename(columns=available_columns)

        # Add underlying symbol
        df["underlying"] = self.underlying_symbol

        # Determine option type from name
        if "name" in df.columns:
            df["option_type"] = df["name"].apply(
                lambda x: "call"
                if "购" in x or "c" in x.lower() or "看涨" in x
                else "put"
                if "沽" in x or "p" in x.lower() or "看跌" in x
                else ""
            )

        # Add implied volatility (placeholder, as it may not be available)
        df["implied_volatility"] = None

        return self._select_options_columns(df)

    def _clean_options_realtime(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and standardizes options realtime data"""
        column_map = {
            "代码": "symbol",
            "名称": "name",
            "最新价": "price",
            "涨跌额": "change",
            "涨跌幅": "pct_change",
            "成交量": "volume",
            "持仓量": "open_interest",
        }

        available_columns = {
            src: target for src, target in column_map.items() if src in raw_df.columns
        }

        df = raw_df.rename(columns=available_columns)

        df = df.assign(
            timestamp=lambda x: pd.Timestamp.now(tz="Asia/Shanghai"),
            underlying=self.underlying_symbol,
            iv=None,  # Implied volatility placeholder
        )

        return self._select_realtime_columns(df)

    def _clean_single_option(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and standardizes single option data"""
        column_map = {
            "代码": "symbol",
            "名称": "name",
            "最新价": "price",
            "涨跌额": "change",
            "涨跌幅": "pct_change",
            "成交量": "volume",
            "持仓量": "open_interest",
        }

        available_columns = {
            src: target for src, target in column_map.items() if src in raw_df.columns
        }

        df = raw_df.rename(columns=available_columns)

        df = df.assign(
            timestamp=lambda x: pd.Timestamp.now(tz="Asia/Shanghai"),
            underlying=self.underlying_symbol,
            iv=None,
        )

        required_columns = [
            "symbol",
            "underlying",
            "price",
            "change",
            "pct_change",
            "timestamp",
            "volume",
            "open_interest",
            "iv",
        ]
        return df[[col for col in required_columns if col in df.columns]]

    def _clean_options_history(self, raw_df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Cleans and standardizes options historical data"""
        column_map = {
            "日期": "timestamp",
            "开盘": "open",
            "收盘": "close",
            "最高": "high",
            "最低": "low",
            "成交量": "volume",
            "持仓量": "open_interest",
            "结算价": "settlement",
        }

        available_columns = {
            src: target for src, target in column_map.items() if src in raw_df.columns
        }

        if not available_columns:
            raise ValueError("Expected columns not found in options history data")

        df = raw_df.rename(columns=available_columns)

        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.tz_localize(
                "Asia/Shanghai"
            )

        df["symbol"] = symbol

        if "open_interest" in df.columns:
            df["open_interest"] = df["open_interest"].astype("int64")

        return self._select_history_columns(df)

    def _select_options_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Selects and orders the standard options chain columns"""
        standard_columns = [
            "underlying",
            "symbol",
            "name",
            "option_type",
            "strike",
            "expiration",
            "price",
            "change",
            "pct_change",
            "volume",
            "open_interest",
            "implied_volatility",
        ]
        return df[[col for col in standard_columns if col in df.columns]]

    def _select_realtime_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Selects and orders the standard realtime options columns"""
        standard_columns = [
            "symbol",
            "underlying",
            "price",
            "change",
            "pct_change",
            "timestamp",
            "volume",
            "open_interest",
            "iv",
        ]
        return df[[col for col in standard_columns if col in df.columns]]

    def _select_history_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Selects and orders the standard options history columns"""
        standard_columns = [
            "timestamp",
            "symbol",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "open_interest",
            "settlement",
        ]
        return df[[col for col in standard_columns if col in df.columns]]
