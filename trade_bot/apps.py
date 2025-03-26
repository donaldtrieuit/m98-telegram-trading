from django.apps import AppConfig


class TradeBotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'trade_bot'

    def ready(self):
        import trade_bot.signals  # noqa
