import asyncio
import httpx

async def simulate_scan_devices_call():
    """
    Simulates an API call to the /scan-devices endpoint and prints the result.
    """
    url = "http://127.0.0.1:8000/scan-devices"  # URL of the API endpoint

    async with httpx.AsyncClient() as client:
        try:
            # Make the GET request to the /scan-devices endpoint
            response = await client.get(url)

            # Print the status code and JSON response
            print(f"Status Code: {response.status_code}")
            print("Response JSON:")
            print(response.json())
        except httpx.RequestError as e:
            print(f"An error occurred while making the request: {e}")

# Run the simulation
if __name__ == "__main__":
    asyncio.run(simulate_scan_devices_call())