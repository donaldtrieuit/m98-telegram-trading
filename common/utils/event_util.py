from django.utils.translation import ugettext_lazy as _


class Event:
    BOT_CREATED = _('BOT_CREATED')
    BOT_STARTED = _('BOT_STARTED')
    BOT_STOPPED = _('BOT_STOPPED')
    BOT_DELETED = _('BOT_DELETED')
    BOT_ORDER_OK = _('BOT_ORDER_OK')
    BOT_ORDER_FAIL = _('BOT_ORDER_FAIL')
    BOT_TRACKING = _('BOT_TRACKING')
    BOT_CLOSE_ORDER = _('BOT_CLOSE_ORDER')


class Description:
    REACHED_TAKE_PROFIT = _('Reached total take profit')
    REACHED_STOP_LOSS = _('Reached total stop loss')
    REACHED_LIMIT_TOTAL_TRADING = _('Reached limit total trading')
    EXCHANGE_KEY_EXPIRED = _('Invalid API key')
    SUBSCRIPTION_EXPIRED = _('Subscription expired')
    EXCHANGE_NO_PERMISSION = _('No access or insufficient permissions')
    BOT_STARTED = _('The bot was started')
    BOT_STOPPED = _('The bot was stopped')
    BOT_CREATED = _('The bot was created')


class LevelEvent:
    INFO = _('info')
    WARNING = _('warning')
    ERROR = _('error')
