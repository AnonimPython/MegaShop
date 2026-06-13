from django import template
from django.template.defaultfilters import floatformat
from ..models import ExchangeRate

register = template.Library()


@register.filter
def to_currency(value, arg):
    #? Converts USD price to given currency and returns formatted: $1,234.56 / Конвертирует USD в указанную валюту
    try:
        currency_code = arg.upper()
        rates = ExchangeRate.get_rates_dict()
        rate_info = rates.get(currency_code)
        if not rate_info:
            return f'${value}'
        rate = rate_info['rate']
        symbol = rate_info['symbol']
        converted = float(value) * float(rate)
        return f'{symbol}{converted:,.2f}'
    except (TypeError, ValueError, AttributeError):
        return str(value)


@register.filter
def usd_format(value):
    #? Formats USD price with $ symbol / Форматирует цену в USD с символом $
    try:
        return f'${float(value):,.2f}'
    except (TypeError, ValueError):
        return str(value)
