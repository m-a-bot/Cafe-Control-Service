"""
URL configuration for cafe-control project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path

from .views import (
    ChangeStatusView,
    FilteredOrdersView,
    ItemsView,
    OrderItemView,
    OrdersView,
    OrderView,
    TotalPriceView,
)

urlpatterns = [
    path("orders/<int:id>/", OrderView.as_view(), name="order-detail-api"),
    path("orders/", OrdersView.as_view(), name="orders-api"),
    path(
        "filtered-orders/",
        FilteredOrdersView.as_view(),
        name="filtered-orders-api",
    ),
    path(
        "orders/<int:id>/status/",
        ChangeStatusView.as_view(),
        name="change-order-status-api",
    ),
    path(
        "orders/total_price/",
        TotalPriceView.as_view(),
        name="total-order-price-api",
    ),
    path(
        "orders/<int:id>/items/",
        OrderItemView.as_view(),
        name="order-item-api",
    ),
    path("items/", ItemsView.as_view(), name="items-api"),
]
