import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def simulate_config_update_param_call():
    """
    Simulates an API call to the /update-config endpoint and logs the result.
    """
    url = "http://127.0.0.1:8000/api/update-config"  # URL of the API endpoint

    # JSON payload to send to the API
    payload = {
        "updates": {
            # "AZAN_SWITCHES": {"Fajr": "On", "Sunrise": "Off", "Dhuhr": "On", "Asr": "On", "Maghrib": "On", "Isha": "On"},
            # "SHORT_AZAN_SWITCHES":{"Fajr": "Off", "Sunrise": "Off", "Dhuhr": "Off", "Asr": "Off", "Maghrib": "Off", "Isha": "Off"},
            "AUDIO_VOLUME": "50.0",
        }
    }

    try:
        # Make the POST request to the /update-config endpoint
        response = requests.post(url, json=payload)

        # Log the status code
        logging.info(f"Status Code: {response.status_code}")

        # Parse the JSON response
        response_json = response.json()

        # Log the full JSON response as a Python dictionary
        logging.info("Full Response Dictionary:")
        logging.info(response_json)

        # Check if 'update_status' exists in the response
        if "update_status" in response_json and isinstance(response_json["update_status"], dict):
            update_status = response_json["update_status"]
            logging.info("\nUpdate Status Dictionary:")
            for key, status in update_status.items():
                logging.info(f"{key}: {status}")
        else:
            logging.warning("The 'update_status' key is not present or is not a dictionary in the response.")
    except requests.RequestException as e:
        logging.error(f"An error occurred while making the request: {e}")
    except ValueError as e:
        logging.error(f"An error occurred while parsing the JSON response: {e}")

# Run the simulation
if __name__ == "__main__":
    simulate_config_update_param_call()