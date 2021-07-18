from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views import View
from django.db.models import Sum
from django.contrib.auth.mixins import LoginRequiredMixin
from app_market.models import Shops, Products, CustomerCart, CustomerCartElement, Purchases
from app_market.forms import QuantityOfCartElementsForm
from app_users.models import Customer


class AppMarketLoginRequired(LoginRequiredMixin):
    login_url = reverse_lazy('login')


class ProductsListView(View):

    def get(self, request):
        shop_filter = Shops.objects.all()
        return render(
            request,
            'app_market/products_list.html',
            {
                'shop_filter': shop_filter,
            },
        )


class AddToCartView(AppMarketLoginRequired, View):

    def get(self, request, prod_id):
        product_to_cart = Products.objects.get(id=prod_id)
        quantity_elements_form = QuantityOfCartElementsForm()
        return render(
            request,
            'app_market/add_to_cart.html',
            {
                'product_to_cart': product_to_cart,
                'quantity_elements_form': quantity_elements_form,
            },
        )

    def post(self, request, prod_id):
        product_to_cart = Products.objects.get(id=prod_id)
        quantity_elements_form = QuantityOfCartElementsForm(request.POST)
        if int(request.POST.get('quantity')) > product_to_cart.product_quantity:
            quantity_elements_form.add_error(
                'quantity',
                'Too many goods. Please, indicate less.',
            )
        if quantity_elements_form.is_valid():
            new_cart_element = CustomerCartElement.objects.create(
                cart_element=product_to_cart,
                element_quantity=quantity_elements_form.cleaned_data['quantity']
            )
            user_cart = CustomerCart.objects.get(customer_cart=request.user)
            user_cart.cart_elements.add(new_cart_element)
            user_cart.total_price += (
                new_cart_element.cart_element.product_price
                * new_cart_element.element_quantity
            )
            user_cart.save(update_fields=['total_price'])
            return HttpResponseRedirect(reverse_lazy('personal_area'))
        else:
            return render(
                request,
                'app_market/add_to_cart.html',
                {
                    'product_to_cart': product_to_cart,
                    'quantity_elements_form': quantity_elements_form,
                },
            )


class PurchaseView(AppMarketLoginRequired, View):

    def get(self, request, cart_id):
        curr_user = Customer.objects.get(id=request.user.id)
        cart_to_payment = CustomerCart.objects.get(id=cart_id)
        if curr_user.balance < cart_to_payment.total_price:
            return HttpResponse('Balance Error')
        curr_user.balance -= cart_to_payment.total_price

        for i_cart_elem in cart_to_payment.cart_elements.select_related():
            i_cart_elem.cart_element.product_quantity -= i_cart_elem.element_quantity
            if i_cart_elem.cart_element.product_quantity == 0:
                i_cart_elem.cart_element.product_shop = None
            i_cart_elem.cart_element.save(
                update_fields=[
                    'product_quantity',
                    'product_shop',
                ],
            )

            new_purchase = Purchases.objects.create(
                purchase_customer=curr_user,
                purchased_product=i_cart_elem.cart_element,
                purchased_quantity=i_cart_elem.element_quantity,
            )

            CustomerCart.remove_from_other_carts(
                new_purchase,
                curr_user
            )

        cart_to_payment.cart_elements.all().delete()
        cart_to_payment.total_price = 0
        cart_to_payment.save(update_fields=['total_price'])
        curr_user.save(update_fields=['balance'])
        return render(
            request,
            'app_market/add_to_purchases.html',
            {
                'cart_to_payment': cart_to_payment,
            },
        )


class ReportView(AppMarketLoginRequired, View):

    def get(self, request):
        data_for_report = Purchases.objects.values(
            'purchased_product__id',
            'purchased_product__product_name',
        ).annotate(total=Sum('purchased_quantity')).order_by('-total')[:10]

        return render(
            request,
            'app_market/report.html',
            {
                'data_for_report': data_for_report,
            },
        )
