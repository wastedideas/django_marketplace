import random
from django.core.management import BaseCommand
from app_market.models import Shops, Products


class Command(BaseCommand):
    help = 'Создание магазинов и товаров'

    def handle(self, *args, **options):
        shop_objs = list(
            (
                Shops(
                    shop_name=f'Shop #{i_shop}'
                ) for i_shop in range(5)
            )
        )
        Shops.objects.bulk_create(shop_objs)
        products_list = [
            'bread',
            'cheese',
            'chocolate',
            'cola',
            'eggs',
            'ice-cream',
            'milk',
            'salt',
            'sugar',
            'water',
        ]

        products_objs = list(
            (
                Products(
                    product_name=random.choice(products_list),
                    product_price=random.random() * 100,
                    product_quantity=random.randint(1, 10),
                    product_shop=random.choice(Shops.objects.all()),
                ) for i_product in range(500)
            )
        )

        Products.objects.bulk_create(products_objs)
