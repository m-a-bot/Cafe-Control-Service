import json
import logging

import requests
from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from .forms import FilterQueryParamsForm, SearchQueryParamsForm

logger = logging.getLogger(__name__)


# Create your views here.
class HomePageView(TemplateView):
    template_name = "cafe_app/index.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        total_order_price_url = request.build_absolute_uri(
            reverse(f"total-order-price-api")
        )

        headers = {
            "Content-Type": "application/json",
            "Token": settings.API_TOKEN,
        }

        response = requests.get(total_order_price_url, headers=headers)

        if response.status_code == 200:
            total_price = response.json()["total_price"]
        else:
            total_price = 0
            logger.error(f"Error with API: {response.status_code}")

        response = requests.get(
            total_order_price_url,
            headers=headers,
            params={"status": "is_paid"},
        )

        if response.status_code == 200:
            total_is_paid_price = response.json()["total_price"]
        else:
            total_is_paid_price = 0
            logger.error(f"Error with API: {response.status_code}")

        context.update(
            {
                "total_price": total_price,
                "total_is_paid_price": total_is_paid_price,
            }
        )

        return self.render_to_response(context)


class OrdersPageView(TemplateView):
    template_name = "cafe_app/orders.html"


class OrdersTemplatePageView(TemplateView):
    template_name = "cafe_app/orders_template.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        headers = {
            "Content-Type": "application/json",
            "Token": settings.API_TOKEN,
        }

        params = request.GET.dict()

        orders_api_url = request.build_absolute_uri(reverse("orders-api"))

        filtered_orders_api_url = request.build_absolute_uri(
            reverse("filtered-orders-api")
        )

        search_query_params = SearchQueryParamsForm(params)

        filter_params = FilterQueryParamsForm(params)

        if filter_params.is_valid():
            response = requests.get(
                filtered_orders_api_url,
                headers=headers,
                params=filter_params.data,
            )
        else:
            response = requests.get(
                orders_api_url,
                headers=headers,
                params=search_query_params.data,
            )

        # logger.info(response.json())

        if response.status_code == 200:
            orders = response.json().get("orders", [])
        else:
            orders = []
            logger.error(f"Error with API: {response.status_code}")

        if orders:
            orders.sort(key=lambda x: (x["status"], float(x["total_price"])))

        context["orders"] = orders

        return self.render_to_response(context)


class OrderPageView(TemplateView):
    template_name = "cafe_app/order_detail.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        id = kwargs.get("id")

        context.update({"order_id": id, "Token": settings.API_TOKEN})

        return self.render_to_response(context)


class OrderTemplatePageView(TemplateView):
    template_name = "cafe_app/order_template.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        id = kwargs.get("id")

        order_detail_api_url = request.build_absolute_uri(
            reverse(f"order-detail-api", kwargs={"id": id})
        )

        headers = {
            "Content-Type": "application/json",
            "Token": settings.API_TOKEN,
        }

        response = requests.get(order_detail_api_url, headers=headers)

        if response.status_code == 200:
            order = response.json()
        else:
            order = {}
            logger.error(f"Error with API: {response.status_code}")

        items_api_url = request.build_absolute_uri(reverse(f"items-api"))

        response = requests.get(items_api_url, headers=headers)

        if response.status_code == 200:
            items = response.json()["items"]
        else:
            items = []
            logger.error(f"Error with API: {response.status_code}")

        # logger.debug(order_items)
        #
        items.sort(key=lambda x: float(x.get("price")))

        if order:
            order["items"].sort(key=lambda x: float(x.get("items_price")))

        # order = {}
        # items = []

        context.update(
            {"order": order, "items": items, "Token": settings.API_TOKEN}
        )

        return self.render_to_response(context)


@method_decorator(csrf_exempt, name="dispatch")
class ClearLocalOrderPageView(View):
    def post(self, request: HttpRequest, *args, **kwargs):
        name_order_items = "order_items"

        if name_order_items in request.session:
            request.session[name_order_items] = {}
        return JsonResponse({"success": True})


@method_decorator(csrf_exempt, name="dispatch")
class ChangeLocalOrderPageView(View):
    def post(self, request: HttpRequest, *args, **kwargs):
        data = json.loads(request.body)
        item_id = str(data.get("item_id"))
        quantityChange = int(data.get("quantity_change", 0))

        order_items = request.session.get("order_items", {})

        logger.info(order_items)

        logger.info(item_id in order_items)

        if item_id in order_items:
            order_items[item_id] += quantityChange
        else:
            order_items[item_id] = quantityChange

        if order_items[item_id] <= 0:
            del order_items[item_id]

        request.session["order_items"] = order_items
        request.session.modified = True

        return JsonResponse({"detail": "success", "order_items": order_items})


@method_decorator(csrf_exempt, name="dispatch")
class CreateOrderPageView(TemplateView):
    template_name = "cafe_app/create_order.html"

    def get(self, request, *args, **kwargs):
        order_items = request.session.get("order_items", {})

        context = self.get_context_data(**kwargs)

        items_api_url = request.build_absolute_uri(reverse(f"items-api"))

        headers = {
            "Content-Type": "application/json",
            "Token": settings.API_TOKEN,
        }

        response = requests.get(items_api_url, headers=headers)

        if response.status_code == 200:
            items = response.json()["items"]
        else:
            items = []
            logger.error(f"Error with API: {response.status_code}")
        #
        items.sort(key=lambda x: int(x.get("id")))

        total_price = 0

        for item in items:
            item_id = str(item["id"])
            if item_id in order_items:
                total_price += float(item["price"]) * order_items[item_id]

        context.update(
            {
                "items": items,
                "order_items": order_items,
                "total_price": total_price,
            }
        )

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        numberTable = data["numberTable"]

        order_items = request.session.get("order_items", {})

        item_ids = list()

        for item_id, value in order_items.items():
            for _ in range(value):
                item_ids.append(int(item_id))

        orders_api_url = request.build_absolute_uri(reverse(f"orders-api"))

        headers = {
            "Content-Type": "application/json",
            "Token": settings.API_TOKEN,
        }

        response = requests.post(
            orders_api_url,
            headers=headers,
            data=json.dumps({"table_number": numberTable, "items": item_ids}),
        )

        if response.status_code == 201:
            redirect_url = request.build_absolute_uri(
                reverse("order-detail", args=[response.json()["order_id"]])
            )
            return JsonResponse(
                {"success": True, "redirect_url": redirect_url}
            )
        else:
            return JsonResponse({"success": False})


class DeleteOrderPageView(TemplateView):
    template_name = "cafe_app/delete_order.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        id = 0

        context.update({"order_id": id, "Token": settings.API_TOKEN})

        return self.render_to_response(context)


class SearchOrdersPageView(TemplateView):
    template_name = "cafe_app/search-orders.html"
