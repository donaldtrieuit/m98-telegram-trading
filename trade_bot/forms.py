from django import forms

from common.utils.encrypt_decrypt_util import MyFernet
from trade_bot.models import Bots, MyExchanges

my_fernet = MyFernet()


class TradingBotForm(forms.ModelForm):
    class Meta:
        model = Bots
        exclude = ('status', 'task_id')


class MyExchangesForm(forms.ModelForm):
    class Meta:
        model = MyExchanges
        exclude = ('status', 'restrictions', 'latest_updated', 'api_key', 'api_password', 'exchange')

    def clean(self):
        if self.instance and not self.instance.pk:
            self.cleaned_data['status'] = 'authenticated'
            self.cleaned_data['api_secret'] = my_fernet.encrypt_data(self.cleaned_data['api_secret'])
        else:
            api_secret = self.cleaned_data.get('api_secret', self.instance.api_secret)
            if api_secret != self.instance.api_secret:
                self.cleaned_data['api_secret'] = my_fernet.encrypt_data(self.cleaned_data['api_secret'])
        exchange_balance = self.process_data(self.cleaned_data)
        self.cleaned_data['exchange_balance'] = exchange_balance
        return self.cleaned_data

    def process_data(self, validated_data):
        exchange_code = validated_data.get('exchange', None)
        api_secret = validated_data.get('api_secret', None)
        wallet_address = validated_data.get('wallet_address', None)
        if exchange_code == 'hyper_liquid':
            if api_secret is None:
                raise forms.ValidationError({"api_secret": "Field api_secret is required!"})
            elif wallet_address is None:
                raise forms.ValidationError({"wallet_address": "Field wallet_address is required!"})
        return 1000

    def save(self, commit=True):
        self.instance.status = self.cleaned_data.get('status', self.instance.status)
        self.instance.restrictions = self.cleaned_data.get('restrictions', self.instance.restrictions)
        self.instance.exchange_balance = self.cleaned_data.get('exchange_balance', self.instance.exchange_balance)
        return super(MyExchangesForm, self).save(commit)
