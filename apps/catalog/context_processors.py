from .models import ExchangeRate


def exchange_rates(request):
    #? Provides exchange rates for all templates / Предоставляет курсы валют для всех шаблонов
    return {
        'exchange_rates': ExchangeRate.get_rates_dict(),
    }
