from django import forms
from django.utils.translation import gettext_lazy as _


class QuantityOfCartElementsForm(forms.Form):
    quantity = forms.DecimalField(label=_('Enter quantity of products'))
