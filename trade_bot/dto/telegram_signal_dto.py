from typing import Optional, Union

from pydantic import BaseModel


class TradingSignal(BaseModel):
    signal_type: str
    symbol: str
    side: str
    entry_price: Union[float, str]
    stop_loss: float
    take_profit: float
    leverage: int
    action_instructions: str
    additional_notes: str
    timestamp: Optional[str] = None
