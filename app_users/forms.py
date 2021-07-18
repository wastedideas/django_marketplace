from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.utils.translation import gettext_lazy as _
from app_users.models import Customer


class UserRegistration(UserCreationForm):

    class Meta:
        model = Customer
        fields = (
            'username',
            'first_name',
            'last_name',
            'password1',
            'password2',
        )


class TopUpBalanceForm(forms.Form):
    amount = forms.DecimalField(label=_('Enter the top-up amount'))
