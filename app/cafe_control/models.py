from django.db import models

ORDER_STATUSES = [
    ("is_pending", "в ожидании"),
    ("is_ready", "готово"),
    ("is_paid", "оплачено"),
]


class Item(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)

    def __str__(self):
        return self.name


class Order(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    table_number = models.IntegerField()
    items = models.ManyToManyField(
        "Item", related_name="items", blank=True, through="OrderItem"
    )
    total_price = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.0, editable=False
    )
    status = models.CharField(choices=ORDER_STATUSES, default="is_pending")

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    items_price = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.0, editable=False
    )

    class Meta:
        unique_together = ("order", "item")
