import logging
from typing import Dict, Optional, Tuple

from common.utils.queue.broker_factory import BrokerFactory
from trade_bot.bots.bot_runner import BotRunner
from trade_bot.data.telegram_signal_publisher import TelegramSignalPublisher
from trade_bot.data.telegram_signal_subscriber import TelegramSignalSubscriber
from trade_bot.dto.telegram_signal_dto import TradingSignal
from trade_bot.models import Bots

logger = logging.getLogger(__name__)
running_bots: Dict[int, BotRunner] = {}
init_consumers: bool = False


def _validate_signal(signal: TradingSignal) -> Tuple[Optional[TradingSignal], Optional[str]]:
    if signal.signal_type.lower() not in ['buy_signal', 'sell_signal']:
        return None, "Not support signal type"

    if not signal.symbol or len(signal.symbol.split('/')) != 2:
        return None, "Invalid symbol"

    if signal.side.lower() not in ['spot', 'long', 'short']:
        return None, "Invalid side"

    if signal.signal_type.lower() == 'buy_signal' and signal.entry_price != 'CMP' and not f"{signal.entry_price}".replace('.', '').isdigit():
        return None, "Invalid entry price"

    if signal.entry_price != 'CMP':
        try:
            signal.entry_price = float(signal.entry_price)
        except Exception as e:
            logger.warning(e)
            signal.entry_price = 0

    if signal.signal_type.lower() != 'buy_signal':
        return signal, None

    if signal.side.lower() == 'long':
        if signal.entry_price != 'CMP' and signal.stop_loss and signal.entry_price <= signal.stop_loss:
            return None, "Invalid stop loss"
        if signal.entry_price != 'CMP' and signal.take_profit and signal.entry_price >= signal.take_profit:
            return None, "Invalid take profit"

    if signal.side.lower() == 'short':
        if signal.entry_price != 'CMP' and signal.stop_loss and signal.entry_price >= signal.stop_loss:
            return None, "Invalid stop loss"
        if signal.entry_price != 'CMP' and signal.take_profit and signal.entry_price <= signal.take_profit:
            return None, "Invalid take profit"

    return signal, None


def _on_telegram_signal(channel_id: str, signal: TradingSignal, date: str):
    for bot_id in running_bots:
        bot_runner = running_bots[bot_id]
        valid_channels = [bot_runner.bot.telegram_channel]
        if bot_runner.bot.telegram_channel and bot_runner.bot.telegram_channel.replace('-', '').isdigit():
            valid_channels = [
                f"{abs(int(bot_runner.bot.telegram_channel))}",
                f"-{abs(int(bot_runner.bot.telegram_channel))}",
                f"100{abs(int(bot_runner.bot.telegram_channel))}",
                f"-100{abs(int(bot_runner.bot.telegram_channel))}",
            ]

        if channel_id not in valid_channels:
            continue

        valid_signal, error_msg = _validate_signal(signal)
        if not valid_signal:
            bot_runner.write_log(error_msg)
        elif signal.signal_type == "buy_signal":
            bot_runner.check_to_buy_by_telegram_signal(signal)
        elif signal.signal_type == "sell_signal":
            bot_runner.check_to_sell_by_telegram_signal(signal)


def start_bot_runner(bot: Bots, task_id: str):
    global running_bots, init_consumers

    if not init_consumers:
        init_consumers = True
        TelegramSignalSubscriber(BrokerFactory.get_broker()).subscribe(_on_telegram_signal)

    if bot.id in running_bots and running_bots[bot.id].running:
        logger.info(f"bot {bot.id} is already running")
        return

    TelegramSignalPublisher(BrokerFactory.get_broker()).publish(
        bot.id,
        bot.telegram_channel,
        "subscribe"
    )
    bot.task_id = task_id
    bot_runner = BotRunner(bot_id=bot.id, **BotRunner.get_creation_bot_params(bot.id, task_id))
    bot_runner.set_stopped_listener(_on_bot_stopped)
    bot_runner.run()
    bot_runner.write_log(f'Bot {bot.id} started.')
    running_bots[bot.id] = bot_runner


def stop_running_bot(bot_id: int) -> bool:
    global running_bots
    if bot_id in running_bots:
        bot_runner = running_bots[bot_id]
        bot_runner.set_stopped_listener(None)
        bot_runner.stop()
        del running_bots[bot_id]
        bot_runner.write_log(f'Bot {bot_id} stopped.')
        return True
    return False


def _on_bot_stopped(bot_id: int):
    global running_bots
    if bot_id in running_bots:
        bot = running_bots[bot_id].bot
        bot.task_id = None
        bot.status = 'off'
        bot.save()
        del running_bots[bot_id]
