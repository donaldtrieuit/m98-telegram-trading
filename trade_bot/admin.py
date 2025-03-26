import logging

from django.conf.urls import url
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import re_path, reverse
from django.utils.html import format_html

from import_export import resources
from import_export.admin import ImportExportModelAdmin

from common.utils.encrypt_decrypt_util import MyFernet
from m98trading import settings
from trade_bot.forms import MyExchangesForm, TradingBotForm
from trade_bot.models import Bots, MyExchanges
from trade_bot.tasks import kill_task_running_bot, start_vol_bot

logger = logging.getLogger(__name__)
my_fernet = MyFernet()


class TradingBotResource(resources.ModelResource):
    class Meta:
        model = Bots


class MyExchangesResource(resources.ModelResource):
    class Meta:
        model = MyExchanges


class TradingBotManagementAdmin(ImportExportModelAdmin):
    resource_class = TradingBotResource
    form = TradingBotForm
    list_display = ['id', 'name', 'user', 'get_exchange', 'created', 'bot_actions']
    list_filter = ('name', 'user__username', 'my_exchange__name', 'status')
    readonly_fields = ["status", "task_id"]

    def get_exchange(self, obj):
        return obj.my_exchange.name

    get_exchange.short_description = 'Exchange'
    get_exchange.admin_order_field = 'exchange'

    def start_volbot_view(self, request, bot_id, *args, **kwargs):
        try:
            vol_bot = Bots.objects.get(pk=bot_id)
            # check bot type
            if vol_bot.status == 'off':
                vol_task = start_vol_bot.apply_async(args=[bot_id], queue=settings.BOT_QUEUE_NAME)
                logger.info("Start vol bot: {}".format(bot_id))

                vol_bot.status = 'on'
                vol_bot.task_id = vol_task
                vol_bot.save()
                logger.info("Started the bot: {}".format(bot_id))
                messages.success(request, 'Job id {} is started successfully!'.format(bot_id))
            else:
                vol_bot.status = 'on'
                vol_bot.save()
                messages.error(request, 'Job id {} had already started before!'.format(bot_id))
        except Exception as ex:
            messages.error(request, 'Error! Can not start job id {} - detail: {}.'.format(bot_id, ex))
            logger.error("start_volbot_view | {}".format(ex))
        return HttpResponseRedirect(reverse('admin:trade_bot_bots_changelist'))

    def stop_volbot_view(self, request, bot_id, *args, **kwargs):
        try:
            messages.success(request, 'Job id {} is stopped successfully!'.format(bot_id))
            vol_bot = Bots.objects.get(pk=bot_id)

            # stop single task
            async_result = kill_task_running_bot.apply_async(
                args=[vol_bot.id, vol_bot.task_id], queue=f"{settings.BOT_QUEUE_NAME}"
            )
            while not async_result.ready():
                import time
                time.sleep(1)

            # update vol bot info
            vol_bot.status = 'off'
            vol_bot.task_id = None
            vol_bot.save()
            # sell_all_coins.delay(bot_id)
            logger.info("Stoped the bot: {}".format(vol_bot.id))
        except Exception as ex:
            messages.error(request, 'Can not stop job {} - detail: {}'.format(bot_id, ex))
            logger.error("stop_volbot_view| {}".format(ex))
        return HttpResponseRedirect(reverse('admin:trade_bot_bots_changelist'))

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            url(
                r'^(?P<bot_id>.+)/vol/start/$',
                self.admin_site.admin_view(self.start_volbot_view),
                name='start-volbot',
            ),
            url(
                r'^(?P<bot_id>.+)/vol/stop/$',
                self.admin_site.admin_view(self.stop_volbot_view),
                name='stop-volbot',
            ),
        ]
        return custom_urls + urls

    def bot_actions(self, obj):
        if obj.status == 'off':
            return format_html(
                '<a class="button" href="{}">Run</a>',
                reverse('admin:start-volbot', args=[obj.pk])
            )
        elif obj.status == 'deleting':
            return None
        else:
            return format_html(
                '<a style="background-color:red; color:white" class="button" href="{}">Stop</a>',
                reverse('admin:stop-volbot', args=[obj.pk])
            )

    bot_actions.short_description = 'Actions'
    bot_actions.allow_tags = True


class CryptoExchangesManagementAdmin(ImportExportModelAdmin):
    resource_class = MyExchangesResource
    form = MyExchangesForm
    list_display = ['name', 'user', 'exchange', 'display_balance', 'status', 'created', 'my_exchange_action']
    list_filter = ('name', 'user', 'exchange')
    readonly_fields = ['exchange_balance']

    def display_balance(self, obj):
        return format_html("${}".format(obj.exchange_balance))
    display_balance.short_description = 'Balance'

    def refresh_crypto_exchange(self, request, crypto_exchange_id, *args, **kwargs):
        try:
            my_exchange = MyExchanges.objects.get(pk=crypto_exchange_id)
            my_exchange.exchange_balance = 1000
            my_exchange.save()
        except Exception as ex:
            logger.error("refresh_crypto_exchange| {}".format(ex))

        return HttpResponseRedirect(reverse('admin:settings_myexchanges_changelist'))

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            re_path(
                r'^(?P<crypto_exchange_id>.+)/cryptoexchange/refresh/$',
                self.admin_site.admin_view(self.refresh_crypto_exchange),
                name='refresh-cryptoexchange',
            ),
        ]
        return custom_urls + urls

    def my_exchange_action(self, obj):
        return format_html(
            '<a class="button" href="{}">Refresh</a>',
            reverse('admin:refresh-cryptoexchange', args=[obj.pk]),
        )

    my_exchange_action.short_description = 'Action'
    my_exchange_action.allow_tags = True


admin.site.register(Bots, TradingBotManagementAdmin)
admin.site.register(MyExchanges, CryptoExchangesManagementAdmin)
