#? Passes store list and selected store to all templates / Передаёт список магазинов и выбранный магазин во все шаблоны
from .models import Store


def stores(request):
    #* Available in all templates as {{ stores }} and {{ current_store }} / Доступен во всех шаблонах как {{ stores }} и {{ current_store }}
    stores_qs = Store.objects.filter(is_active=True)
    current_store = None
    store_id = request.session.get('store_id')

    if store_id:
        try:
            current_store = stores_qs.get(id=store_id)
        except Store.DoesNotExist:
            current_store = None

    return {
        'stores': stores_qs,
        'current_store': current_store,
    }
