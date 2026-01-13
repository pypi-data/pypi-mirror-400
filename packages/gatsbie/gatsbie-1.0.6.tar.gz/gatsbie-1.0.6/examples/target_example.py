"""Example usage of the Target SDK."""

import os
import sys

from gatsbie.target import (
    Client,
    NearbyStoresRequest,
    GetProductRequest,
    AddToCartRequest,
)


def main():
    # Get API key from environment
    api_key = os.environ.get("GATSBIE_API_KEY")
    if not api_key:
        print("GATSBIE_API_KEY environment variable is required")
        sys.exit(1)

    # Create client
    client = Client(api_key)

    # Health check
    print("=== Health Check ===")
    try:
        health = client.health()
        print(f"Status: {health.status}")
    except Exception as err:
        print(f"Health check failed: {err}")

    # Ping (get quota info)
    print("\n=== Ping ===")
    try:
        ping = client.ping()
        print(f"Message: {ping.message}")
        if ping.quota_used is not None:
            print(f"Quota: {ping.quota_used} / {ping.quota_limit}")
    except Exception as err:
        print(f"Ping failed: {err}")

    # Find nearby stores
    print("\n=== Nearby Stores ===")
    try:
        stores = client.get_nearby_stores(
            NearbyStoresRequest(
                lat=40.7147,
                lng=-74.0112,
                limit=5,
            )
        )
        for store in stores:
            print(
                f"- {store.name} ({store.city}, {store.state}) - "
                f"{store.distance_miles:.2f} miles"
            )
    except Exception as err:
        print(f"Failed to get nearby stores: {err}")

    # Get product details (requires proxy)
    proxy = os.environ.get("PROXY_URL")
    if proxy:
        print("\n=== Product Details ===")
        try:
            product = client.get_product(
                GetProductRequest(
                    tcin="86777236",
                    proxy=proxy,
                )
            )
            print(f"Title: {product.title}")
            print(f"Price: {product.current_price}")
            print(f"In Stock: {product.in_stock}")
            if product.on_sale:
                print(
                    f"On Sale! Save {product.savings_amount} "
                    f"({product.savings_percent}% off)"
                )
            if product.variations:
                print(f"Variations: {len(product.variations)}")
                for v in product.variations:
                    print(f"  - {v.name}: {v.value} ({v.current_price})")
        except Exception as err:
            print(f"Failed to get product: {err}")

    # Add to cart (requires proxy and access token)
    access_token = os.environ.get("TARGET_ACCESS_TOKEN")
    if proxy and access_token:
        print("\n=== Add to Cart ===")
        try:
            cart_resp = client.add_to_cart(
                AddToCartRequest(
                    tcin="94716087",
                    quantity=1,
                    access_token=access_token,
                    proxy=proxy,
                )
            )
            print(f"Success: {cart_resp.success}")
            print(f"Cart ID: {cart_resp.cart_id}")
            print(f"Items in Cart: {cart_resp.total_items_in_cart}")
            print(f"Item: {cart_resp.item_added.title}")
            print(f"Total: ${cart_resp.pricing.total:.2f}")
        except Exception as err:
            print(f"Failed to add to cart: {err}")


if __name__ == "__main__":
    main()
