import json
import logging
from urllib.request import urlopen
from urllib.error import URLError

logger = logging.getLogger(__name__)

# Free ip-api.com — no key required, 45 req/min limit from one IP
GEO_API_URL = 'http://ip-api.com/json/{}?fields=status,country,countryCode,city,lat,lon,query'


def detect_location(ip_address):
    #? Detect country and city from IP address / Определяет страну и город по IP
    #? Uses ip-api.com (free, no key) / Использует ip-api.com (бесплатно, без ключа)
    #? Cached in session to avoid repeated API calls / Кэшируется в сессии

    if not ip_address or ip_address in ('127.0.0.1', '::1', 'localhost'):
        return {
            'country': None,
            'country_code': None,
            'city': None,
            'lat': None,
            'lon': None,
        }

    # For private/local IPs, return empty
    if ip_address.startswith(('192.168.', '10.', '172.')):
        return {
            'country': None,
            'country_code': None,
            'city': None,
            'lat': None,
            'lon': None,
        }

    try:
        url = GEO_API_URL.format(ip_address)
        with urlopen(url, timeout=3) as resp:
            data = json.loads(resp.read().decode())

        if data.get('status') == 'success':
            return {
                'country': data.get('country'),
                'country_code': data.get('countryCode'),
                'city': data.get('city'),
                'lat': data.get('lat'),
                'lon': data.get('lon'),
            }
        else:
            logger.warning('GeoIP lookup failed for %s: %s', ip_address, data.get('message', 'unknown'))
    except (URLError, json.JSONDecodeError, OSError) as e:
        logger.warning('GeoIP error for %s: %s', ip_address, e)

    return {
        'country': None,
        'country_code': None,
        'city': None,
        'lat': None,
        'lon': None,
    }
