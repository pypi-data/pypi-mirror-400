"""Target API client."""

from typing import Any, Dict, List, Optional

import httpx

from .errors import APIError, RequestError
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

DEFAULT_BASE_URL = "https://target.gatsbie.io"
DEFAULT_TIMEOUT = 120.0


class Client:
    """Target API client.

    Args:
        api_key: Your Gatsbie API key (should start with 'gats_').
        base_url: Custom base URL for the API (optional).
        timeout: Request timeout in seconds (default: 120).
        http_client: Custom httpx.Client instance (optional).

    Example:
        >>> from gatsbie.target import Client, NearbyStoresRequest, GetProductRequest
        >>> client = Client("gats_your_api_key")
        >>>
        >>> # Find nearby stores
        >>> stores = client.get_nearby_stores(NearbyStoresRequest(
        ...     lat=40.7147,
        ...     lng=-74.0112,
        ...     limit=5,
        ... ))
        >>>
        >>> # Get product details
        >>> product = client.get_product(GetProductRequest(
        ...     tcin="86777236",
        ...     proxy="http://user:pass@host:port",
        ... ))
        >>> print(product.title, product.current_price)
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        http_client: Optional[httpx.Client] = None,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self._client = http_client or httpx.Client(timeout=timeout)
        self._owns_client = http_client is None

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def close(self) -> None:
        """Close the HTTP client."""
        if self._owns_client:
            self._client.close()

    def _request(
        self,
        method: str,
        path: str,
        body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an authenticated request to the API."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        try:
            response = self._client.request(
                method,
                f"{self.base_url}{path}",
                headers=headers,
                json=body,
            )
        except httpx.RequestError as e:
            raise RequestError(f"Request failed: {e}") from e

        data = response.json()

        if response.status_code >= 400:
            raise APIError(
                message=data.get("error", "Unknown error"),
                status=data.get("status"),
                details=data.get("details"),
                suggestion=data.get("suggestion"),
                code=data.get("code"),
                http_status=response.status_code,
            )

        return data

    def _get(self, path: str) -> Dict[str, Any]:
        """Make a GET request."""
        return self._request("GET", path)

    def _post(self, path: str, body: Dict[str, Any]) -> Dict[str, Any]:
        """Make a POST request."""
        return self._request("POST", path, body)

    # ========================================================================
    # API Methods
    # ========================================================================

    def health(self) -> HealthResponse:
        """Check the API server health status.

        Returns:
            HealthResponse with the server status.
        """
        data = self._get("/health")
        return HealthResponse(status=data["status"])

    def ping(self) -> PingResponse:
        """Ping the API and get quota information.

        Returns:
            PingResponse with message and quota info.
        """
        data = self._get("/api/v1/ping")
        return PingResponse(
            message=data["message"],
            quota_used=data.get("quota_used"),
            quota_limit=data.get("quota_limit"),
        )

    def get_nearby_stores(self, request: NearbyStoresRequest) -> List[StoreResponse]:
        """Find nearby Target stores.

        Args:
            request: The nearby stores request parameters.

        Returns:
            List of nearby stores sorted by distance.
        """
        params = [f"lat={request.lat}", f"lng={request.lng}"]
        if request.limit is not None:
            params.append(f"limit={request.limit}")
        if request.radius is not None:
            params.append(f"radius={request.radius}")

        path = f"/api/v1/stores/nearby?{'&'.join(params)}"
        data = self._get(path)

        return [
            StoreResponse(
                id=store["id"],
                name=store["name"],
                address=store["address"],
                city=store["city"],
                state=store["state"],
                postal_code=store["postalCode"],
                latitude=store["latitude"],
                longitude=store["longitude"],
                drive_up_enabled=store["driveUpEnabled"],
                distance_miles=store["distanceMiles"],
            )
            for store in data
        ]

    def get_product(self, request: GetProductRequest) -> ProductResponse:
        """Get detailed product information.

        Args:
            request: The product request parameters.

        Returns:
            Product details including pricing, availability, and variations.
        """
        if not request.tcin:
            raise APIError(message="tcin is required", http_status=400)
        if not request.proxy:
            raise APIError(message="proxy is required", http_status=400)

        params = [f"proxy={request.proxy}"]
        if request.store_id:
            params.append(f"store_id={request.store_id}")

        path = f"/api/v1/products/{request.tcin}?{'&'.join(params)}"
        data = self._get(path)

        variations = None
        if data.get("variations"):
            variations = [
                ProductVariation(
                    tcin=v["tcin"],
                    name=v["name"],
                    value=v["value"],
                    swatch_image_url=v.get("swatch_image_url"),
                    primary_image_url=v["primary_image_url"],
                    current_price=v["current_price"],
                    in_stock=v["in_stock"],
                    available_for_shipping=v["available_for_shipping"],
                    available_for_pickup=v["available_for_pickup"],
                )
                for v in data["variations"]
            ]

        return ProductResponse(
            tcin=data["tcin"],
            title=data["title"],
            current_price=data["current_price"],
            regular_price=data.get("regular_price"),
            on_sale=data["on_sale"],
            savings_amount=data.get("savings_amount"),
            savings_percent=data.get("savings_percent"),
            primary_image_url=data["primary_image_url"],
            in_stock=data["in_stock"],
            available_for_shipping=data["available_for_shipping"],
            available_for_pickup=data["available_for_pickup"],
            free_shipping_available=data["free_shipping_available"],
            rating_average=data.get("rating_average"),
            rating_count=data.get("rating_count"),
            review_count=data.get("review_count"),
            variations=variations,
        )

    def add_to_cart(self, request: AddToCartRequest) -> AddToCartResponse:
        """Add an item to the Target shopping cart.

        Args:
            request: The add to cart request parameters.

        Returns:
            Cart update response with item details and pricing.
        """
        if not request.tcin:
            raise APIError(message="tcin is required", http_status=400)
        if request.quantity < 1:
            raise APIError(message="quantity must be at least 1", http_status=400)
        if not request.access_token:
            raise APIError(message="access_token is required", http_status=400)
        if not request.proxy:
            raise APIError(message="proxy is required", http_status=400)

        # Validate fulfillment type requires store_id
        if request.fulfillment_type in (
            FulfillmentType.CURBSIDE,
            FulfillmentType.STORE_PICKUP,
        ) and not request.store_id:
            raise APIError(
                message="store_id is required when fulfillment_type is CURBSIDE or STORE_PICKUP",
                http_status=400,
            )

        body: Dict[str, Any] = {
            "tcin": request.tcin,
            "quantity": request.quantity,
            "access_token": request.access_token,
            "proxy": request.proxy,
        }
        if request.fulfillment_type:
            body["fulfillment_type"] = request.fulfillment_type.value
        if request.store_id:
            body["store_id"] = request.store_id

        data = self._post("/api/v1/cart/items", body)

        item_added = AddedItemSummary(
            tcin=data["item_added"]["tcin"],
            title=data["item_added"]["title"],
            image_url=data["item_added"]["image_url"],
            quantity=data["item_added"]["quantity"],
            unit_price=data["item_added"]["unit_price"],
            subtotal=data["item_added"]["subtotal"],
        )

        fulfillment = FulfillmentSummary(
            type=data["fulfillment"]["type"],
            estimated_date=data["fulfillment"]["estimated_date"],
            store_name=data["fulfillment"].get("store_name"),
            pickup_hours=data["fulfillment"].get("pickup_hours"),
        )

        pricing = PricingSummary(
            item_total=data["pricing"]["item_total"],
            shipping=data["pricing"]["shipping"],
            tax=data["pricing"]["tax"],
            total=data["pricing"]["total"],
        )

        return_policy = None
        if data.get("return_policy"):
            return_policy = ReturnPolicySummary(
                days=data["return_policy"]["days"],
                days_with_circle=data["return_policy"]["days_with_circle"],
            )

        return AddToCartResponse(
            success=data["success"],
            message=data.get("message"),
            cart_id=data["cart_id"],
            total_items_in_cart=data["total_items_in_cart"],
            item_added=item_added,
            fulfillment=fulfillment,
            pricing=pricing,
            return_policy=return_policy,
        )
