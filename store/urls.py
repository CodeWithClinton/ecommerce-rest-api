from django.urls import path

from . import views

urlpatterns = [
    path("categories/", views.category_list, name="category-list"),
    path("categories/<int:category_id>/", views.category_detail, name="category-detail"),
    path("products/", views.product_list, name="product-list"),
    path("products/<int:product_id>/", views.product_detail, name="product-detail"),
    path("customers/", views.customer_list, name="customer-list"),
    path("customers/<int:customer_id>/", views.customer_detail, name="customer-detail"),
    path("orders/", views.order_list, name="order-list"),
    path("orders/<int:order_id>/", views.order_detail, name="order-detail"),
    path("orders/<int:order_id>/items/", views.add_order_item, name="order-add-item"),
]
