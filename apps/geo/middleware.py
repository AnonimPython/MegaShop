from loguru import logger


class RequestLoggingMiddleware:
    #? Logs every request with status, method, path, and duration / Логирует каждый запрос
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        import time
        start = time.time()
        response = self.get_response(request)
        duration = time.time() - start
        if request.path.startswith('/static/') or request.path.startswith('/favicon'):
            return response
        logger.debug('{} {} → {} ({:.0f}ms)', request.method, request.path,
                      response.status_code, duration * 1000)
        return response
