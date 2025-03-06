from django.contrib import admin

from .models import Item, Order, OrderItem


class OrderItemInline(admin.TabularInline):  # Или StackedInline
    model = OrderItem
    extra = 1


class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ("total_price",)
    inlines = [OrderItemInline]


class OrderItemAdmin(admin.ModelAdmin):
    readonly_fields = ("items_price",)


# Register your models here.
admin.site.register(Item)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
