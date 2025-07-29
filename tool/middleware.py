import time

import structlog
from django.utils.deprecation import MiddlewareMixin

log = structlog.get_logger()


class LoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request._start_time = time.time()

    def process_response(self, request, response):
        duration = int((time.time() - getattr(request, '_start_time', time.time())) * 1000)
        log.info('http_request', method=request.method, path=request.get_full_path(), status=response.status_code,
                 duration_ms=duration, user=getattr(request.user, 'username', None))
        return response
