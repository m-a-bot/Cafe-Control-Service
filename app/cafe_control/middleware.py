from django.conf import settings
from django.http import HttpResponseBadRequest, JsonResponse


class TokenRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/api/"):

            token = request.headers.get("Token")
            if not token:
                return HttpResponseBadRequest()
            if token != settings.API_TOKEN:
                return HttpResponseBadRequest()

        return self.get_response(request)  # Продолжаем обработку запроса
