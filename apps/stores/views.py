#? Store selection, context data for templates / Выбор магазина, контекстные данные для шаблонов
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from loguru import logger


@require_POST
def set_current_store(request):
    #* Saves selected store to session / Сохраняет выбранный магазин в сессию
    store_id = request.POST.get('store_id', '')
    if store_id:
        request.session['store_id'] = int(store_id)
        logger.debug('Store switched: → store_id={}', store_id)
    else:
        request.session.pop('store_id', None)
        logger.debug('Store cleared')
    return redirect(request.POST.get('next', '/'))
