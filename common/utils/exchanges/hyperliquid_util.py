import logging
import traceback
from datetime import datetime
from typing import Any, Dict, Optional

import eth_account
from eth_account.signers.local import LocalAccount
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants

from common.dto.order_dto import OrderDTO
from common.utils.encrypt_decrypt_util import MyFernet

my_fernet = MyFernet()
logger = logging.getLogger(__name__)


class HyperLiquidUtil:
    def __init__(self, my_exchange):
        account: LocalAccount = eth_account.Account.from_key(my_fernet.decrypt_data(my_exchange.api_secret))
        self.address = my_fernet.decrypt_data(my_exchange.wallet_address)
        self.info = Info(constants.MAINNET_API_URL, True)
        self.user_state = self.info.user_state(self.address)
        self.meta_data = self.info.meta()['universe']
        self.exchange = Exchange(
            wallet=account, base_url=constants.MAINNET_API_URL, account_address=self.address
        )

    def fetch_balance(self) -> (float, str):
        account_balance = 0
        status = 'success'
        try:
            self.user_state = self.info.user_state(self.address)
            account_balance = float(self.user_state['marginSummary']['accountValue'])
        except Exception as ex:
            logger.warning(ex)
            status = 'error'
        return account_balance, status

    def set_leverage(self, symbol: str, margin_mode: str, leverage: int) -> Any:
        return self.exchange.update_leverage(leverage, symbol, margin_mode == "cross")

    def get_price(self, symbol: str) -> float:
        return float(self.info.l2_snapshot(symbol)["levels"][0][0]["px"])

    def get_decimal_value(self, coin_name):
        """Get decimal precision for a coin."""
        for item in self.meta_data:
            if item['name'] == coin_name:
                return int(item['szDecimals'])
        logger.warning(f"No decimal value found for coin: {coin_name}")
        return 4

    def create_buy_order(self, coin, volume, leverage, position_side) -> [Optional[OrderDTO], str, str]:
        order_info = None
        try:
            decimals = self.get_decimal_value(coin)
            amount = round(volume, decimals)
            order_result = self.exchange.market_open(
                coin, position_side == 'long', amount, None, 0.01
            )
            logger.info(f'buy order info: {order_result}')
            if order_result is None:
                return None, "error", "Exchange returned no response"

            if order_result["status"] != "ok":
                return None, "error", order_result.get("response", "Place Order Failed")

            for status in order_result["response"]["data"]["statuses"]:
                if "error" in status:
                    return order_info, "error", status["error"]
                filled = status["filled"]
                cost = float(filled["totalSz"]) * float(filled["avgPx"])
                initial_margin = cost / leverage
                order_info = OrderDTO(**{
                    'symbol': coin,
                    'side': 'buy',
                    "order_id": filled["oid"],
                    "buy_price": filled["avgPx"],
                    "amount": volume,
                    "filled": filled["totalSz"],
                    "cost": cost,
                    'leverage': leverage,
                    'position_side': position_side,
                    'initial_margin': initial_margin,
                    "timestamp": datetime.now().timestamp(),
                })
                order_response = self.fetch_order(filled['oid'])
                if order_response:
                    order_info.fee_cost = order_response["fee"]
                    order_info.fee_currency = order_response["feeToken"]
                    order_info.margin_mode = 'cross' if order_response["crossed"] else 'isolated'
                    order_info.timestamp = order_response["time"]
            return order_info, 'success', ""
        except Exception as ex:
            print(traceback.print_exc())
            return None, "error", str(ex)

    def create_sell_order(self, coin, volume, leverage, margin_mode, position_side) -> [Optional[OrderDTO], str, str]:
        order_info = None
        try:
            decimals = self.get_decimal_value(coin)
            amount = round(volume, decimals)
            order_result = self.exchange.market_close(
                coin, amount, None, 0.01
            )
            logger.info(f'sell order info: {order_result}')
            if order_result is None:
                return None, "error", "Exchange returned no response"

            if order_result["status"] != "ok":
                return None, "error", order_result.get("response", "Place Order Failed")

            for status in order_result["response"]["data"]["statuses"]:
                if "error" in status:
                    return order_info, "error", status["error"]
                filled = status["filled"]
                cost = float(filled["totalSz"]) * float(filled["avgPx"])
                initial_margin = cost / leverage
                order_info = OrderDTO(**{
                    'symbol': coin,
                    "order_id": filled["oid"],
                    "sell_price": filled["avgPx"],
                    "amount": filled["totalSz"],
                    "filled": filled["totalSz"],
                    "cost": cost,
                    'leverage': leverage,
                    'margin_mode': margin_mode,
                    'position_side': position_side,
                    'initial_margin': initial_margin,
                    "timestamp": datetime.now().timestamp(),
                })
                order_response = self.fetch_order(filled['oid'])
                if order_response:
                    order_info.fee_cost = order_response["fee"]
                    order_info.fee_currency = order_response["feeToken"]
                    order_info.margin_mode = 'cross' if order_response["crossed"] else 'isolated'
                    order_info.est = order_response["closedPnl"]
                    order_info.timestamp = order_response["time"]
            return order_info, 'success', ""
        except Exception as ex:
            print(traceback.print_exc())
            return None, "error", str(ex)

    def fetch_order(self, order_id: int) -> Optional[Dict[str, Any]]:
        orders = self.info.user_fills(self.address)
        for order in orders:
            if order["oid"] == order_id:
                return order
        return None
