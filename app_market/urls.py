from django.urls import path
from app_market.views import ProductsListView, AddToCartView, PurchaseView, ReportView


urlpatterns = [
    path(
        '',
        ProductsListView.as_view(),
        name='products_list',
    ),
    path(
        'add_to_cart/<int:prod_id>',
        AddToCartView.as_view(),
        name='add_to_cart'
        ),
    path(
        'purchase/<int:cart_id>',
        PurchaseView.as_view(),
        name='purchase'
    ),
    path(
        'report/',
        ReportView.as_view(),
        name='report',
    ),
]
