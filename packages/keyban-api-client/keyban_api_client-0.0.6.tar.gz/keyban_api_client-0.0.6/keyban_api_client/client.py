"""
Keyban API Product Python Client

A Python client for interacting with the Keyban API Product API.
This client provides methods for CRUD operations on products.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

import requests
from pydantic import BaseModel, Field, field_validator


class DynamicFieldDef(BaseModel):
    """
    Dynamic field definition model.

    Supported types:
    - 'number': Numeric values with optional min/max constraints
    - 'string': Text with optional minLength/maxLength constraints
    - 'url': URL string
    - 'image': Image URL string
    - 'text': Multi-line text
    - 'boolean': True/false value
    - 'date': ISO date string with optional min/max constraints
    - 'enum': Selection from predefined variants
    - 'json': Arbitrary JSON value
    - 'array': List of items with recursive itemsType definition
    - 'object': Nested object with recursive fields definition
    """
    name: str
    label: Optional[str] = None
    required: bool = False
    type: str  # 'number', 'string', 'url', 'image', 'text', 'boolean', 'date', 'enum', 'json', 'array', 'object'

    # String/Array field options
    minLength: Optional[int] = None
    maxLength: Optional[int] = None

    # Number field options
    min: Optional[Union[float, str]] = None  # str for date type (ISO date)
    max: Optional[Union[float, str]] = None  # str for date type (ISO date)

    # Enum field options
    variants: Optional[List[str]] = None

    # Array field options (recursive)
    itemsType: Optional['DynamicFieldDef'] = None

    # Object field options (recursive)
    fields: Optional[List['DynamicFieldDef']] = None

    # Default value (type depends on field type)
    default: Optional[Any] = None

    model_config = {"extra": "allow"}


class ProductFields(BaseModel):
    """Dynamic product fields based on field definitions"""

    model_config = {"extra": "allow"}  # Use model_config for Pydantic v2

    def __init__(self, **data):
        """Initialize ProductFields with dynamic data"""
        super().__init__(**data)

    def model_dump(self, **kwargs):
        """Custom serialization to exclude null values"""
        data = super().model_dump(**kwargs)
        # Remove null/None values as API doesn't accept them
        return {k: v for k, v in data.items() if v is not None}


class Application(BaseModel):
    """Application model"""
    id: UUID
    shopifyShop: Optional[Union[str, Dict[str, Any]]] = None

    model_config = {"extra": "allow"}

class Product(BaseModel):
    """Keyban API DPP Product model"""
    id: UUID
    application: Union[Application, UUID, str]  # Handle both object and UUID formats
    network: str  # Network enum value
    status: str  # DppProductStatus enum value
    name: str  # Product name
    shopify_id: Optional[str] = Field(default=None, alias="shopifyId")  # Shopify product ID (if linked)
    fields: Optional[Dict[str, Any]] = None  # Dynamic product fields
    productFields: Optional[List[DynamicFieldDef]] = None  # Product field definitions
    passportsFields: Optional[List[DynamicFieldDef]] = None  # Passport field definitions
    certified_paths: Optional[List[str]] = Field(default=None, alias="certifiedPaths")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    @field_validator('application', mode='before')
    @classmethod
    def parse_application(cls, v):
        """Handle both Application object and UUID string formats"""
        if isinstance(v, str):
            # If it's a string UUID, convert to Application object
            return Application(id=UUID(v))
        elif isinstance(v, dict):
            # If it's a dict, use it as-is for Application parsing
            return v
        return v

    model_config = {"populate_by_name": True}


class CreateProductRequest(BaseModel):
    """Request model for creating a DPP product"""
    application: UUID
    network: str = "StarknetSepolia"
    status: str = "DRAFT"
    name: str
    fields: Optional[Dict[str, Any]] = None
    productFields: Optional[List[DynamicFieldDef]] = None
    passportsFields: Optional[List[DynamicFieldDef]] = None
    certified_paths: List[str] = Field(default_factory=list, alias="certifiedPaths")

    @field_validator('network')
    @classmethod
    def validate_network(cls, v):
        """Only StarknetSepolia network is currently supported"""
        if v != "StarknetSepolia":
            raise ValueError("Only StarknetSepolia network is currently supported")
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        """Validate product status"""
        valid_statuses = ["ACTIVE", "ARCHIVED", "DRAFT", "UNLISTED"]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
        return v

    model_config = {"populate_by_name": True}


class UpdateProductRequest(BaseModel):
    """Request model for updating a DPP product"""
    network: Optional[str] = None
    status: Optional[str] = None
    name: Optional[str] = None
    fields: Optional[Dict[str, Any]] = None
    productFields: Optional[List[DynamicFieldDef]] = None
    passportsFields: Optional[List[DynamicFieldDef]] = None
    certified_paths: Optional[List[str]] = Field(default=None, alias="certifiedPaths")

    @field_validator('network')
    @classmethod
    def validate_network(cls, v):
        """Only StarknetSepolia network is currently supported"""
        if v is not None and v != "StarknetSepolia":
            raise ValueError("Only StarknetSepolia network is currently supported")
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        """Validate product status"""
        if v is not None:
            valid_statuses = ["ACTIVE", "ARCHIVED", "DRAFT", "UNLISTED"]
            if v not in valid_statuses:
                raise ValueError(f"Status must be one of: {valid_statuses}")
        return v

    model_config = {"populate_by_name": True}


class ProductListResponse(BaseModel):
    """Response model for listing products"""
    data: List[Product]
    total: int


class FilterOperator(BaseModel):
    """Filter operator for querying"""
    field: str
    operator: str  # 'eq', 'contains', 'gt', 'lt'
    value: Any


class QueryParams(BaseModel):
    """Query parameters for listing products"""
    filters: Optional[List[FilterOperator]] = None
    current_page: Optional[int] = Field(default=1, alias="currentPage")
    page_size: Optional[int] = Field(default=10, alias="pageSize")

    model_config = {"populate_by_name": True}


class ProductClient:
    """
    Python client for interacting with Keyban API DPP Product endpoints.

    Supports the following operations:
    - List products with filtering and pagination
    - Get a specific product by ID
    - Create a new product
    - Update an existing product
    - Delete an existing product

    The list_products() method supports filtering using FilterOperator objects.
    Supported filter fields: application.id (eq only), name (eq, contains)
    Supported network: StarknetSepolia (default)
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        api_version: str = "v1",
        timeout: int = 30
    ):
        """
        Initialize the Keyban API DPP Product client.

        Args:
            base_url: Base URL of the API (e.g., "https://api.keyban.io")
            api_key: API key for authentication (required)
            api_version: API version (default: "v1")
            timeout: Request timeout in seconds (default: 30)
        """
        self.base_url = base_url.rstrip('/')
        self.api_version = api_version
        self.timeout = timeout

        self.session = requests.Session()
        self.session.headers.update({
            "X-Api-Key": api_key,
            "Content-Type": "application/json"
        })

    def _get_endpoint_url(self, path: str = "") -> str:
        """Get the full endpoint URL"""
        path = path.lstrip('/')
        return f"{self.base_url}/{self.api_version}/dpp/products/{path}".rstrip('/')

    def _make_request(
        self,
        method: str,
        path: str = "",
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        exclude_content_type: bool = False
    ) -> requests.Response:
        """
        Make HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, PATCH, DELETE, etc.)
            path: URL path to append to base endpoint
            params: Query parameters
            data: Form data
            json_data: JSON body data
            exclude_content_type: If True, removes Content-Type header (useful for DELETE)

        Returns:
            requests.Response object
        """
        url = self._get_endpoint_url(path)

        headers = None
        if exclude_content_type:
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}

        response = self.session.request(
            method=method,
            url=url,
            params=params,
            data=data,
            json=json_data,
            headers=headers,
            timeout=self.timeout
        )

        response.raise_for_status()
        return response

    def list_products(
        self,
        filters: Optional[List[FilterOperator]] = None,
        current_page: int = 1,
        page_size: int = 10
    ) -> ProductListResponse:
        """
        List DPP products with filtering and pagination.

        Args:
            filters: List of FilterOperator objects for filtering (optional)
            current_page: Page number (1-based, default: 1)
            page_size: Number of items per page (default: 10, max: 100)

        Returns:
            ProductListResponse containing the list of products and total count

        Supported filter fields and operators:
            - application.id: Application UUID (eq only)
            - name: Product name (eq for exact match, contains for substring search)

        Examples:
            # List all products (no filters)
            all_products = client.list_products()

            # Filter by application ID (exact match only)
            app_filter = FilterOperator(field="application.id", operator="eq", value=str(app_id))
            products = client.list_products(filters=[app_filter])

            # Filter by product name (exact match)
            name_filter = FilterOperator(field="name", operator="eq", value="My Product")
            products = client.list_products(filters=[name_filter])

            # Filter by product name (substring search, case-insensitive)
            name_filter = FilterOperator(field="name", operator="contains", value="Nike")
            products = client.list_products(filters=[name_filter])

            # Combine filters
            filters = [
                FilterOperator(field="application.id", operator="eq", value=str(app_id)),
                FilterOperator(field="name", operator="contains", value="Product")
            ]
            products = client.list_products(filters=filters)
        """
        params = {
            "currentPage": current_page,
            "pageSize": min(page_size, 100)  # Enforce max page size
        }

        # Add filters as properly formatted query parameters
        if filters:
            for i, filter_obj in enumerate(filters):
                params[f"filters[{i}][field]"] = filter_obj.field
                params[f"filters[{i}][operator]"] = filter_obj.operator
                params[f"filters[{i}][value]"] = str(filter_obj.value)

        response = self._make_request("GET", params=params)
        return ProductListResponse(**response.json())

    def get_product(self, product_id: UUID) -> Product:
        """
        Get a specific product by its ID.

        This endpoint is public and doesn't require authentication.

        Args:
            product_id: The UUID of the product

        Returns:
            Product object

        Raises:
            requests.HTTPError: If the product is not found (404) or other HTTP errors
        """
        response = self._make_request("GET", str(product_id))
        return Product(**response.json())

    def create_product(self, product_data: CreateProductRequest) -> Product:
        """
        Create a new DPP product.

        Requires authentication and organization-level access.

        Args:
            product_data: The product data to create

        Returns:
            Created Product object

        Raises:
            requests.HTTPError: If the application is not found (404) or other HTTP errors
        """
        # Convert Pydantic model to dict, handling aliases and converting UUIDs to strings
        json_data = product_data.model_dump(by_alias=True, exclude_unset=True, mode='json')

        response = self._make_request("POST", json_data=json_data)
        return Product(**response.json())

    def update_product(
        self,
        product_id: UUID,
        update_data: UpdateProductRequest
    ) -> Product:
        """
        Update an existing DPP product.

        Requires authentication and organization-level access.
        Only products belonging to the authenticated organization can be updated.

        Args:
            product_id: The UUID of the product to update
            update_data: The updated product data

        Returns:
            Updated Product object

        Raises:
            requests.HTTPError: If the product is not found (404) or other HTTP errors
        """
        # Convert Pydantic model to dict, excluding unset fields and handling aliases
        json_data = update_data.model_dump(by_alias=True, exclude_unset=True, mode='json')
        # Remove None values as API might not accept them
        json_data = {k: v for k, v in json_data.items() if v is not None}

        response = self._make_request("PATCH", str(product_id), json_data=json_data)
        return Product(**response.json())

    def delete_product(self, product_id: UUID) -> bool:
        """
        Delete an existing DPP product.

        Requires authentication and organization-level access.
        Only products belonging to the authenticated organization can be deleted.

        Args:
            product_id: The UUID of the product to delete

        Returns:
            bool: True if deletion was successful

        Raises:
            requests.HTTPError: If the product is not found (404) or other HTTP errors
        """
        response = self._make_request("DELETE", str(product_id), json_data={})

        # DELETE typically returns 204 No Content on success
        return response.status_code in [200, 204]

    def close(self):
        """Close the HTTP session"""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Convenience functions for filter creation
def create_filter(field: str, operator: str, value: Any) -> FilterOperator:
    """
    Create a FilterOperator for use with list_products.

    Args:
        field: Field to filter on ("application.id" or "name")
        operator: Filter operator ("eq" or "contains")
        value: Value to filter by

    Returns:
        FilterOperator object

    Supported fields and operators:
        - application.id: eq only
        - name: eq (exact match) or contains (substring search)

    Examples:
        # Filter by application ID
        app_filter = create_filter("application.id", "eq", str(app_id))

        # Filter by name (exact match)
        name_filter = create_filter("name", "eq", "My Product")

        # Filter by name (substring search)
        name_filter = create_filter("name", "contains", "Nike")

        # Multiple filters example
        filters = [
            create_filter("application.id", "eq", str(app_id)),
            create_filter("name", "contains", "Product")
        ]
        products = client.list_products(filters=filters)
    """
    return FilterOperator(field=field, operator=operator, value=value)


# Convenience functions for common operations
def search_products_by_application_id(
    client: ProductClient,
    application_id: UUID,
    page_size: int = 100
) -> List[Product]:
    """
    Convenience function to search for DPP products by application ID.

    Args:
        client: ProductClient instance
        application_id: Application ID to filter by
        page_size: Number of results to return (default: 100)

    Returns:
        List of matching Product objects
    """
    filters = [
        FilterOperator(field="application.id", operator="eq", value=str(application_id))
    ]

    response = client.list_products(
        filters=filters,
        page_size=page_size
    )

    return response.data
