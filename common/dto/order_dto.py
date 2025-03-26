from typing import Any, Optional

from pydantic import BaseModel


class OrderDTO(BaseModel):
    symbol: Optional[str] = None
    order_id: Any = None
    buy_price: float = 0
    sell_price: float = 0
    amount: float = 0
    filled: float = 0
    cost: float = 0
    fee_cost: float = 0
    fee_currency: Optional[str] = None
    profit: float = 0
    est: float = 0
    timestamp: Optional[float] = None
    leverage: int = 0
    margin_mode: Optional[str] = None
    position_side: str = 'long'
    side: str = 'buy'
    order_type: str = 'market'
    initial_margin: float = 0
    base_order: float = 0
    hedged: bool = False
