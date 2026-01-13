"""
Keyban API Client

A Python client library for interacting with the Keyban API Product management.
This library provides a simple and intuitive interface for managing products
in your applications.
"""

from ._version import __version__
from .client import (
    ProductClient,
    ProductFields,
    Product,
    Application,
    DynamicFieldDef,
    CreateProductRequest,
    UpdateProductRequest,
    ProductListResponse,
    FilterOperator,
    QueryParams,
    create_filter,
    search_products_by_application_id,
)

__author__ = "Keyban"
__email__ = "support@keyban.io"

__all__ = [
    "ProductClient",
    "ProductFields",
    "Product",
    "Application",
    "DynamicFieldDef",
    "CreateProductRequest",
    "UpdateProductRequest",
    "ProductListResponse",
    "FilterOperator",
    "QueryParams",
    "create_filter",
    "search_products_by_application_id",
    "__version__",
]
