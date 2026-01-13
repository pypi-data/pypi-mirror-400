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
from uuid import UUID
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
]

# Create the product data (must conform to schema)
product_data = ProductFields(
    name="My Test Product",
    description="A product created via Python client"
)

request = CreateProductRequest(
    name="My Test Product",
    application=UUID("your-application-id"),
    status="ACTIVE",
    productFields=product_fields_schema,  # Schema definition
    fields=product_data.model_dump(),     # Data conforming to schema
    certified_paths=["name", "description"]
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

### Full Product Creation with Dynamic Field Schema

```python
from uuid import UUID
from keyban_api_client import ProductClient, ProductFields, CreateProductRequest, DynamicFieldDef

# Initialize client
client = ProductClient(
    base_url="https://api.prod.keyban.io",
    api_key="your-api-key"
)

# Define the schema for allowed product fields
product_fields_schema = [
    # Basic fields
    DynamicFieldDef(name="identifier", type="string", required=True),
    DynamicFieldDef(name="name", type="string", required=True, minLength=1, maxLength=200),
    DynamicFieldDef(name="description", type="text"),
    DynamicFieldDef(name="image", type="image"),
    DynamicFieldDef(name="gtin", type="string", minLength=8, maxLength=14),
    DynamicFieldDef(name="sku", type="string", required=True),

    # Nested object field
    DynamicFieldDef(
        name="brand",
        type="object",
        fields=[
            DynamicFieldDef(name="name", type="string", required=True),
            DynamicFieldDef(name="identifier", type="string"),
        ]
    ),

    # Enum field
    DynamicFieldDef(
        name="category",
        type="enum",
        variants=["Electronics", "Clothing", "Food", "Other"]
    ),

    # Array field
    DynamicFieldDef(name="keywords", type="array", itemsType=DynamicFieldDef(name="[]", type="string")),

    # Number field with constraints
    DynamicFieldDef(name="price", type="number", min=0),

    # Nested manufacturer object
    DynamicFieldDef(
        name="manufacturer",
        type="object",
        fields=[
            DynamicFieldDef(name="name", type="string", required=True),
            DynamicFieldDef(name="location", type="string"),
            DynamicFieldDef(
                name="certifications",
                type="array",
                itemsType=DynamicFieldDef(name="[]", type="string")
            ),
        ]
    ),
]

# Define schema for passport fields (individual items minted from this product)
passport_fields_schema = [
    DynamicFieldDef(name="serialNumber", type="string", required=True),
    DynamicFieldDef(name="manufacturingDate", type="date"),
    DynamicFieldDef(name="batchId", type="string"),
]

# Create product data (must conform to productFields schema)
product_data = ProductFields(
    identifier="PROD-001",
    name="Organic Cotton T-Shirt",
    description="Sustainably produced cotton t-shirt",
    image="https://example.com/product.jpg",
    gtin="1234567890123",
    sku="ECO-TS-M-BLU",
    brand={"name": "EcoWear", "identifier": "ecowear-brand"},
    category="Clothing",
    keywords=["organic", "cotton", "sustainable"],
    price=29.99,
    manufacturer={
        "name": "EcoTextiles Ltd",
        "location": "Istanbul, Turkey",
        "certifications": ["GOTS", "OEKO-TEX"]
    }
)

# Create with schema and certification
request = CreateProductRequest(
    name=product_data.name,
    application=UUID("your-application-id"),
    status="ACTIVE",
    productFields=product_fields_schema,    # Schema for product-level fields
    passportsFields=passport_fields_schema,  # Schema for passport-level fields
    fields=product_data.model_dump(),        # Actual data conforming to productFields
    certified_paths=["name", "brand", "gtin", "sku"]  # Fields to certify on blockchain
)

product = client.create_product(request)
client.close()
```

## Product Sheet Certification

Product sheets are certified on the blockchain using the `certifiedPaths` field. This field points to specific fields within `product.data` that will be digitally signed and recorded on the blockchain.

### How Certification Works

1. **Certified Paths**: The `certifiedPaths` field contains an array of JSON paths pointing to fields in the product data that should be certified
2. **Automatic Triggering**: Certification events are automatically triggered when:
   - `certifiedPaths` field is updated
   - Any data field pointed to by `certifiedPaths` changes (during create or update operations)
   - **Important**: Certification is only triggered when the product sheet status is "active" (case-insensitive)
3. **Blockchain Event**: A new blockchain event is emitted containing:
   - IPFS CID pointing to the certified data
   - Certifier signature
   - Product ID

### Example: Creating a Product with Certification

```python
from uuid import UUID
from keyban_api_client import ProductFields, CreateProductRequest, UpdateProductRequest, DynamicFieldDef

# Define the schema - this validates what fields are allowed
product_fields_schema = [
    DynamicFieldDef(name="identifier", type="string", required=True),
    DynamicFieldDef(name="name", type="string", required=True),
    DynamicFieldDef(name="description", type="text"),
    DynamicFieldDef(name="image", type="image"),
    DynamicFieldDef(name="gtin", type="string"),
    DynamicFieldDef(name="sku", type="string"),
    DynamicFieldDef(
        name="brand",
        type="object",
        fields=[
            DynamicFieldDef(name="name", type="string", required=True),
            DynamicFieldDef(name="identifier", type="string"),
            DynamicFieldDef(name="description", type="text"),
        ]
    ),
    DynamicFieldDef(name="countryOfOrigin", type="string"),
    DynamicFieldDef(name="keywords", type="array", itemsType=DynamicFieldDef(name="[]", type="string")),
    DynamicFieldDef(name="material", type="string"),
    DynamicFieldDef(name="certification", type="string"),
    DynamicFieldDef(
        name="manufacturer",
        type="object",
        fields=[
            DynamicFieldDef(name="name", type="string", required=True),
            DynamicFieldDef(name="location", type="string"),
            DynamicFieldDef(name="certifications", type="array", itemsType=DynamicFieldDef(name="[]", type="string")),
        ]
    ),
    DynamicFieldDef(
        name="sustainability",
        type="object",
        fields=[
            DynamicFieldDef(name="carbonFootprint", type="string"),
            DynamicFieldDef(name="waterUsage", type="string"),
            DynamicFieldDef(name="recyclable", type="boolean"),
        ]
    ),
]

# Create product data conforming to schema
product_data = ProductFields(
    identifier="PROD-001",
    name="Organic Cotton T-Shirt",
    description="Sustainably produced cotton t-shirt",
    image="https://example.com/product.jpg",
    gtin="1234567890123",
    sku="ECO-TS-M-BLU",
    brand={
        "name": "EcoWear",
        "identifier": "ecowear-brand",
        "description": "Sustainable fashion brand"
    },
    countryOfOrigin="TR",
    keywords=["organic", "cotton", "sustainable", "GOTS"],
    material="100% Organic Cotton",
    certification="GOTS Certified",
    manufacturer={
        "name": "EcoTextiles Ltd",
        "location": "Istanbul, Turkey",
        "certifications": ["GOTS", "OEKO-TEX"]
    },
    sustainability={
        "carbonFootprint": "2.1 kg CO2",
        "waterUsage": "2700L",
        "recyclable": True
    }
)

# Create product with schema and certification
request = CreateProductRequest(
    name=product_data.name,
    application=UUID("your-app-id"),
    status="ACTIVE",
    productFields=product_fields_schema,  # Schema definition
    fields=product_data.model_dump(),     # Data conforming to schema
    certified_paths=[
        "identifier",
        "name",
        "description",
        "image",
        "gtin",
        "sku",
        "brand.name",
        "brand.identifier",
        "countryOfOrigin",
    ]
)

# Create the product - certification job will be automatically triggered
product = client.create_product(request)

# Later updates to certified fields will trigger new certification events
update_data = UpdateProductRequest(
    fields=ProductFields(
        name="Updated Product Name",
        description="Updated product description",
        keywords=["updated", "product"]
    ).model_dump(),
    certified_paths=["name", "description"]  # Re-certify updated fields
)
client.update_product(product.id, update_data)
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
    sheets = client.list_products()
except requests.HTTPError as e:
    if e.response.status_code == 401:
        print("Authentication failed")
    elif e.response.status_code == 404:
        print("Resource not found")
    else:
        print(f"HTTP error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Pagination

```python
# Get all product sheets across multiple pages
all_sheets = []
page = 1
page_size = 50

while True:
    response = client.list_products(
        current_page=page,
        page_size=page_size
    )

    all_sheets.extend(response.data)

    # Check if we've got all sheets
    if len(response.data) < page_size:
        break

    page += 1

print(f"Retrieved {len(all_sheets)} total product sheets")
```

### Context Manager Usage

```python
# Automatically close the session
with ProductClient(base_url="...", api_key="...") as client:
    sheets = client.list_products()
    # Client automatically closed when exiting the context
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
- `passportsFields`: Optional[List[DynamicFieldDef]] (schema for passport fields)
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

# Simple string field
name_field = DynamicFieldDef(name="name", type="string", required=True, maxLength=100)

# Number with constraints
price_field = DynamicFieldDef(name="price", type="number", min=0, max=10000)

# Enum field
status_field = DynamicFieldDef(
    name="status",
    type="enum",
    variants=["pending", "approved", "rejected"]
)

# Date field with range
date_field = DynamicFieldDef(
    name="expiryDate",
    type="date",
    min="2024-01-01",
    max="2030-12-31"
)

# Array of strings
tags_field = DynamicFieldDef(
    name="tags",
    type="array",
    itemsType=DynamicFieldDef(name="[]", type="string")
)

# Nested object
address_field = DynamicFieldDef(
    name="address",
    type="object",
    fields=[
        DynamicFieldDef(name="street", type="string", required=True),
        DynamicFieldDef(name="city", type="string", required=True),
        DynamicFieldDef(name="zipCode", type="string"),
    ]
)

# Array of objects
items_field = DynamicFieldDef(
    name="items",
    type="array",
    minLength=1,
    itemsType=DynamicFieldDef(
        name="[]",
        type="object",
        fields=[
            DynamicFieldDef(name="sku", type="string", required=True),
            DynamicFieldDef(name="quantity", type="number", min=1),
        ]
    )
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
- `passportsFields`: Optional[List[DynamicFieldDef]] - Schema for passport-level fields
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
