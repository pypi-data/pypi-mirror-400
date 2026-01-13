# Keyban API Client

A Python client library for interacting with the Keyban API Product management. This client provides a clean, type-safe interface for managing products, including full CRUD operations.

## Features

- **List products** with filtering and pagination
- **Get specific products** by ID (public endpoint)
- **Create new products** with validation
- **Update existing products** with partial updates
- **Delete products** with proper authorization
- **Dynamic field schemas** using `DynamicFieldDef` for type-safe product and passport fields
- **Type-safe models** using Pydantic for request/response validation
- **Comprehensive error handling** with proper HTTP status code handling
- **Convenience functions** for common operations

**Supported Network:** Currently supports StarknetSepolia only (default).

## Quick Start

### Simple Product Creation

```python
from uuid import UUID, uuid4
from keyban_api_client import ProductClient, ProductFields, CreateProductRequest, DynamicFieldDef

# Initialize the client
client = ProductClient(
    base_url="https://api.prod.keyban.io",
    api_key="your-api-key"
)

# Define the schema for product fields (what fields are allowed)
product_fields_schema = [
    DynamicFieldDef(name="name", type="string", required=True),
    DynamicFieldDef(name="description", type="text"),
    DynamicFieldDef(name="identifier", type="string", required=True),
]

# Create the product data (must conform to schema)
product_name = f"My Product {uuid4().hex[:8]}"
product_data = ProductFields(
    name=product_name,
    description="A product created via Python client",
    identifier=f"PRODUCT-{uuid4().hex[:6].upper()}"
)

request = CreateProductRequest(
    name=product_name,
    application=UUID("your-application-id"),
    status="ACTIVE",
    network="StarknetSepolia",
    productFields=product_fields_schema,  # Schema definition
    fields=product_data.model_dump(),     # Data conforming to schema
)

new_product = client.create_product(request)
print(f"Created product: {new_product.id}")

# List products
products = client.list_products(page_size=10)
print(f"Found {products.total} products")

# Get a specific product (public endpoint - no auth needed)
product = client.get_product(new_product.id)
print(f"Product: {product.name}")

# Close the client when done
client.close()
```

## Certification

Product sheets are certified on the blockchain using the `certifiedPaths` field. This field points to specific fields within `product.data` that will be digitally signed and recorded on the blockchain.

**How it works:**

1. **Certified Paths**: JSON paths pointing to fields that should be certified (e.g., `["name", "brand.name", "gtin"]`)
2. **Automatic Triggering**: Certification events fire when `certifiedPaths` or any referenced field changes
3. **Status Requirement**: Certification only triggers when product status is `ACTIVE`
4. **Blockchain Event**: Emits transaction with IPFS CID, certifier signature, and product ID

**Example** (see Complete CRUD Workflow for full code):

```python
request = CreateProductRequest(
    name="Product",
    application=UUID("your-app-id"),
    status="ACTIVE",  # Required for certification
    fields=product_data.model_dump(),
    certified_paths=["name", "description", "brand.name"]  # Fields to certify
)
```

### Tracking Certifications

You can track product certifications using the Keyban indexer API:

```bash
curl 'https://subql-starknet-sepolia.prod.keyban.io/' \
  -H 'accept: application/json' \
  -H 'content-type: application/json' \
  --data-raw '{
    "query": "query CertificationEvents { productCertifications( filter: {productId: {equalTo: \"<productId>\"}} ) { edges { node { transactionId ipfsCid certifierPubkey certifierSignature } } } }",
    "operationName": "CertificationEvents"
  }'
```

Replace `<productId>` with your actual product sheet ID.

## Advanced Usage

### Filtering with FilterOperator

The API supports filtering on the following fields:

- `application.id`: Filter by application UUID (eq operator only)
- `name`: Filter by product name (eq for exact match, contains for substring search)

```python
from keyban_api_client import FilterOperator

# Filter by application ID (exact match only)
app_filter = FilterOperator(field="application.id", operator="eq", value="your-app-id")

# Filter by product name (substring search, case-insensitive)
name_filter = FilterOperator(field="name", operator="contains", value="Cotton")

# Combine filters
products = client.list_products(
    filters=[app_filter, name_filter],
    page_size=20
)

print(f"Found {products.total} matching products")
for product in products.data:
    print(f"- {product.name} ({product.status})")
```

### Error Handling

```python
import requests
from keyban_api_client import ProductClient

client = ProductClient(base_url="...", api_key="...")

try:
    product = client.create_product(request)
except requests.HTTPError as e:
    if e.response.status_code == 400:
        # Get detailed error message from API
        try:
            error_details = e.response.json()
            print(f"Validation error: {error_details}")
        except:
            print(f"Bad request: {e.response.text}")
    elif e.response.status_code == 401:
        print("Authentication failed - check your API key")
    elif e.response.status_code == 404:
        print("Resource not found")
    else:
        print(f"HTTP error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    client.close()
```

### Pagination & Context Manager

```python
# Paginate through all products
all_products = []
page = 1
while True:
    response = client.list_products(current_page=page, page_size=50)
    all_products.extend(response.data)
    if len(response.data) < 50:
        break
    page += 1

# Or use context manager for auto-cleanup
with ProductClient(base_url="...", api_key="...") as client:
    products = client.list_products()
```

### Complete CRUD Workflow

```python
from uuid import UUID, uuid4
from keyban_api_client import (
    ProductClient, ProductFields, CreateProductRequest,
    UpdateProductRequest, DynamicFieldDef
)

client = ProductClient(base_url="https://api.prod.keyban.io", api_key="your-api-key")

# 1. Define schemas
product_fields_schema = [
    DynamicFieldDef(name="name", type="string", required=True, maxLength=200),
    DynamicFieldDef(name="description", type="text"),
    DynamicFieldDef(name="identifier", type="string", required=True),
    DynamicFieldDef(name="brand", type="string"),
    DynamicFieldDef(name="keywords", type="array", itemsType=DynamicFieldDef(name="[]", type="string")),
]

passport_fields_schema = [
    DynamicFieldDef(name="serialNumber", type="string", required=True),
    DynamicFieldDef(name="manufacturingDate", type="date"),
]

# 2. Create product data
product_data = ProductFields(
    name=f"CLI Product {uuid4().hex[:8]}",
    description="Created from CLI for testing",
    identifier=f"PRODUCT-{uuid4().hex[:6].upper()}",
    brand="TestBrand",
    keywords=["cli", "test", "demo"]
)

# 3. Create product
create_request = CreateProductRequest(
    name=product_data.name,
    application=UUID("your-application-id"),
    status="ACTIVE",
    network="StarknetSepolia",
    productFields=product_fields_schema,
    passportsFields=passport_fields_schema,
    fields=product_data.model_dump(),
    certified_paths=["name", "description", "brand"]
)

created = client.create_product(create_request)
print(f"Created: {created.id}")

# 4. Update product
# IMPORTANT: The API requires all required fields in updates, even if unchanged.
# You must include fields marked as required in the schema (e.g., 'identifier').
updated_data = ProductFields(
    name=f"{created.name} (Updated)",
    description="Updated description",
    identifier=product_data.identifier,  # Required field - must be preserved!
    brand=product_data.brand,
    keywords=["cli", "test", "demo", "updated"]
)

update_request = UpdateProductRequest(
    fields=updated_data.model_dump(),
    certified_paths=["name", "description"]
)

updated = client.update_product(created.id, update_request)
print(f"Updated: {updated.name}")

# 5. Delete product (optional)
# deleted = client.delete_product(created.id)
# print(f"Deleted: {deleted}")

client.close()
```

### Product with Nested Objects

```python
from uuid import UUID, uuid4
from keyban_api_client import ProductClient, ProductFields, CreateProductRequest, DynamicFieldDef

client = ProductClient(base_url="https://api.prod.keyban.io", api_key="your-api-key")

# Schema with nested objects, arrays, and enums
product_fields_schema = [
    DynamicFieldDef(name="identifier", type="string", required=True),
    DynamicFieldDef(name="name", type="string", required=True, maxLength=200),
    DynamicFieldDef(name="description", type="text"),
    DynamicFieldDef(name="gtin", type="string", minLength=8, maxLength=14),

    # Nested object: brand
    DynamicFieldDef(
        name="brand",
        type="object",
        fields=[
            DynamicFieldDef(name="name", type="string", required=True),
            DynamicFieldDef(name="identifier", type="string"),
        ]
    ),

    # Enum field
    DynamicFieldDef(name="category", type="enum", variants=["Electronics", "Clothing", "Food", "Other"]),

    # Array of strings
    DynamicFieldDef(name="keywords", type="array", itemsType=DynamicFieldDef(name="[]", type="string")),

    # Nested object: manufacturer with nested array
    DynamicFieldDef(
        name="manufacturer",
        type="object",
        fields=[
            DynamicFieldDef(name="name", type="string", required=True),
            DynamicFieldDef(name="location", type="string"),
            DynamicFieldDef(name="certifications", type="array", itemsType=DynamicFieldDef(name="[]", type="string")),
        ]
    ),
]

# Create product data conforming to the schema
product_data = ProductFields(
    identifier=f"PRODUCT-{uuid4().hex[:6].upper()}",
    name="Organic Cotton T-Shirt",
    description="Sustainably produced cotton t-shirt",
    gtin="1234567890123",
    brand={"name": "EcoWear", "identifier": "ecowear-brand"},
    category="Clothing",
    keywords=["organic", "cotton", "sustainable"],
    manufacturer={
        "name": "EcoTextiles Ltd",
        "location": "Portugal",
        "certifications": ["GOTS", "OEKO-TEX"]
    }
)

request = CreateProductRequest(
    name=product_data.name,
    application=UUID("your-application-id"),
    status="ACTIVE",
    network="StarknetSepolia",
    productFields=product_fields_schema,
    fields=product_data.model_dump(),
    certified_paths=["name", "brand.name", "gtin", "manufacturer.name"]  # Certify nested fields
)

product = client.create_product(request)
print(f"Created: {product.name} with brand {product.fields.get('brand', {}).get('name')}")
client.close()
```

## API Reference

### ProductClient

Main client class for interacting with the API.

#### Constructor

```python
ProductClient(
    base_url: str,
    api_version: str = "v1",
    api_key: Optional[str] = None,
    timeout: int = 30
)
```

#### Methods

##### `list_products(filters=None, current_page=1, page_size=10)`

List products with optional filtering.

- **filters** (List[FilterOperator], optional): List of filters. Supported fields: `application.id` (eq only), `name` (eq, contains)
- **current_page** (int): Page number (1-based, default: 1)
- **page_size** (int): Items per page (default: 10, max: 100)

Returns: `ProductListResponse` with `data` (list of products) and `total` count.

##### `get_product(product_id: UUID)`

Get a specific product sheet by ID. This is a public endpoint.

Returns: `Product` object.

##### `create_product(product_data: CreateProductRequest)`

Create a new product sheet. Requires authentication.

Returns: Created `Product` object.

##### `update_product(product_id: UUID, update_data: UpdateProductRequest)`

Update an existing product sheet. Requires authentication and organization access.

Returns: Updated `Product` object.

##### `delete_product(product_id: UUID)`

Delete an existing product sheet. Requires authentication and organization-level access. Only product sheets belonging to the authenticated organization can be deleted.

Returns: `bool` - True if deletion was successful.

### Data Models

#### Product

Main product model with fields:

- `id`: UUID
- `application`: Application (nested object)
- `network`: str (network enum value)
- `status`: str (status enum value)
- `name`: str (product name)
- `shopify_id`: Optional[str] (Shopify product ID if linked)
- `fields`: Dict[str, Any] (product information)
- `productFields`: Optional[List[DynamicFieldDef]] (schema for product fields)
- `passportsFields`: Optional[List[DynamicFieldDef]] (schema for individual passport items minted from this product)
- `certified_paths`: Optional[List[str]] (blockchain-certified fields)
- `created_at`: datetime
- `updated_at`: datetime

#### DynamicFieldDef

Defines the schema for dynamic fields. Each field definition has:

**Base properties (all types):**

- `name`: str (required) - Field name
- `label`: Optional[str] - Display label
- `required`: bool (default: False) - Whether field is required
- `type`: str (required) - One of the supported types below
- `default`: Optional[Any] - Default value

**Supported types and their specific properties:**

| Type | Description | Extra Properties |
|------|-------------|------------------|
| `number` | Numeric value | `min`, `max` |
| `string` | Single-line text | `minLength`, `maxLength` |
| `text` | Multi-line text | - |
| `url` | URL string | - |
| `image` | Image URL | - |
| `boolean` | True/false | - |
| `date` | ISO date string | `min`, `max` (ISO dates) |
| `enum` | Selection from list | `variants` (required) |
| `json` | Arbitrary JSON | - |
| `array` | List of items | `minLength`, `maxLength`, `itemsType` |
| `object` | Nested object | `fields` (list of DynamicFieldDef) |

**Examples:**

```python
from keyban_api_client import DynamicFieldDef

# Basic types
DynamicFieldDef(name="name", type="string", required=True, maxLength=100)
DynamicFieldDef(name="price", type="number", min=0, max=10000)
DynamicFieldDef(name="status", type="enum", variants=["pending", "approved", "rejected"])
DynamicFieldDef(name="expiryDate", type="date", min="2024-01-01", max="2030-12-31")

# Array of strings
DynamicFieldDef(name="tags", type="array", itemsType=DynamicFieldDef(name="[]", type="string"))

# Nested object
DynamicFieldDef(
    name="address",
    type="object",
    fields=[
        DynamicFieldDef(name="street", type="string", required=True),
        DynamicFieldDef(name="city", type="string", required=True),
    ]
)
```

#### ProductFields

Product data following standard product format:

- `name`: Optional[str]
- `description`: Optional[str]
- `brand`: Optional[str or Dict]
- `identifier`: Optional[str]
- `gtin`: Optional[str]
- `sku`: Optional[str]
- `countryOfOrigin`: Optional[str]
- `keywords`: Optional[List[str]]
- Additional fields allowed (extra="allow")

#### CreateProductRequest

For creating new products:

- `name`: str (required)
- `application`: UUID (required)
- `network`: str (required, default: "StarknetSepolia")
- `status`: str (required, default: "DRAFT")
- `fields`: Dict[str, Any] (required) - Product data conforming to productFields schema
- `productFields`: Optional[List[DynamicFieldDef]] - Schema for product-level fields
- `passportsFields`: Optional[List[DynamicFieldDef]] - Schema for individual passport items (e.g., serialNumber, manufacturingDate)
- `certified_paths`: Optional[List[str]] - Fields to certify on blockchain

#### UpdateProductRequest

For updating existing products (all fields optional):

- `status`: Optional[str]
- `name`: Optional[str]
- `fields`: Optional[Dict[str, Any]]
- `productFields`: Optional[List[DynamicFieldDef]]
- `passportsFields`: Optional[List[DynamicFieldDef]]
- `certified_paths`: Optional[List[str]]

## API Endpoints Covered

This client covers the following endpoints from the Keyban API Product controller:

- `GET /v1/dpp/products` - List products with filtering and pagination
- `GET /v1/dpp/products/:id` - Get product by ID
- `POST /v1/dpp/products` - Create product
- `PATCH /v1/dpp/products/:id` - Update product
- `DELETE /v1/dpp/products/:id` - Delete product

### Product Status Values

- `DRAFT` (default)
- `ACTIVE`
- `ARCHIVED`
- `UNLISTED`

## License

This client is part of the DAP (Digital Asset Platform) by Keyban project.
