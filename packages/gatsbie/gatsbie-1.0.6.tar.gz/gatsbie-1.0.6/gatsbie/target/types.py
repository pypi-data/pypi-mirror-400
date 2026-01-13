"""Type definitions for the Target SDK."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


# ============================================================================
# Response Types
# ============================================================================


@dataclass
class HealthResponse:
    """Response from the health check endpoint."""

    status: str


@dataclass
class PingResponse:
    """Response from the ping endpoint."""

    message: str
    quota_used: Optional[int] = None
    quota_limit: Optional[int] = None


@dataclass
class StoreResponse:
    """Target store with distance information."""

    id: int
    name: str
    address: str
    city: str
    state: str
    postal_code: str
    latitude: float
    longitude: float
    drive_up_enabled: bool
    distance_miles: float


@dataclass
class ProductVariation:
    """Product variation information (color, size, etc.)."""

    tcin: str
    name: str
    value: str
    primary_image_url: str
    current_price: str
    in_stock: bool
    available_for_shipping: bool
    available_for_pickup: bool
    swatch_image_url: Optional[str] = None


@dataclass
class ProductResponse:
    """Product details response."""

    tcin: str
    title: str
    current_price: str
    primary_image_url: str
    in_stock: bool
    available_for_shipping: bool
    available_for_pickup: bool
    free_shipping_available: bool
    on_sale: bool
    regular_price: Optional[str] = None
    savings_amount: Optional[str] = None
    savings_percent: Optional[float] = None
    rating_average: Optional[float] = None
    rating_count: Optional[int] = None
    review_count: Optional[int] = None
    variations: Optional[List[ProductVariation]] = None


@dataclass
class AddedItemSummary:
    """Summary of item added to cart."""

    tcin: str
    title: str
    image_url: str
    quantity: int
    unit_price: float
    subtotal: float


@dataclass
class FulfillmentSummary:
    """Fulfillment details for cart items."""

    type: str
    estimated_date: str
    store_name: Optional[str] = None
    pickup_hours: Optional[int] = None


@dataclass
class PricingSummary:
    """Price breakdown for cart items."""

    item_total: float
    shipping: float
    tax: float
    total: float


@dataclass
class ReturnPolicySummary:
    """Return policy information."""

    days: int
    days_with_circle: int


@dataclass
class AddToCartResponse:
    """Response after adding item to cart."""

    success: bool
    cart_id: str
    total_items_in_cart: int
    item_added: AddedItemSummary
    fulfillment: FulfillmentSummary
    pricing: PricingSummary
    message: Optional[str] = None
    return_policy: Optional[ReturnPolicySummary] = None


# ============================================================================
# Request Types
# ============================================================================


@dataclass
class NearbyStoresRequest:
    """Request for finding nearby stores."""

    lat: float
    lng: float
    limit: Optional[int] = None
    radius: Optional[float] = None


@dataclass
class GetProductRequest:
    """Request for getting product details."""

    tcin: str
    proxy: str
    store_id: Optional[str] = None


class FulfillmentType(str, Enum):
    """Fulfillment type for cart items."""

    SHIP = "SHIP"
    CURBSIDE = "CURBSIDE"
    STORE_PICKUP = "STORE_PICKUP"


@dataclass
class AddToCartRequest:
    """Request for adding item to cart."""

    tcin: str
    quantity: int
    access_token: str
    proxy: str
    fulfillment_type: Optional[FulfillmentType] = None
    store_id: Optional[str] = None
