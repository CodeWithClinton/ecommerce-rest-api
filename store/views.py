from decimal import Decimal, InvalidOperation

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Category, Customer, Order, OrderItem, Product


def category_to_dict(category: Category) -> dict:
    return {
        "id": category.id,
        "name": category.name,
        "slug": category.slug,
        "created_at": category.created_at,
        "updated_at": category.updated_at,
    }


def product_to_dict(product: Product) -> dict:
    return {
        "id": product.id,
        "name": product.name,
        "slug": product.slug,
        "description": product.description,
        "price": str(product.price),
        "stock": product.stock,
        "is_active": product.is_active,
        "category": category_to_dict(product.category),
        "created_at": product.created_at,
        "updated_at": product.updated_at,
    }


def customer_to_dict(customer: Customer) -> dict:
    return {
        "id": customer.id,
        "first_name": customer.first_name,
        "last_name": customer.last_name,
        "email": customer.email,
        "phone": customer.phone,
        "created_at": customer.created_at,
        "updated_at": customer.updated_at,
    }


def order_item_to_dict(item: OrderItem) -> dict:
    return {
        "id": item.id,
        "product": product_to_dict(item.product),
        "quantity": item.quantity,
        "unit_price": str(item.unit_price),
        "subtotal": str(item.subtotal),
    }


def order_to_dict(order: Order) -> dict:
    return {
        "id": order.id,
        "customer": customer_to_dict(order.customer),
        "status": order.status,
        "items": [order_item_to_dict(item) for item in order.items.select_related("product", "product__category")],
        "total_amount": str(order.total_amount),
        "created_at": order.created_at,
        "updated_at": order.updated_at,
    }


def parse_decimal(value, field_name: str):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Response(
            {"error": f"{field_name} must be a valid decimal value."},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["GET", "POST"])
def category_list(request):
    if request.method == "GET":
        categories = Category.objects.all()
        return Response([category_to_dict(category) for category in categories])

    name = request.data.get("name")
    slug = request.data.get("slug")

    if not name or not slug:
        return Response(
            {"error": "Both name and slug are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if Category.objects.filter(slug=slug).exists():
        return Response(
            {"error": "A category with this slug already exists."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    category = Category.objects.create(name=name, slug=slug)
    return Response(category_to_dict(category), status=status.HTTP_201_CREATED)


@api_view(["GET", "PATCH", "DELETE"])
def category_detail(request, category_id: int):
    category = get_object_or_404(Category, pk=category_id)

    if request.method == "GET":
        return Response(category_to_dict(category))

    if request.method == "PATCH":
        name = request.data.get("name")
        slug = request.data.get("slug")

        if slug and Category.objects.exclude(pk=category.id).filter(slug=slug).exists():
            return Response(
                {"error": "A category with this slug already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if name is not None:
            category.name = name
        if slug is not None:
            category.slug = slug

        category.save()
        return Response(category_to_dict(category))

    category.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
def product_list(request):
    if request.method == "GET":
        products = Product.objects.select_related("category").all()
        return Response([product_to_dict(product) for product in products])

    category_id = request.data.get("category_id")
    name = request.data.get("name")
    slug = request.data.get("slug")
    price = request.data.get("price")

    if not all([category_id, name, slug, price is not None]):
        return Response(
            {"error": "category_id, name, slug, and price are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    category = Category.objects.filter(pk=category_id).first()
    if not category:
        return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

    parsed_price = parse_decimal(price, "price")
    if isinstance(parsed_price, Response):
        return parsed_price

    if Product.objects.filter(slug=slug).exists():
        return Response(
            {"error": "A product with this slug already exists."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    product = Product.objects.create(
        category=category,
        name=name,
        slug=slug,
        description=request.data.get("description", ""),
        price=parsed_price,
        stock=request.data.get("stock", 0),
        is_active=request.data.get("is_active", True),
    )
    return Response(product_to_dict(product), status=status.HTTP_201_CREATED)


@api_view(["GET", "PATCH", "DELETE"])
def product_detail(request, product_id: int):
    product = get_object_or_404(Product.objects.select_related("category"), pk=product_id)

    if request.method == "GET":
        return Response(product_to_dict(product))

    if request.method == "PATCH":
        if request.data.get("category_id") is not None:
            category = Category.objects.filter(pk=request.data.get("category_id")).first()
            if not category:
                return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
            product.category = category

        if request.data.get("slug"):
            slug = request.data.get("slug")
            if Product.objects.exclude(pk=product.id).filter(slug=slug).exists():
                return Response(
                    {"error": "A product with this slug already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            product.slug = slug

        for field in ["name", "description", "stock", "is_active"]:
            if request.data.get(field) is not None:
                setattr(product, field, request.data.get(field))

        if request.data.get("price") is not None:
            parsed_price = parse_decimal(request.data.get("price"), "price")
            if isinstance(parsed_price, Response):
                return parsed_price
            product.price = parsed_price

        product.save()
        return Response(product_to_dict(product))

    product.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
def customer_list(request):
    if request.method == "GET":
        customers = Customer.objects.all()
        return Response([customer_to_dict(customer) for customer in customers])

    first_name = request.data.get("first_name")
    last_name = request.data.get("last_name")
    email = request.data.get("email")

    if not first_name or not last_name or not email:
        return Response(
            {"error": "first_name, last_name, and email are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if Customer.objects.filter(email=email).exists():
        return Response(
            {"error": "A customer with this email already exists."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    customer = Customer.objects.create(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=request.data.get("phone", ""),
    )
    return Response(customer_to_dict(customer), status=status.HTTP_201_CREATED)


@api_view(["GET", "PATCH", "DELETE"])
def customer_detail(request, customer_id: int):
    customer = get_object_or_404(Customer, pk=customer_id)

    if request.method == "GET":
        return Response(customer_to_dict(customer))

    if request.method == "PATCH":
        if request.data.get("email"):
            email = request.data.get("email")
            if Customer.objects.exclude(pk=customer.id).filter(email=email).exists():
                return Response(
                    {"error": "A customer with this email already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            customer.email = email

        for field in ["first_name", "last_name", "phone"]:
            if request.data.get(field) is not None:
                setattr(customer, field, request.data.get(field))

        customer.save()
        return Response(customer_to_dict(customer))

    customer.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
def order_list(request):
    if request.method == "GET":
        orders = Order.objects.select_related("customer").prefetch_related("items__product__category")
        return Response([order_to_dict(order) for order in orders])

    customer_id = request.data.get("customer_id")
    if not customer_id:
        return Response(
            {"error": "customer_id is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    customer = Customer.objects.filter(pk=customer_id).first()
    if not customer:
        return Response({"error": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)

    status_value = request.data.get("status", Order.Status.PENDING)
    allowed_statuses = [choice[0] for choice in Order.Status.choices]
    if status_value not in allowed_statuses:
        return Response(
            {"error": f"status must be one of: {', '.join(allowed_statuses)}."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    order = Order.objects.create(customer=customer, status=status_value)

    return Response(order_to_dict(order), status=status.HTTP_201_CREATED)


@api_view(["GET", "PATCH", "DELETE"])
def order_detail(request, order_id: int):
    order = get_object_or_404(
        Order.objects.select_related("customer").prefetch_related("items__product__category"),
        pk=order_id,
    )

    if request.method == "GET":
        return Response(order_to_dict(order))

    if request.method == "PATCH":
        if request.data.get("status") is not None:
            status_value = request.data.get("status")
            allowed_statuses = [choice[0] for choice in Order.Status.choices]
            if status_value not in allowed_statuses:
                return Response(
                    {"error": f"status must be one of: {', '.join(allowed_statuses)}."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            order.status = status_value

        if request.data.get("customer_id") is not None:
            customer = Customer.objects.filter(pk=request.data.get("customer_id")).first()
            if not customer:
                return Response({"error": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)
            order.customer = customer

        order.save()
        return Response(order_to_dict(order))

    order.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
def add_order_item(request, order_id: int):
    order = get_object_or_404(Order, pk=order_id)

    product_id = request.data.get("product_id")
    quantity = request.data.get("quantity", 1)

    if not product_id:
        return Response({"error": "product_id is required."}, status=status.HTTP_400_BAD_REQUEST)

    product = Product.objects.select_related("category").filter(pk=product_id).first()
    if not product:
        return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return Response(
            {"error": "quantity must be a positive integer."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if quantity <= 0:
        return Response(
            {"error": "quantity must be a positive integer."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    item = OrderItem.objects.create(
        order=order,
        product=product,
        quantity=quantity,
        unit_price=product.price,
    )

    order = Order.objects.select_related("customer").prefetch_related("items__product__category").get(pk=order.id)

    return Response(
        {
            "message": "Order item added successfully.",
            "item": order_item_to_dict(item),
            "order": order_to_dict(order),
        },
        status=status.HTTP_201_CREATED,
    )
