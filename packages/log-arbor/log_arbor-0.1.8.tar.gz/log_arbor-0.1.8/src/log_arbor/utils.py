import requests
import os
from dotenv import load_dotenv
from datetime import datetime
from requests.exceptions import RequestException

load_dotenv()

def log(service_id: str, level: str, message: str):
    """Pushes the log to a service through LogArbor Logs API"""

    current_time_format_string = "%Y-%m-%d %H:%M:%S"
    current_datetime_object = datetime.now()

    try:
        log_json = {
            "service_id": service_id,
            "token": os.getenv("LOGARBOR_API_TOKEN"),
            "message": message,
            "level": level,
            "time": current_datetime_object.strftime(current_time_format_string)
        }


        response = requests.post(os.getenv("LOGARBOR_LOG_API"), json=log_json)

        if not response.status_code == 200 and not response.status_code == 202:
            raise RuntimeError(f"Log API rejected a request with a status code: {response.status_code} and message: {response.text}")
    except RequestException as e:
        raise RuntimeError(f"An error occurred while accessing Log API: {e}")
    except Exception as e:
        raise RuntimeError(f"An error occurred during the log function: {e}")

