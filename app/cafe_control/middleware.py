import logging

from django.conf import settings
from django.http import HttpRequest, JsonResponse

logger = logging.getLogger(__name__)


class TokenRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        if request.path.startswith("/api/"):
            token = request.headers.get("Token")
            if not token:
                return JsonResponse({"detail": "Bad Request"}, status=400)
            if token != settings.API_TOKEN:
                return JsonResponse({"detail": "Bad Request"}, status=400)

        return self.get_response(request)  # Продолжаем обработку запроса
