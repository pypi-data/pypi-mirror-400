import json
from queue import Queue
from typing import Any, Literal
from urllib.parse import urlencode

import polars as pl
import pyotp
import requests
import shortuuid  # type:ignore
from retrying import retry  # type: ignore

from quantplay.broker.generics.broker import Broker
from quantplay.broker.kotak_utils.kotak_ws import NeoWebSocket
from quantplay.exception import TokenException
from quantplay.exception.exceptions import (
    BrokerException,
    InvalidArgumentException,
    QuantplayOrderPlacementException,
    retry_exception,
)
from quantplay.model.broker import (
    MarginsResponse,
    ModifyOrderRequest,
    UserBrokerProfileResponse,
)
from quantplay.model.generics import (
    ExchangeType,
    OrderStatusType,
    OrderTypeType,
    ProductType,
    TransactionType,
)
from quantplay.model.order_event import OrderUpdateEvent
from quantplay.utils.constant import Constants
from quantplay.utils.pickle_utils import InstrumentData
from quantplay.wrapper.aws.s3 import S3Utils

# V2 API Fixed endpoints for login
LOGIN_BASE_URL = "https://mis.kotaksecurities.com"


class KotakV2(Broker):
    """
    Kotak Neo V2 API Implementation
    Uses TOTP-based authentication and dynamic baseUrl for trading APIs

    Key V2 API Characteristics:
    - Two-step authentication: TOTP login → MPIN validation
    - Dynamic baseUrl returned after MPIN validation (not hardcoded)
    - Most order APIs use application/x-www-form-urlencoded with jData parameter
    - Report APIs (order_book, positions, etc.) use application/json GET requests
    - Server routing via hsServerId (sId) query parameter
    - Supports regular, Cover Order (CO), and Bracket Order (BO) types

    Implementation Notes:
    - Based on official Kotak Neo V2 Postman collection
    - Extended fields in modify_order for complete API support
    - Holdings API uses different path: portfolio/v1/holdings
    """

    def __init__(
        self,
        user_id: str,
        order_updates: Queue[OrderUpdateEvent] | None = None,
        access_token: str | None = None,
        mobilenumber: str | None = None,
        password: str | None = None,
        totp_secret: str | None = None,
        mpin: str | None = None,
        configuration: dict[str, str] | None = None,
        load_instrument: bool = True,
        verify_config: bool = True,
    ) -> None:
        super().__init__()

        self.user_id = user_id
        self.order_updates = order_updates
        self.configuration: dict[str, str] = {}
        self.base_url: str = ""

        if configuration:
            # Restore from saved configuration
            self.configuration = configuration
            self.base_url = configuration.get("baseUrl", "")

            if verify_config:
                self.margins()  # Verify configuration is valid

        elif access_token and mobilenumber and totp_secret and mpin:
            # New authentication flow
            self.login_v2(access_token, mobilenumber, user_id, totp_secret, mpin)

        else:
            raise InvalidArgumentException(
                "Either provide configuration or all required auth parameters: "
                "access_token, mobilenumber, totp_secret, mpin"
            )

        if load_instrument:
            self.load_instrument()

    def load_instrument(self, file_name: str | None = None) -> None:
        """Load instrument data from cache or S3"""
        try:
            instrument_cache = InstrumentData.get_instance()
            if instrument_cache is not None:
                self.symbol_data = instrument_cache.load_data("kotak_instruments")
                Constants.logger.info("[LOADING_INSTRUMENTS] loading data from cache")
                return
            raise Exception("InstrumentData cache not available")
        except Exception:
            inst_data_df = S3Utils.get_parquet(
                "quantplay-market-data/symbol_data/kotak_instruments.parquet"
            )
            inst_data_df = inst_data_df.with_columns(
                pl.col("tradingsymbol").alias("broker_symbol")
            )
            self.instrument_data = inst_data_df
            self.initialize_symbol_data_v2(save_as="kotak_instruments")

        self.initialize_broker_symbol_map()

    def login_v2(
        self,
        access_token: str,
        mobilenumber: str,
        user_id: str,
        totp_secret: str,
        mpin: str,
    ) -> None:
        """
        V2 Authentication Flow:
        1. TOTP Login - Get view token
        2. MPIN Validation - Get trade token and baseUrl
        """
        # Step 1: TOTP Login
        totp_code = pyotp.TOTP(totp_secret).now()

        totp_login_resp = requests.post(
            url=f"{LOGIN_BASE_URL}/login/1.0/tradeApiLogin",
            headers={
                "Authorization": access_token,
                "neo-fin-key": "neotradeapi",
                "Content-Type": "application/json",
            },
            data=json.dumps(
                {
                    "mobileNumber": mobilenumber,
                    "ucc": user_id,
                    "totp": totp_code,
                }
            ),
        )

        if not totp_login_resp.ok:
            raise InvalidArgumentException(f"TOTP Login failed: {totp_login_resp.text}")

        totp_resp = totp_login_resp.json()

        if "data" not in totp_resp:
            raise TokenException(
                f"TOTP Login failed: {totp_resp.get('message', 'Unknown error')}"
            )

        totp_data = totp_resp["data"]
        view_token = totp_data.get("token")
        view_sid = totp_data.get("sid")

        if not view_token or not view_sid:
            raise TokenException("Failed to get view token or sid from TOTP login")

        # Step 2: MPIN Validation
        mpin_validate_resp = requests.post(
            url=f"{LOGIN_BASE_URL}/login/1.0/tradeApiValidate",
            headers={
                "Authorization": access_token,
                "neo-fin-key": "neotradeapi",
                "Content-Type": "application/json",
                "sid": view_sid,
                "Auth": view_token,
            },
            data=json.dumps({"mpin": mpin}),
        )

        if not mpin_validate_resp.ok:
            raise InvalidArgumentException(
                f"MPIN validation failed: {mpin_validate_resp.text}"
            )

        mpin_resp = mpin_validate_resp.json()

        if "data" not in mpin_resp:
            raise TokenException(
                f"MPIN validation failed: " f"{mpin_resp.get('message', 'Unknown error')}"
            )

        mpin_data = mpin_resp["data"]

        if mpin_data.get("status") != "success":
            raise TokenException("MPIN validation failed - status not success")

        # Extract and store configuration
        self.base_url = mpin_data.get("baseUrl", "")
        self.configuration = {
            "access_token": access_token,
            "Auth": mpin_data.get("token", ""),
            "Sid": mpin_data.get("sid", ""),
            "baseUrl": self.base_url,
            "hsServerId": mpin_data.get("hsServerId", ""),
            "dataCenter": mpin_data.get("dataCenter", ""),
        }

        if not self.base_url:
            raise TokenException("Failed to get baseUrl from MPIN validation")

        Constants.logger.info(f"[KOTAK_V2] Login successful, baseUrl: {self.base_url}")

    def order_history(self, order_id: str) -> pl.DataFrame:
        """Get order history for a specific order"""
        body = {"nOrdNo": order_id}
        order_history_resp = self.request("order_history", body=body)
        if order_history_resp is None:
            raise BrokerException("Failed to get order history from Kotak V2")
        order_history = order_history_resp["data"]
        order_history_df = pl.DataFrame(order_history)[
            [
                "tok",
                "flDtTm",
                "nOrdNo",
                "exch",
                "prod",
                "trdSym",
                "trnsTp",
                "qty",
                "prcTp",
                "GuiOrdId",
            ]
        ]
        order_history_df = order_history_df.rename(
            {
                "tok": "token",
                "flDtTm": "update_timestamp",
                "nOrdNo": "order_id",
                "exch": "exchange",
                "prod": "product",
                "trdSym": "tradingsymbol",
                "trnsTp": "transaction_type",
                "qty": "quantity",
                "prcTp": "order_type",
                "GuiOrdId": "tag",
            }
        )
        order_history_df = order_history_df.with_columns(
            pl.col("update_timestamp")
            .str.strptime(pl.Datetime(time_unit="ms"), format="%d-%b-%Y %H:%M:%S")
            .alias("update_timestamp")
        ).sort("update_timestamp")

        return order_history_df

    # **
    # ** GET Api's
    # **

    def orders(self, tag: str | None = None, add_ltp: bool = True) -> pl.DataFrame:
        """Fetch all orders"""
        orders_resp = self.request("order_book")

        if orders_resp is None:
            raise BrokerException("Failed to get orders from Kotak V2")

        if orders_resp.get("error", None) is not None:
            raise BrokerException(f"Kotak V2 Error : {orders_resp['error']}")

        if (
            orders_resp.get("stat", "Not_Ok") == "Not_Ok"
            and orders_resp["errMsg"] == "No Data"
        ):
            return pl.DataFrame(schema=self.orders_schema)

        orders_df = pl.DataFrame(orders_resp["data"])
        if "rejRsn" not in orders_df.columns:
            orders_df = orders_df.with_columns(pl.lit("").alias("rejRsn"))

        orders_df = orders_df.rename(
            {
                "actId": "user_id",
                "nOrdNo": "order_id",
                "exSeg": "exchange",
                "prod": "product",
                "trdSym": "tradingsymbol",
                "ordSt": "status",
                "prcTp": "order_type",
                "trnsTp": "transaction_type",
                "prc": "price",
                "avgPrc": "average_price",
                "trgPrc": "trigger_price",
                "ordDtTm": "order_timestamp",
                "tok": "token",
                "qty": "quantity",
                "fldQty": "filled_quantity",
                "rejRsn": "status_message",
            }
        )

        orders_df = orders_df.with_columns(
            pl.lit("regular").alias("variety"),
            pl.col("GuiOrdId").str.split(":").list.get(0).alias("tag"),
            pl.lit(None).alias("ltp"),
            pl.col("status_message").alias("status_message_raw"),
            pl.col("order_timestamp")
            .str.strptime(pl.Datetime(time_unit="ms"), format="%d-%b-%Y %H:%M:%S")
            .alias("order_timestamp"),
            pl.col("status").str.to_uppercase().alias("status"),
        )
        orders_df = orders_df.with_columns(
            pl.col("order_timestamp").alias("update_timestamp"),
            (pl.col("quantity") - pl.col("filled_quantity")).alias("pending_quantity"),
            pl.col("tradingsymbol").str.replace("-EQ", "").alias("tradingsymbol"),
        )
        orders_df = orders_df[list(self.orders_schema.keys())].cast(self.orders_schema)

        orders_df = orders_df.with_columns(
            pl.when(pl.col("exchange") == "nse_cm")
            .then(pl.lit("NSE"))
            .when(pl.col("exchange") == "bse_cm")
            .then(pl.lit("BSE"))
            .when(pl.col("exchange") == "nse_fo")
            .then(pl.lit("NFO"))
            .when(pl.col("exchange") == "bse_fo")
            .then(pl.lit("BFO"))
            .when(pl.col("exchange") == "cde_fo")
            .then(pl.lit("CDS"))
            .when(pl.col("exchange") == "bcs-fo")
            .then(pl.lit("BCD"))
            .when(pl.col("exchange") == "mcx_fo")
            .then(pl.lit("MCX"))
            .otherwise(pl.col("exchange"))
            .alias("exchange"),
            pl.when(pl.col("order_type") == "L")
            .then(pl.lit("LIMIT"))
            .when(pl.col("order_type") == "MKT")
            .then(pl.lit("MARKET"))
            .otherwise(pl.col("order_type"))
            .alias("order_type"),
            pl.when(pl.col("transaction_type") == "B")
            .then(pl.lit("BUY"))
            .when(pl.col("transaction_type") == "S")
            .then(pl.lit("SELL"))
            .otherwise(pl.col("transaction_type"))
            .alias("transaction_type"),
        )

        return orders_df

    def add_ltps(self, df: pl.DataFrame) -> pl.DataFrame:
        """Add LTP to DataFrame"""
        data = df.to_dicts()
        token_list = [self.token_converter(int(d["token"]), d["exchange"]) for d in data]
        ltps: list[float] = self.ltp_from_tokens(token_list)  # type:ignore

        ltps = [float(a) if a else None for a in ltps]  # type:ignore
        ltps = pl.Series("ltp", ltps, dtype=pl.Float64)  # type:ignore

        df = df.with_columns(ltps)

        df = df.with_columns(
            (
                pl.col("sell_value")
                - pl.col("buy_value")
                + pl.col("quantity") * pl.col("ltp")
            ).alias("pnl")
        )
        return df

    def positions(self, drop_cnc: bool = True, add_ltp: bool = True) -> pl.DataFrame:
        """Fetch all positions"""
        positions_resp = self.request("positions")

        if positions_resp is None:
            raise BrokerException("Failed to get positions from Kotak V2")

        if positions_resp["stat"] == "Not_Ok" and positions_resp["errMsg"] == "No Data":
            return pl.DataFrame(schema=self.positions_schema)
        positions_df = pl.DataFrame(positions_resp["data"])

        positions_df = positions_df.rename(
            {
                "trdSym": "tradingsymbol",
                "buyAmt": "buy_value",
                "sellAmt": "sell_value",
                "prod": "product",
                "tok": "token",
                "exSeg": "exchange",
                "optTp": "option_type",
            }
        )
        positions_df = positions_df.with_columns(
            (
                pl.col("flBuyQty").fill_null(0).cast(pl.Int64)
                + pl.col("cfBuyQty").fill_null(0).cast(pl.Int64)
            ).alias("buy_quantity"),
            (
                pl.col("flSellQty").fill_null(0).cast(pl.Int64)
                + pl.col("cfSellQty").fill_null(0).cast(pl.Int64)
            ).alias("sell_quantity"),
            pl.lit(0).alias("ltp"),
            (
                pl.col("buy_value").cast(pl.Float64) + pl.col("cfBuyAmt").cast(pl.Float64)
            ).alias("buy_value"),
            (
                pl.col("sell_value").cast(pl.Float64)
                + pl.col("cfSellAmt").cast(pl.Float64)
            ).alias("sell_value"),
            pl.lit(0).alias("pnl"),
            pl.when(pl.col("exchange") == "nse_cm")
            .then(pl.lit("NSE"))
            .when(pl.col("exchange") == "bse_cm")
            .then(pl.lit("BSE"))
            .when(pl.col("exchange") == "nse_fo")
            .then(pl.lit("NFO"))
            .when(pl.col("exchange") == "bse_fo")
            .then(pl.lit("BFO"))
            .when(pl.col("exchange") == "cde_fo")
            .then(pl.lit("CDS"))
            .when(pl.col("exchange") == "bcs-fo")
            .then(pl.lit("BCD"))
            .when(pl.col("exchange").is_in(["mcx", "mcx_fo"]))
            .then(pl.lit("MCX"))
            .otherwise(pl.col("exchange"))
            .alias("exchange"),
            pl.when(pl.col("option_type") == "XX")
            .then(pl.lit(None))
            .otherwise(pl.col("option_type"))
            .alias("option_type"),
        )
        positions_df = positions_df.with_columns(
            (pl.col("buy_quantity") - pl.col("sell_quantity")).alias("quantity")
        )
        positions_df = positions_df.with_columns(
            (
                (
                    pl.col("buy_value").cast(pl.Float64)
                    - pl.col("sell_value").cast(pl.Float64)
                )
                / pl.col("quantity")
            ).alias("average_price")
        )
        positions_df = positions_df.with_columns(
            pl.when(pl.col("quantity").cast(pl.Int32) == 0)
            .then(pl.lit(0))
            .otherwise(pl.col("average_price"))
            .alias("average_price"),
            pl.col("tradingsymbol").str.replace("-EQ", "").alias("tradingsymbol"),
        )
        positions_df = positions_df[list(self.positions_schema.keys())].cast(
            self.positions_schema
        )

        return self.add_ltps(positions_df)

    def trades(self) -> pl.DataFrame:
        """Fetch trade book"""
        self.request("trade_report")
        return pl.DataFrame(schema=self.positions_schema)

    def holdings(self, add_ltp: bool = True) -> pl.DataFrame:
        """Fetch holdings - V2 API has updated response structure"""
        holdings_resp = self.request("holdings")

        if holdings_resp is None or len(holdings_resp["data"]) == 0:
            return pl.DataFrame(schema=self.holidings_schema)

        holdings_df = pl.DataFrame(holdings_resp["data"])
        holdings_df = holdings_df.rename(
            {
                "symbol": "tradingsymbol",
                "exchangeSegment": "exchange",
                "exchangeIdentifier": "token",
                "averagePrice": "average_price",
                "closingPrice": "price",
                "holdingCost": "buy_value",
            }
        )
        holdings_df = holdings_df.with_columns(
            pl.when(pl.col("exchange") == "nse_cm")
            .then(pl.lit("NSE"))
            .when(pl.col("exchange") == "bse_cm")
            .then(pl.lit("BSE"))
            .when(pl.col("exchange") == "nse_fo")
            .then(pl.lit("NFO"))
            .when(pl.col("exchange") == "bse_fo")
            .then(pl.lit("BFO"))
            .when(pl.col("exchange") == "cde_fo")
            .then(pl.lit("CDS"))
            .when(pl.col("exchange") == "bcs-fo")
            .then(pl.lit("BCD"))
            .when(pl.col("exchange") == "mcx")
            .then(pl.lit("MCX"))
            .when(pl.col("exchange") == "mcx_fo")
            .then(pl.lit("MCX"))
            .otherwise(pl.col("exchange"))
            .alias("exchange"),
            pl.lit(None).alias("isin"),
        )

        holdings_df = holdings_df.with_columns(
            (pl.col("quantity") * pl.col("price")).alias("value"),
            pl.lit(0).alias("pledged_quantity"),
            (pl.col("quantity") * pl.col("average_price")).alias("buy_value"),
            (pl.col("quantity") * pl.col("price")).alias("current_value"),
            ((pl.col("price") / pl.col("average_price") - 1) * 100).alias("pct_change"),
        )

        holdings_df[list(self.holidings_schema.keys())].cast(self.holidings_schema)
        holdings_df = holdings_df.filter(pl.col("exchange") != "MCX")

        return holdings_df[list(self.holidings_schema.keys())].cast(self.holidings_schema)

    def ltp(self, exchange: str, tradingsymbol: str) -> float:
        """Get Last Traded Price for a symbol"""
        exchange = self.get_quantplay_exchange(exchange)
        tradingsymbol = self.get_quantplay_symbol(tradingsymbol)
        token = self.symbol_data[f"{exchange}:{tradingsymbol}"]["token"]

        instrument_token = self.token_converter(int(token), exchange)
        ltp = self.ltp_from_token(instrument_token)
        if ltp is None:
            raise InvalidArgumentException(
                f"LTP for {exchange} {tradingsymbol} is not available"
            )
        return float(ltp)

    def profile(self) -> UserBrokerProfileResponse:
        """Get user profile"""
        return {"user_id": self.user_id or ""}

    @retry(
        wait_exponential_multiplier=3000,
        wait_exponential_max=10000,
        stop_max_attempt_number=2,
        retry_on_exception=retry_exception,
    )
    def margins(self) -> MarginsResponse:
        """Get margin/limits information"""
        limits_resp = self.request(
            "limits", body={"seg": "ALL", "exch": "ALL", "prod": "ALL"}
        )

        if limits_resp is None:
            raise TokenException("Kotak V2 token expired, please generate a new token")

        response: MarginsResponse = {
            "margin_used": float(limits_resp["MarginUsed"]),
            "margin_available": float(limits_resp["Net"]),
            "total_balance": float(limits_resp["MarginUsed"]) + float(limits_resp["Net"]),
            "cash": 0,
        }
        if "CollateralValue" in limits_resp:
            response["cash"] = float(limits_resp["CollateralValue"])
        return response

    # **
    # ** POST/PUT Api's
    # **

    def place_order(
        self,
        tradingsymbol: str,
        exchange: ExchangeType,
        quantity: int,
        order_type: OrderTypeType,
        transaction_type: TransactionType,
        tag: str | None,
        product: ProductType,
        price: float,
        trigger_price: float | None = None,
    ) -> str | None:
        """Place a new order"""
        if tag:
            tag = tag + ":" + str(shortuuid.uuid())  # type:ignore
        else:
            tag = str(shortuuid.uuid())  # type:ignore

        place_order_body = {
            "am": "NO",
            "dq": "0",
            "es": self.get_exchange(exchange),
            "mp": "0",
            "pc": self.get_product(product),
            "pf": "N",
            "pr": str(price),
            "pt": self.get_order_type(order_type),
            "qt": str(quantity),
            "rt": "DAY",
            "tp": str(trigger_price or "0"),
            "ts": self.get_symbol(tradingsymbol, exchange),
            "tt": self.get_transaction_type(transaction_type),
            "ig": tag,
        }
        place_order_resp = self.request("place_order", body=place_order_body)

        if place_order_resp is None:
            raise QuantplayOrderPlacementException("Failed to place order on Kotak V2")

        if place_order_resp["stat"] == "Not_Ok":
            raise QuantplayOrderPlacementException(place_order_resp["errMsg"])

        return place_order_resp["nOrdNo"]

    def cancel_order(self, order_id: str, variety: str | None = None) -> None:
        """Cancel an order"""
        body = {"on": order_id, "am": "NO"}
        self.request("cancel_order", body=body)

    def exit_cover_order(self, order_id: str) -> None:
        """
        Exit a Cover Order (CO)
        Cover orders are special bracket orders with stop loss
        """
        body = {"on": order_id, "am": "NO"}
        self.request("exit_cover_order", body=body)

    def exit_bracket_order(self, order_id: str) -> None:
        """
        Exit a Bracket Order (BO)
        Bracket orders have both target and stop loss legs
        """
        body = {"on": order_id, "am": "NO"}
        self.request("exit_bracket_order", body=body)

    def modify_order(self, order: ModifyOrderRequest) -> str:
        """
        Modify an existing order

        Note: This implementation uses extended API fields not shown in basic
        Postman examples:
        - "tk" (token): Required for order identification
        - "dd" (disclosed quantity details): Set to "NA" for non-disclosed orders
        - "ig" (internal GUID/tag): Preserves original order tag
        - "vd" (validity): DAY validity instead of "rt" (retention type)

        These fields are required by the full V2 API for proper order modification.
        """
        order_id = order["order_id"]
        price = order.get("price")
        trigger_price = order.get("trigger_price", 0)
        if trigger_price is None:
            trigger_price = 0

        order_history = self.order_history(order_id).to_dicts()[-1]

        order_type = self.get_order_type(
            order.get("order_type", order_history["order_type"])
        )
        quantity = str(order.get("quantity", order_history["quantity"]))
        modify_order_request = {
            "tk": str(order_history["token"]),
            "mp": "0",
            "pc": order_history["product"],
            "dd": "NA",
            "dq": "0",
            "vd": "DAY",
            "ts": order_history["tradingsymbol"],
            "tt": order_history["transaction_type"],
            "pr": str(price),
            "tp": str(trigger_price),
            "qt": quantity,
            "no": order_id,
            "es": self.get_exchange(order_history["exchange"]),
            "pt": order_type,
            "ig": order_history["tag"],
        }

        try:
            Constants.logger.info(f"Modifying order [{order_id}] new price [{price}]")

            modify_order_response = self.request(
                "modify_order", body=modify_order_request
            )

            if modify_order_response is None:
                raise BrokerException("Failed to modify order on Kotak V2")

            return modify_order_response["nOrdNo"]

        except Exception as e:
            exception_message = (
                f"OrderModificationFailed for {order_id} failed with exception {e}"
            )
            if (
                "Order cannot be modified as it is being processed"
                not in exception_message
            ):
                Constants.logger.error(f"{exception_message}")

        return order_id

    def get_transaction_type(self, transaction_type: TransactionType) -> str:
        """Convert Quantplay transaction type to broker format"""
        transaction_type_map: dict[TransactionType, str] = {
            "BUY": "B",
            "SELL": "S",
        }
        return transaction_type_map.get(transaction_type, transaction_type)

    def get_order_type(self, order_type: OrderTypeType) -> str:
        """Convert Quantplay order type to broker format"""
        order_type_map: dict[OrderTypeType, str] = {
            "LIMIT": "L",
            "MARKET": "MKT",
            "SL": "SL",
            "SL-M": "SL-M",
        }
        return order_type_map.get(order_type, order_type)

    def get_quantplay_order_type(self, order_type: str) -> OrderTypeType:
        """Convert broker order type to Quantplay format"""
        order_type_map: dict[str, str] = {
            "L": "LIMIT",
            "MKT": "MARKET",
        }
        return order_type_map.get(order_type, order_type)  # type:ignore

    def get_quantplay_order_status(self, status: str) -> OrderStatusType:
        """Convert broker order status to Quantplay format"""
        if status in [
            "put order req received",
            "validation pending",
            "open pending",
            "modify pending",
            "modify validation pending",
            "modified",
        ]:
            return "OPEN"
        if status == "cancel pending":
            return "CANCELLED"
        status = status.upper()
        if status not in [
            "OPEN",
            "TRIGGER PENDING",
            "CANCELLED",
            "REJECTED",
            "COMPLETE",
        ]:
            Constants.logger.error(f"{status} not supported for Kotak V2")
            return "INVALID STATUS"  # type:ignore
        return status  # type:ignore

    def get_exchange(self, exchange: ExchangeType) -> str:
        """Convert Quantplay exchange to broker format"""
        exchange_segment_map: dict[ExchangeType, str] = {
            "NSE": "nse_cm",
            "BSE": "bse_cm",
            "NFO": "nse_fo",
            "BFO": "bse_fo",
            "CDS": "cde_fo",
            "BCD": "bcs-fo",
            "MCX": "mcx_fo",
        }
        return exchange_segment_map.get(exchange, exchange)

    def get_quantplay_exchange(self, exchange: str) -> ExchangeType:
        """Convert broker exchange to Quantplay format"""
        exchange_segment_map: dict[str, str] = {
            "nse_cm": "NSE",
            "bse_cm": "BSE",
            "nse_fo": "NFO",
            "bse_fo": "BFO",
            "cde_fo": "CDS",
            "mcx": "MCX",
        }
        return exchange_segment_map.get(exchange, exchange)  # type:ignore

    def get_lot_size(self, exchange: str, tradingsymbol: str):
        """Get lot size for a symbol"""
        tradingsymbol = self.get_quantplay_symbol(tradingsymbol)
        exchange = self.get_quantplay_exchange(exchange)

        try:
            return int(
                self.symbol_data["{}:{}".format(exchange, tradingsymbol)]["lot_size"]
            )
        except Exception as e:
            Constants.logger.error(
                "[GET_LOT_SIZE] unable to get lot size for {} {}".format(
                    exchange, tradingsymbol
                )
            )
            raise e

    def get_product(self, product: ProductType) -> str:
        """Convert Quantplay product to broker format"""
        product_map: dict[ProductType, str] = {
            "NRML": "NRML",
            "CNC": "CNC",
            "MIS": "MIS",
        }
        return product_map.get(product, product)

    def get_symbol(self, symbol: str, exchange: ExchangeType | None = None):
        """Convert Quantplay symbol to broker format"""
        if exchange in ["NSE", "nse_cm"]:
            if symbol in ["NIFTY", "BANKNIFTY"]:
                return symbol
            if "-EQ" not in symbol:
                return f"{symbol}-EQ"
            else:
                return symbol
        if exchange in ["BSE", "bse_cm"]:
            return symbol

        if symbol not in self.quantplay_symbol_map:
            return symbol
        return self.quantplay_symbol_map[symbol]

    # **
    # ** Kotak V2 Utils
    # **

    def request(
        self,
        item: Literal[
            "place_order",
            "cancel_order",
            "modify_order",
            "order_history",
            "order_book",
            "trade_report",
            "positions",
            "holdings",
            "margin",
            "scrip_master",
            "limits",
            "logout",
            "quotes",
            "exit_cover_order",
            "exit_bracket_order",
        ],
        params: dict[str, str | int | float] | None = None,
        body: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """
        Make API requests to Kotak V2 endpoints
        Uses dynamic baseUrl returned from MPIN validation
        """
        # V2 endpoint mappings - note the different paths
        url_map = {
            "place_order": ("quick/order/rule/ms/place", "POST", False),
            "cancel_order": ("quick/order/cancel", "POST", False),
            "modify_order": ("quick/order/vr/modify", "POST", False),
            "order_history": ("quick/order/history", "POST", False),
            "order_book": ("quick/user/orders", "GET", True),
            "trade_report": ("quick/user/trades", "GET", True),
            "positions": ("quick/user/positions", "GET", True),
            "holdings": ("portfolio/v1/holdings", "GET", True),
            "margin": (
                "quick/user/check-margin",
                "POST",
                False,
            ),  # Fixed: POST + urlencoded
            "scrip_master": ("script-details/1.0/masterscrip/file-paths", "GET", True),
            "limits": ("quick/user/limits", "POST", False),
            "logout": ("login/1.0/logout", "GET", True),
            "quotes": ("script-details/1.0/quotes/", "GET", True),
            "exit_cover_order": ("quick/order/co/exit", "POST", False),
            "exit_bracket_order": ("quick/order/bo/exit", "POST", False),
        }

        url, method, is_content_type_json = url_map[item]
        content_type = (
            "application/json"
            if is_content_type_json
            else "application/x-www-form-urlencoded"
        )

        # Use dynamic baseUrl for all APIs
        url = f"{self.base_url}/{url}"

        # V2 API uses different header structure
        # - No 'Authorization' header for order/reports APIs
        # - Plain token in 'Authorization' for quotes/scripmaster
        request_headers = {
            "Sid": self.configuration["Sid"],
            "Auth": self.configuration["Auth"],
            "neo-fin-key": "neotradeapi",
            "Content-Type": content_type,
        }

        # Add accept header for all except place_order
        if item != "place_order":
            request_headers["accept"] = "application/json"

        # Add Authorization header only for quotes and scripmaster
        if item in ["quotes", "scrip_master"]:
            request_headers["Authorization"] = self.configuration["access_token"]

        # sId (server ID) query parameter - required for routing requests to
        # correct server instance in Kotak's distributed architecture
        query_params = {"sId": self.configuration.get("hsServerId", "")}

        request_body = None

        if params is not None:
            request_params = urlencode({**params, **query_params})
        else:
            request_params = urlencode(query_params)

        # Prepare request body based on content type
        if body is not None:
            if content_type == "application/json":
                request_body = json.dumps(body)
            elif content_type == "application/x-www-form-urlencoded":
                # URL-encode the jData parameter
                request_body = urlencode({"jData": json.dumps(body)})

        resp = None
        resp_data = None

        if method == "GET":
            resp = requests.get(url=url, params=request_params, headers=request_headers)

        elif method == "POST":
            url += "?" + urlencode(query_params)

            resp = requests.post(
                url,
                headers=request_headers,
                data=request_body,  # type:ignore
            )

        if resp and resp.ok:
            resp_data = resp.json()

        if resp_data is None:
            if resp is not None:
                Constants.logger.error(resp.text)
                try:
                    response = json.loads(resp.text)

                    if "error" in response:
                        raise BrokerException(f"Kotak V2 Error : {response['error']}")

                    if "errMsg" in response:
                        raise BrokerException(f"Kotak V2 Error : {response['errMsg']}")
                except BrokerException:
                    raise
                except Exception:
                    raise BrokerException(
                        "Request Failed: No response from Kotak V2 server"
                    )
            else:
                raise BrokerException("Request Failed: No response from Kotak V2 server")

        return resp_data

    def event_handler_order_update(self, order: dict[str, Any]):
        """Handle order update events from WebSocket"""
        if "data" not in order:
            return
        data = json.loads(order["data"])
        if data["type"] != "order":
            return
        order = data["data"]
        if order["ordSt"] in [
            "put order req received",
            "validation pending",
            "modify pending",
            "modify validation pending",
            "modified",
            "not cancelled",
        ]:
            return

        quantplay_order: OrderUpdateEvent = {
            "placed_by": self.user_id,  # type:ignore
            "tradingsymbol": order["trdSym"],
            "exchange": self.get_quantplay_exchange(order["exSeg"]),
            "tag": order["GuiOrdId"],
            "order_id": order["nOrdNo"],
            "exchange_order_id": order["exOrdId"],
            "order_type": self.get_quantplay_order_type(order["prcTp"]),
            "price": float(order["prc"]),
            "quantity": int(order["qty"]),
            "product": order["prod"],
            "status": self.get_quantplay_order_status(order["ordSt"]),
        }

        if quantplay_order["exchange"] == "NSE":
            quantplay_order["tradingsymbol"] = quantplay_order["tradingsymbol"].replace(
                "-EQ", ""
            )

        quantplay_order["transaction_type"] = "BUY" if order["trnsTp"] == "B" else "SELL"
        if "trgPrc" in order:
            quantplay_order["trigger_price"] = float(order["trgPrc"])
        else:
            quantplay_order["trigger_price"] = None
        Constants.logger.info(f"Kotak V2 event {quantplay_order}")

        if self.order_updates:
            self.order_updates.put(quantplay_order)

    def stream_order_data(self) -> None:
        """Stream order updates via WebSocket"""
        ws = NeoWebSocket(
            sid=self.configuration.get("Sid", ""),
            token=self.configuration.get("Auth", ""),
            server_id=self.configuration.get("hsServerId", ""),
            data_center=self.configuration.get("dataCenter"),
            version="NEW",  # V2 always uses NEW version
        )
        ws.on_message = self.event_handler_order_update
        ws.on_error = lambda x: print(f"[KOTAK_V2_WS_ERROR]: {self.user_id} {x}")
        ws.on_close = lambda: print(f"[KOTAK_V2_WS_CLOSE]: {self.user_id}")
        ws.on_open = lambda: print(f"[KOTAK_V2_WS_OPEN]: {self.user_id}")

        ws.get_order_feed()
