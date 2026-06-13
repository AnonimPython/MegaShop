from .geoip import detect_location


def geo_location(request):
    #? Detects user location from IP and caches in session / Определяет местоположение по IP и кэширует в сессии
    geo = request.session.get('geo_location')
    if not geo:
        ip = request.META.get('REMOTE_ADDR', '')
        # If behind a proxy, check for forwarded IP
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
        if forwarded:
            ip = forwarded.split(',')[0].strip()
        geo = detect_location(ip)
        request.session['geo_location'] = geo

    # Suggest store matching detected city / Предложить магазин в городе пользователя
    suggested_store = None
    if geo and geo.get('city'):
        from apps.stores.models import Store
        city_lower = geo['city'].lower()
        match = Store.objects.filter(is_active=True, city__icontains=city_lower).first()
        suggested_store = match

    return {'geo_location': geo, 'suggested_store': suggested_store}
