from decimal import Decimal
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from app_market.models import CustomerCart, Purchases


class Customer(AbstractUser):
    BRONZE = Decimal(0)
    SILVER = Decimal(100)
    GOLD = Decimal(500)
    PLATINUM = Decimal(1000)
    DIAMOND = Decimal(5000)

    CUSTOMER_STATUS = [
        (BRONZE, 'Bronze customer'),
        (SILVER, 'Silver customer'),
        (GOLD, 'Gold customer'),
        (PLATINUM, 'Platinum customer'),
        (DIAMOND, 'Diamond customer'),
    ]

    balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name=_('balance'),
    )
    status = models.DecimalField(
        max_digits=4,
        decimal_places=0,
        choices=CUSTOMER_STATUS,
        default=BRONZE,
        verbose_name=_('status'),
    )

    class Meta:
        verbose_name = _('customer')
        verbose_name_plural = _('customers')

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if kwargs.get('update_fields') and 'balance' in kwargs['update_fields']:

            if Purchases.objects.filter(purchase_customer=self):
                total_amount_by_user = Purchases.get_total_amount(self)

                if total_amount_by_user >= self.DIAMOND:
                    self.status = self.DIAMOND
                elif self.PLATINUM <= total_amount_by_user <= self.DIAMOND:
                    self.status = self.PLATINUM
                elif self.GOLD <= total_amount_by_user <= self.PLATINUM:
                    self.status = self.GOLD
                elif self.SILVER <= total_amount_by_user <= self.GOLD:
                    self.status = self.SILVER

        super().save()


@receiver(post_save, sender=Customer)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        CustomerCart.objects.create(
            customer_cart=instance,
        )
