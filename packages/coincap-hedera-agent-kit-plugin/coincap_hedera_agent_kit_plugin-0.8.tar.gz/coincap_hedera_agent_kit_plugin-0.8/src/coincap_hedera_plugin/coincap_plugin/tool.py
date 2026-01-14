import requests
import os


# Use the CoinCap API to get the current price in USD of one HBAR
def get_hbar_price_from_coincap():
    headers = {"Authorization": f"Bearer {os.getenv("COINCAP_BEARER_TOKEN")}"}

    # Send GET request
    response = requests.get(
        "https://rest.coincap.io/v3/price/bysymbol/hbar", headers=headers
    )

    # Raise an error if the request failed (4xx / 5xx)
    response.raise_for_status()

    # Parse JSON response
    json_data = response.json()

    # Get the first element from the "data" array and convert it to float
    first_value = float(json_data["data"][0])

    print(f"* got this value from coincap api {first_value}")

    return first_value
