from django import forms


class SearchQueryParamsForm(forms.Form):
    number_table = forms.IntegerField(required=False, min_value=1)
    status = forms.CharField(required=False)


class FilterQueryParamsForm(forms.Form):
    BOOL_CHOICES = [("true", True), ("false", False)]

    is_pending = forms.TypedChoiceField(
        choices=BOOL_CHOICES,
        required=True,
        coerce=lambda x: x == "true",
    )
    is_ready = forms.TypedChoiceField(
        choices=BOOL_CHOICES,
        required=True,
        coerce=lambda x: x == "true",
    )
    is_paid = forms.TypedChoiceField(
        choices=BOOL_CHOICES,
        required=True,
        coerce=lambda x: x == "true",
    )
