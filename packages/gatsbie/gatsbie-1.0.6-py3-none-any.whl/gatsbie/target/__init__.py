"""Target SDK - Official Python SDK for the Target API."""

from .client import Client
from .errors import (
    APIError,
    ERR_INTERNAL_ERROR,
    ERR_INVALID_REQUEST,
    ERR_INVENTORY_UNAVAILABLE,
    ERR_NOT_FOUND,
    ERR_UNAUTHORIZED,
    ERR_UPSTREAM_ERROR,
    RequestError,
    TargetError,
)
from .types import (
    AddedItemSummary,
    AddToCartRequest,
    AddToCartResponse,
    FulfillmentSummary,
    FulfillmentType,
    GetProductRequest,
    HealthResponse,
    NearbyStoresRequest,
    PingResponse,
    PricingSummary,
    ProductResponse,
    ProductVariation,
    ReturnPolicySummary,
    StoreResponse,
)

__all__ = [
    # Client
    "Client",
    # Errors
    "TargetError",
    "APIError",
    "RequestError",
    "ERR_UNAUTHORIZED",
    "ERR_INVALID_REQUEST",
    "ERR_NOT_FOUND",
    "ERR_UPSTREAM_ERROR",
    "ERR_INTERNAL_ERROR",
    "ERR_INVENTORY_UNAVAILABLE",
    # Types
    "HealthResponse",
    "PingResponse",
    "StoreResponse",
    "NearbyStoresRequest",
    "ProductResponse",
    "ProductVariation",
    "GetProductRequest",
    "FulfillmentType",
    "AddToCartRequest",
    "AddedItemSummary",
    "FulfillmentSummary",
    "PricingSummary",
    "ReturnPolicySummary",
    "AddToCartResponse",
]
