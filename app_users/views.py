from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render
from django.views import View
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from app_market.models import CustomerCart
from app_market.views import AppMarketLoginRequired
from app_users.forms import UserRegistration, TopUpBalanceForm


class UserRegisterView(FormView):
    form_class = UserRegistration
    template_name = 'app_users/register.html'
    success_url = reverse_lazy('products_list')

    def form_valid(self, form):
        form.save()
        username = self.request.POST['username']
        raw_password = self.request.POST['password1']
        user = authenticate(
            username=username,
            password=raw_password,
        )
        login(self.request, user)
        return super().form_valid(form)


class UserLoginView(LoginView):
    template_name = 'app_users/login.html'


class UserLogoutView(LogoutView):
    template_name = 'app_users/logout.html'


class PersonalAreaView(AppMarketLoginRequired, View):

    def get(self, request):
        user_cart = CustomerCart.objects.get(customer_cart=request.user)
        return render(
            request,
            'app_users/personal_area.html',
            {
                'user_cart': user_cart,
            },
        )


class TopUpBalanceView(AppMarketLoginRequired, FormView):
    form_class = TopUpBalanceForm
    template_name = 'app_users/top_up_balance.html'
    success_url = reverse_lazy('personal_area')

    def form_valid(self, form):
        top_up_balance_amount = form.cleaned_data['amount']
        self.request.user.balance += top_up_balance_amount
        self.request.user.save(update_fields=['balance'])
        return super().form_valid(form)
