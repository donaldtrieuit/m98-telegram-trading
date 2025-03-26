import logging
import time
from typing import Callable, Optional

from django.core.exceptions import ObjectDoesNotExist

from common.dto.order_dto import OrderDTO
from common.utils import remote_lock_util
from common.utils.encrypt_decrypt_util import MyFernet
from common.utils.exchanges.hyperliquid_util import HyperLiquidUtil
from trade_bot.dto.telegram_signal_dto import TradingSignal
from trade_bot.models import Bots, MyExchanges

my_fernet = MyFernet()
logger = logging.getLogger(__name__)


class BotLoggerAdapter(logging.LoggerAdapter):
    bot_id = None
    task_id = None

    def __init__(self, bot_id, task_id):
        super().__init__(logging.getLogger(task_id), {})
        self.bot_id = bot_id
        self.task_id = task_id

    def process(self, msg, kwargs):
        return f"[{self.bot_id}][{self.task_id}] {msg}", kwargs


class BotRunner:
    bot_id: int
    bot: Bots = None
    my_exchange: MyExchanges = None
    running: bool = False
    on_stop: Optional[Callable] = None

    def __init__(self, bot_id: int, bot_logger, file_logger):
        """Initialize BotRunner with bot ID."""
        self.bot_id = bot_id
        # init logger
        self.logger = bot_logger
        self.log_file = file_logger
        self._load_bot()
        self._initialize_exchange()

    def _load_bot(self) -> None:
        """Load bot and exchange data from database."""
        try:
            self.bot = Bots.objects.select_related('my_exchange').get(pk=self.bot_id)
            self.my_exchange = self.bot.my_exchange
            self.write_log(f"Initialized BotRunner for bot ID {self.bot_id}: {self.bot.name}")
        except ObjectDoesNotExist:
            self.write_log(f"Bot with ID {self.bot_id} does not exist", types='error')
            raise

    def _initialize_exchange(self) -> None:
        """Initialize exchange utility."""
        self.exchange_util = HyperLiquidUtil(self.my_exchange)

    def buy_coin(self, symbol: str, volume: float) -> Optional[OrderDTO]:
        """Execute buy order with validation."""
        self.write_log(f"Bot {self.bot_id}: buy volume {volume} for {symbol}", types='info')
        return None

    def check_to_buy_by_telegram_signal(self, telegram_signal: TradingSignal):
        self.write_log(f"Telegram signal: {telegram_signal.symbol} {telegram_signal.signal_type} - entry: {telegram_signal.entry_price} - tp: {telegram_signal.take_profit} - sl: {telegram_signal.stop_loss}")

    def sell_coin(self, symbol: str, volume: float) -> Optional[OrderDTO]:
        """Execute sell order with validation and delete CoinsBought record on success."""
        if volume <= 0:
            self.write_log(f"Bot {self.bot_id}: Invalid sell volume {volume} for {symbol}", types='warning')
            return None

        self.write_log(f"Bot {self.bot_id}: sell volume {volume} for {symbol}", types='info')
        return None

    def check_to_sell_by_telegram_signal(self, telegram_signal: TradingSignal):
        self.write_log(f"Telegram signal: {telegram_signal.symbol} {telegram_signal.signal_type} - entry: {telegram_signal.entry_price} - tp: {telegram_signal.take_profit} - sl: {telegram_signal.stop_loss}")

    def run(self):
        self.running = True
        while self.bot.status != 'off' and self.running:
            try:
                remote_lock_util.set_key(f"bot_{self.bot_id}", 60 + 30)
                time.sleep(30)
            except (Exception, Bots.DoesNotExist) as ex:
                logger.error(ex)
                break
            except Exception as ex:
                self.logger.error(ex)

        BotRunner.clear_logger(self.bot_id)
        if self.on_stop:
            self.on_stop(self.bot_id)

    def set_stopped_listener(self, func: Optional[Callable]):
        self.on_stop = func

    def stop(self):
        self.running = False

    def write_log(self, msg_origin, key_msg='', keys_format=None, types='info'):
        try:
            msg_format = msg_origin
            if keys_format:
                msg_format = msg_origin.format(**keys_format)
            msg = f"VolBot: [{self.bot_id}][{self.bot.name}] - {msg_format}"
            if types == "error":
                logger.error(msg)
            elif types == "warning":
                logger.warning(msg)
            else:
                logger.info(msg)
        except Exception as e:
            self.logger.error(e)

    @staticmethod
    def get_creation_bot_params(bot_id: int, task_id: Optional[str]):
        bot_logger = BotLoggerAdapter(bot_id, task_id)
        return {
            'bot_logger': bot_logger,
            'file_logger': None,
        }

    @staticmethod
    def clear_logger(bot_id):
        logger.info(f"Clear file logger VolBot {bot_id}")
        log_file = logging.getLogger(f"VolBot {bot_id}")
        for handler in log_file.handlers:
            handler.close()
        log_file.handlers.clear()
