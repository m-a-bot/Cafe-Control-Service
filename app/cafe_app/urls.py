from django.urls import path

from .views import (
    ChangeLocalOrderPageView,
    ClearLocalOrderPageView,
    CreateOrderPageView,
    DeleteOrderPageView,
    HomePageView,
    OrderPageView,
    OrdersPageView,
    OrdersTemplatePageView,
    OrderTemplatePageView,
    SearchOrdersPageView,
)

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("orders/<int:id>", OrderPageView.as_view(), name="order-detail"),
    path(
        "orders_template/<int:id>",
        OrderTemplatePageView.as_view(),
        name="order_template-detail",
    ),
    path("orders", OrdersPageView.as_view(), name="orders"),
    path(
        "orders_template",
        OrdersTemplatePageView.as_view(),
        name="orders_template",
    ),
    path("create-order", CreateOrderPageView.as_view(), name="create-order"),
    path(
        "change-local-order",
        ChangeLocalOrderPageView.as_view(),
        name="change-local-order",
    ),
    path(
        "clear-local-order",
        ClearLocalOrderPageView.as_view(),
        name="clear-local-order",
    ),
    path("delete-order", DeleteOrderPageView.as_view(), name="delete-order"),
    path(
        "search-orders",
        SearchOrdersPageView.as_view(),
        name="search-orders",
    ),
]
