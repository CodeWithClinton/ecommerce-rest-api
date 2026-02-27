# E-commerce REST API Endpoints

Base URL prefix: `/api/`

## Categories

### `GET /api/categories/`
Return all categories.

### `POST /api/categories/`
Create a category.

**Body**
```json
{
  "name": "Electronics",
  "slug": "electronics"
}
```

**Validation**
- `name` and `slug` are required.
- `slug` must be unique.

### `GET /api/categories/{category_id}/`
Return one category by ID.

### `PATCH /api/categories/{category_id}/`
Update a category.

**Body (all fields optional)**
```json
{
  "name": "Updated name",
  "slug": "updated-slug"
}
```

**Validation**
- If provided, `slug` must remain unique.

### `DELETE /api/categories/{category_id}/`
Delete a category.

---

## Products

### `GET /api/products/`
Return all products.

### `POST /api/products/`
Create a product.

**Body**
```json
{
  "category_id": 1,
  "name": "Headphones",
  "slug": "headphones",
  "description": "Noise-cancelling",
  "price": "199.99",
  "stock": 50,
  "is_active": true
}
```

**Validation**
- Required: `category_id`, `name`, `slug`, `price`.
- `category_id` must reference an existing category.
- `price` must be a valid decimal.
- `slug` must be unique.

### `GET /api/products/{product_id}/`
Return one product by ID.

### `PATCH /api/products/{product_id}/`
Update a product.

**Body (all fields optional)**
```json
{
  "category_id": 2,
  "name": "Updated product",
  "slug": "updated-product",
  "description": "Updated description",
  "price": "149.99",
  "stock": 40,
  "is_active": false
}
```

**Validation**
- If provided, `category_id` must exist.
- If provided, `price` must be a valid decimal.
- If provided, `slug` must remain unique.

### `DELETE /api/products/{product_id}/`
Delete a product.

---

## Customers

### `GET /api/customers/`
Return all customers.

### `POST /api/customers/`
Create a customer.

**Body**
```json
{
  "first_name": "Jane",
  "last_name": "Doe",
  "email": "jane@example.com",
  "phone": "+1-555-0100"
}
```

**Validation**
- Required: `first_name`, `last_name`, `email`.
- `email` must be unique.

### `GET /api/customers/{customer_id}/`
Return one customer by ID.

### `PATCH /api/customers/{customer_id}/`
Update a customer.

**Body (all fields optional)**
```json
{
  "first_name": "Janet",
  "last_name": "Doe",
  "email": "janet@example.com",
  "phone": "+1-555-0101"
}
```

**Validation**
- If provided, `email` must remain unique.

### `DELETE /api/customers/{customer_id}/`
Delete a customer.

---

## Orders

### `GET /api/orders/`
Return all orders with their items and totals.

### `POST /api/orders/`
Create an order.

**Body**
```json
{
  "customer_id": 1,
  "status": "pending"
}
```

**Validation**
- `customer_id` is required and must exist.
- `status` is optional.
- Allowed `status` values: `pending`, `paid`, `shipped`, `completed`, `canceled`.

### `GET /api/orders/{order_id}/`
Return one order by ID.

### `PATCH /api/orders/{order_id}/`
Update an order.

**Body (all fields optional)**
```json
{
  "customer_id": 2,
  "status": "paid"
}
```

**Validation**
- If provided, `customer_id` must exist.
- If provided, `status` must be one of: `pending`, `paid`, `shipped`, `completed`, `canceled`.

### `DELETE /api/orders/{order_id}/`
Delete an order.

### `POST /api/orders/{order_id}/items/`
Add an item to an existing order.

**Body**
```json
{
  "product_id": 10,
  "quantity": 2
}
```

**Validation**
- `product_id` is required and must exist.
- `quantity` is optional (defaults to `1`) and must be a positive integer.

---

## Response notes

- All endpoints return JSON.
- List endpoints return arrays.
- Detail endpoints return a single object.
- Create endpoints return `201 Created`.
- Delete endpoints return `204 No Content`.
- Validation errors return `400 Bad Request`.
- Missing related resources (for example invalid `customer_id`) return `404 Not Found`.
