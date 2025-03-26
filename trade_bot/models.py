from django.contrib.auth.models import User
from django.db import models

from django_extensions.db.models import TimeStampedModel

from common.utils.encrypt_decrypt_util import MyFernet

my_fernet = MyFernet()

EXCHANGES_LIST = [
    ('binance', 'Binance'),
]

AUTHENTICATION = [
    ('authenticated', 'Authenticated'),
    ('unauthenticated', 'Unauthenticated'),
]

BOT_STATUS_LIST = [
    ('on', 'ON'),
    ('off', 'OFF'),
    ('deleting', 'DELETING'),
]

MARGIN_MODE = [
    ('isolated', 'Isolated'),
    ('cross', 'Cross')
]

POSITION_SIDE = [
    ('long', 'Long'),
    ('short', 'Short'),
    ('both', 'Both'),
]

SIDE_LIST = [
    ('buy', 'Buy'),
    ('sell', 'Sell')
]

TYPE_EVENT = [
    ('warning', 'WARNING'),
    ('error', 'ERROR'),
    ('info', 'INFO'),
]


class MyExchanges(TimeStampedModel, models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='crypto_exchange', verbose_name='User')
    exchange = models.CharField(max_length=64,
                                choices=EXCHANGES_LIST, null=False, blank=False, default="hyper_liquid", verbose_name='Exchange')
    exchange_balance = models.FloatField(default=0.0, null=False, blank=False, verbose_name='Exchange Balance')
    name = models.CharField(max_length=128, null=False, blank=False, default="", verbose_name='Exchange Name')
    api_key = models.CharField(max_length=300, null=True, blank=True, default="", verbose_name='API key')
    api_secret = models.CharField(max_length=300, null=True, blank=True, default="", verbose_name='API Secret')
    api_password = models.CharField(max_length=300, null=True, blank=True, default="", verbose_name='API Password')
    wallet_address = models.CharField(max_length=300, null=True, blank=True, default="", verbose_name='Wallet Address')
    latest_updated = models.DateTimeField(null=True, blank=True, verbose_name='Latest Updated')
    status = models.CharField(max_length=64,
                              choices=AUTHENTICATION, null=False, blank=False, default="unauthenticated",
                              verbose_name='Status')
    restrictions = models.TextField(blank=True, null=True, verbose_name='Restrictions')

    class Meta:
        unique_together = ('user', 'exchange', 'name', 'api_password', 'wallet_address')
        verbose_name = 'My Exchanges'
        verbose_name_plural = 'My Exchanges'
        ordering = ['-created']

        indexes = [
            models.Index(fields=['api_key', ]),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return f'{self.name}'


class Bots(TimeStampedModel, models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             null=False, blank=False, related_name='trade_bots', verbose_name='User')
    name = models.CharField(max_length=250, blank=False,
                            null=False, default='', verbose_name='Bot Name')
    status = models.CharField(max_length=32, blank=False,
                              null=False, default="off", choices=BOT_STATUS_LIST, verbose_name='Status')
    my_exchange = models.ForeignKey(MyExchanges, on_delete=models.CASCADE,
                                    blank=False, null=False, help_text='Select your exchange credential',
                                    verbose_name='My Exchange')
    telegram_channel = models.CharField(max_length=250, blank=False, null=False, default='', verbose_name='Telegram Channel')
    task_id = models.CharField(max_length=512, null=True, blank=True, verbose_name='Task Id')

    def __str__(self):
        return '{}-{}'.format(self.id, self.name)

    class Meta:
        verbose_name = 'Bots'
        verbose_name_plural = 'Bots'
        ordering = ['-created']
        unique_together = ['user', 'name']

        indexes = [
            models.Index(fields=['name', ]),
        ]
