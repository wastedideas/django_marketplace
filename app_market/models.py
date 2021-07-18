from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, F


class Shops(models.Model):
    shop_name = models.CharField(
        max_length=200,
        default='',
        verbose_name=_('shop name'),
    )

    class Meta:
        verbose_name = _('shop')
        verbose_name_plural = _('shops')

    def __str__(self):
        return self.shop_name


class Products(models.Model):
    product_name = models.CharField(
        max_length=200,
        default='',
        verbose_name=_('product name'),
    )
    product_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name=_('product price')
    )
    product_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name=_('product quantity')
    )
    product_shop = models.ForeignKey(
        'Shops',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_('product shop'),
    )

    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')

    def __str__(self):
        return self.product_name


class CustomerCart(models.Model):
    customer_cart = models.ForeignKey(
        'app_users.Customer',
        on_delete=models.CASCADE,
        verbose_name=_('customer cart')
    )
    cart_elements = models.ManyToManyField(
        'CustomerCartElement',
        blank=True,
        verbose_name=_('products in cart'),
    )
    total_price = models.DecimalField(
        max_digits=15,
        null=True,
        blank=True,
        default=0,
        decimal_places=2,
        verbose_name=_('total price'),
    )

    def __str__(self):
        return f'Cart for customer {self.customer_cart}'

    @classmethod
    def remove_from_other_carts(cls, purchase, user):
        for i_cart in CustomerCart.objects.all().exclude(customer_cart=user):
            elems_in_other_carts = i_cart.cart_elements.filter(
                cart_element__id=purchase.purchased_product.id
            )
            if elems_in_other_carts:
                for i_elem in elems_in_other_carts:
                    if i_elem.element_quantity > i_elem.cart_element.product_quantity:
                        i_elem.element_quantity = i_elem.cart_element.product_quantity
                        if i_elem.element_quantity == 0:
                            i_cart.cart_elements.remove(i_elem)
                        else:
                            i_elem.save(update_fields=['element_quantity'])


class CustomerCartElement(models.Model):
    cart_element = models.ForeignKey(
        'Products',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_('element'),
    )
    element_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name=_('element quantity')
    )


class Purchases(models.Model):
    purchase_customer = models.ForeignKey(
        'app_users.Customer',
        on_delete=models.CASCADE,
        verbose_name=_('customer')
    )
    purchased_product = models.ForeignKey(
        'app_market.Products',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_('purchase product')
    )
    purchased_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name=_('purchase quantity')
    )

    @classmethod
    def get_total_amount(cls, user):
        total_dict = Purchases.objects.filter(purchase_customer=user).aggregate(
            total_amount=Sum(
                F(
                    'purchased_product__product_price'
                ) * F(
                    'purchased_quantity'
                )
            )
        )
        return total_dict['total_amount']
