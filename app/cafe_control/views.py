import json
import logging

from django import http, views
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .forms import (
    FilterQueryParamsForm,
    InfoItemForm,
    InfoOrderForm,
    SearchQueryParamsForm,
    StatusOrderForm,
)
from .models import Item, Order, OrderItem

logger = logging.getLogger(__name__)


def find_total_price(order_id: int):
    order = Order.objects.get(id=order_id)
    price_data = OrderItem.objects.filter(order=order).aggregate(
        total=Sum("items_price")
    )
    order.total_price = price_data["total"] or 0
    order.save(update_fields=["total_price"])


def add_items_to_order(order_id: int, item_ids: list[int], update=False):

    if update:
        OrderItem.objects.filter(order_id=order_id).delete()

    for item_id in item_ids:

        order_item, created = OrderItem.objects.get_or_create(
            order_id=order_id, item_id=item_id
        )

        if not created:
            order_item.quantity += 1
        else:
            order_item.quantity = 1

        order_item.items_price = order_item.quantity * order_item.item.price
        order_item.save(update_fields=["quantity", "items_price"])

    find_total_price(order_id)

    return JsonResponse({"detail": "Items was added to order"})


def remove_items_from_order(order_id: int, item_ids: list[int]):

    for item_id in item_ids:
        try:
            order_item = OrderItem.objects.get(
                order_id=order_id, item_id=item_id
            )
        except OrderItem.DoesNotExist:
            continue

        if order_item.quantity > 1:
            order_item.quantity -= 1
            order_item.items_price = (
                order_item.quantity * order_item.item.price
            )
            order_item.save(update_fields=["quantity", "items_price"])
        else:
            order_item.delete()

    find_total_price(order_id)

    return JsonResponse({"detail": "Items was removed from order"})


@method_decorator(csrf_exempt, name="dispatch")
class OrderView(views.View):

    # ok
    def get(self, request: http.HttpRequest, id: int) -> HttpResponse:

        try:
            order = Order.objects.get(id=id)
            items_data = []
            for order_item in order.orderitem_set.all():
                items_data.append(
                    {
                        "item_id": order_item.item.id,
                        "item_name": order_item.item.name,
                        "quantity": order_item.quantity,
                        "items_price": order_item.items_price,
                    }
                )
        except ObjectDoesNotExist:
            return JsonResponse(
                {
                    "detail": "Order does not exist",
                },
                status=404,
            )
        order_data = {
            "id": order.id,
            "table_number": order.table_number,
            "items": items_data,
            "total_price": order.total_price,
            "status": order.status,
        }

        return JsonResponse(order_data)

    def put(self, request: http.HttpRequest, id: int) -> HttpResponse:
        info_order = InfoOrderForm(json.loads(request.body))
        if not info_order.is_valid():
            return http.HttpResponseBadRequest()

        data = info_order.cleaned_data
        item_ids = data.pop("items")
        add_items_to_order(id, item_ids, update=True)

        Order.objects.filter(id=id).update(**data)
        order = Order.objects.get(id=id)

        items_data = []
        for order_item in order.orderitem_set.all():
            items_data.append(
                {
                    "item_id": order_item.item.id,
                    "item_name": order_item.item.name,
                    "quantity": order_item.quantity,
                    "items_price": order_item.items_price,
                }
            )

        order_data = {
            "id": order.id,
            "table_number": order.table_number,
            "items": items_data,
            "total_price": order.total_price,
            "status": order.status,
        }

        return JsonResponse({"order": order_data})

    # ok
    def delete(self, request: http.HttpRequest, id: int) -> HttpResponse:
        try:
            order = Order.objects.get(id=id)
            order.delete()
        except ObjectDoesNotExist:
            return JsonResponse(
                {"detail": "Order does not exist", "success": False},
                status=404,
            )
        except Exception:
            return http.HttpResponseBadRequest()

        return JsonResponse(
            {"detail": "Order was successfully deleted", "success": True},
            status=200,
        )


@method_decorator(csrf_exempt, name="dispatch")
class OrdersView(views.View):
    def get(self, request: http.HttpRequest) -> HttpResponse:

        filter_query = SearchQueryParamsForm(request.GET)

        table_number = filter_query.data.get("table_number")
        status = filter_query.data.get("status")

        query = Q()

        if table_number:
            query &= Q(table_number=table_number)

        if status:
            query &= Q(status=status)

        orders = Order.objects.filter(query)

        orders_data = []
        for order in orders:
            items_data = []
            for (
                order_item
            ) in (
                order.orderitem_set.all()
            ):  # Используем обратную связь через промежуточную модель
                items_data.append(
                    {
                        "item_id": order_item.item.id,
                        "item_name": order_item.item.name,
                        "quantity": order_item.quantity,
                        "items_price": order_item.items_price,
                    }
                )

            orders_data.append(
                {
                    "id": order.id,
                    "table_number": order.table_number,
                    "items": items_data,
                    "total_price": order.total_price,
                    "status": order.status,
                }
            )

        return JsonResponse({"orders": orders_data})

    def post(self, request: http.HttpRequest) -> HttpResponse:
        info_order = InfoOrderForm(json.loads(request.body))
        if not info_order.is_valid():
            return JsonResponse({"detail": "Bad Request"}, status=400)

        data = info_order.cleaned_data
        item_ids = data.pop("items")

        order = Order.objects.create(**data)
        add_items_to_order(order.id, item_ids)

        return JsonResponse(
            {"detail": "Order was successfully created", "order_id": order.id},
            status=201,
        )


@method_decorator(csrf_exempt, name="dispatch")
class FilteredOrdersView(views.View):
    def get(self, request: http.HttpRequest) -> HttpResponse:

        filter_query = FilterQueryParamsForm(request.GET)

        if not filter_query.is_valid():
            return JsonResponse({"detail": "Bad Request"}, status=400)

        is_pending = filter_query.cleaned_data.get("is_pending")
        is_ready = filter_query.cleaned_data.get("is_ready")
        is_paid = filter_query.cleaned_data.get("is_paid")

        query = Q()

        if is_pending:
            query |= Q(status="is_pending")

        if is_ready:
            query |= Q(status="is_ready")

        if is_paid:
            query |= Q(status="is_paid")

        orders = Order.objects.filter(query)
        orders_data = []
        for order in orders:
            items_data = []
            for (
                order_item
            ) in (
                order.orderitem_set.all()
            ):  # Используем обратную связь через промежуточную модель
                items_data.append(
                    {
                        "item_id": order_item.item.id,
                        "item_name": order_item.item.name,
                        "quantity": order_item.quantity,
                        "items_price": order_item.items_price,
                    }
                )

            orders_data.append(
                {
                    "id": order.id,
                    "table_number": order.table_number,
                    "items": items_data,
                    "total_price": order.total_price,
                    "status": order.status,
                }
            )
        return JsonResponse({"orders": orders_data})


@method_decorator(csrf_exempt, name="dispatch")
class ChangeStatusView(views.View):
    # ok
    def patch(self, request: http.HttpRequest, id: int) -> HttpResponse:
        status_order_form = StatusOrderForm(json.loads(request.body))
        if not status_order_form.is_valid():
            return http.HttpResponseBadRequest()

        status = status_order_form.cleaned_data.get("status")
        Order.objects.filter(id=id).update(status=status)
        order = Order.objects.get(id=id)

        items_data = []
        for (
            order_item
        ) in (
            order.orderitem_set.all()
        ):  # Используем обратную связь через промежуточную модель
            items_data.append(
                {
                    "item_id": order_item.item.id,
                    "item_name": order_item.item.name,
                    "quantity": order_item.quantity,
                    "items_price": order_item.items_price,
                }
            )

        order_data = {
            "id": order.id,
            "table_number": order.table_number,
            "items": items_data,
            "total_price": order.total_price,
            "status": order.status,
            "success": True,
        }

        return JsonResponse(order_data)


class TotalPriceView(views.View):
    def get(self, request: http.HttpRequest) -> HttpResponse:

        status_order_form = StatusOrderForm(request.GET)
        if not status_order_form.is_valid():
            orders = Order.objects
        else:
            status = status_order_form.cleaned_data.get("status")
            orders = Order.objects.filter(status=status)

        total_orders_price = orders.aggregate(total_price=Sum("total_price"))
        total_orders_price["total_price"] = (
            total_orders_price["total_price"] or 0
        )
        return JsonResponse({**total_orders_price})


@method_decorator(csrf_exempt, name="dispatch")
class OrderItemView(views.View):
    # TODO добавлять, если уже есть item? да, считать количество
    def post(self, request: http.HttpRequest, id: int) -> HttpResponse:
        info_item_form = InfoItemForm(json.loads(request.body))
        if not info_item_form.is_valid():
            return http.HttpResponseBadRequest()

        item_id = info_item_form.cleaned_data["item_id"]
        item_ids = [
            item_id,
        ]

        try:
            add_items_to_order(id, item_ids)

        except ObjectDoesNotExist:
            return JsonResponse(
                {"error": "Object not found", "success": False}, status=404
            )

        return JsonResponse({"detail": "Item added to order", "success": True})

    def get(self, request: http.HttpRequest, id: int) -> HttpResponse:
        try:
            order = Order.objects.get(id=id)
            items_data = []
            for order_item in order.orderitem_set.all():
                items_data.append(
                    {
                        "item_id": order_item.item.id,
                        "item_name": order_item.item.name,
                        "quantity": order_item.quantity,
                        "items_price": order_item.items_price,
                    }
                )

        except ObjectDoesNotExist:
            return JsonResponse({"error": "Object not found"}, status=404)

        return JsonResponse({"items": items_data})

    def delete(self, request: http.HttpRequest, id: int) -> HttpResponse:
        info_item_form = InfoItemForm(json.loads(request.body))
        if not info_item_form.is_valid():
            return http.HttpResponseBadRequest()

        item_id = info_item_form.cleaned_data["item_id"]
        item_ids = [
            item_id,
        ]
        try:
            remove_items_from_order(id, item_ids)

        except ObjectDoesNotExist:
            return JsonResponse({"error": "Object not found"}, status=404)
        return JsonResponse({"detail": "Item removed from order"})


class ItemsView(views.View):
    def get(self, request: http.HttpRequest) -> HttpResponse:
        items = Item.objects.all()
        items_data = [
            {
                "id": item.id,
                "name": item.name,
                "price": item.price,
            }
            for item in items
        ]
        return JsonResponse({"items": items_data})
