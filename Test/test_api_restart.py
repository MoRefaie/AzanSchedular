import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def simulate_scan_devices_call():
    """
    Simulates an API call to the /scan-devices endpoint and logs the result.
    """
    url = "http://127.0.0.1:8000/api/restart-scheduler"  # URL of the API endpoint

    try:
        # Make the GET request to the /scan-devices endpoint
        response = requests.get(url)

        # Log the status code
        logging.info(f"Status Code: {response.status_code}")

        # Parse the JSON response
        response_json = response.json()

        # Log the full JSON response as a Python dictionary
        logging.info("Full Response Dictionary:")
        logging.info(response_json)

        # Check if 'data' exists and contains 'devices'
        if "data" in response_json and isinstance(response_json["data"], dict):
            data_json = response_json["data"]
            if "devices" in data_json:
                logging.info("\nDevices Dictionary:")
                logging.info(data_json["devices"])
            else:
                logging.warning("The 'devices' key is not present in the 'data' dictionary.")
        else:
            logging.warning("The 'data' key is not present or is not a dictionary in the response.")
    except requests.RequestException as e:
        logging.error(f"An error occurred while making the request: {e}")
    except ValueError as e:
        logging.error(f"An error occurred while parsing the JSON response: {e}")

# Run the simulation
if __name__ == "__main__":
    simulate_scan_devices_call()