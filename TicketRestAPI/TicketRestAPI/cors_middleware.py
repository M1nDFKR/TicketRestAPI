from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse

class CorsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.method == 'OPTIONS' and 'HTTP_ACCESS_CONTROL_REQUEST_METHOD' in request.META:
            response = HttpResponse()
            response['Content-Length'] = '0'
            response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
            response['Access-Control-Allow-Methods'] = request.META.get('HTTP_ACCESS_CONTROL_REQUEST_METHOD', 'POST, GET, OPTIONS')
            response['Access-Control-Allow-Headers'] = request.META.get('HTTP_ACCESS_CONTROL_REQUEST_HEADERS', 'Authorization')
            return response
        return None
