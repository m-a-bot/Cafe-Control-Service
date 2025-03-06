from random import choices

from django import forms
from django.core.exceptions import ValidationError

from .models import ORDER_STATUSES, Item


class SearchQueryParamsForm(forms.Form):
    number_table = forms.IntegerField(required=False, min_value=1)
    status = forms.CharField(required=False)


class FilterQueryParamsForm(forms.Form):
    BOOL_CHOICES = [("true", True), ("false", False)]

    is_pending = forms.TypedChoiceField(
        choices=BOOL_CHOICES, required=True, coerce=lambda x: x == "true"
    )
    is_ready = forms.TypedChoiceField(
        choices=BOOL_CHOICES, required=True, coerce=lambda x: x == "true"
    )
    is_paid = forms.TypedChoiceField(
        choices=BOOL_CHOICES, required=True, coerce=lambda x: x == "true"
    )


class StatusOrderForm(forms.Form):
    status = forms.TypedChoiceField(choices=ORDER_STATUSES, required=True)


class InfoOrderForm(forms.Form):
    table_number = forms.IntegerField(min_value=1)
    items = forms.JSONField()

    def clean_items(self):
        items = self.cleaned_data["items"]
        if not isinstance(items, list):
            raise ValidationError("items must be list")

        existing_ids = set(
            Item.objects.filter(id__in=items).values_list("id", flat=True)
        )
        missing_ids = set(items) - existing_ids

        if missing_ids:
            raise ValidationError("")

        return items


class InfoItemForm(forms.Form):
    item_id = forms.IntegerField(min_value=1)
