import logging
import os

import requests

logger = logging.getLogger(__name__)

AUTH_SERVICE_BASE_URL = os.environ.get("AUTH_SERVICE_BASE_URL",)

def fetch_data_central_db(query, fetch=None, mappings=None, params=None):
    """Fetches data from the central database."""
    logger.info(f"Executing query on central DB: {query}")
    try:
        data = {"query": query}
        if fetch:
            data["fetch"] = fetch
        if mappings:
            data["mappings"] = mappings
        if params:
            data["params"] = params

        res_data = requests.post(url=f"{AUTH_SERVICE_BASE_URL}/execute_query", json=data)
        status_code = res_data.status_code

        if status_code != 200:
            logger.error(f"Error fetching from Data Central DB: {res_data.text}")
            raise Exception(f"Error occurred while fetching data from Data Central DB: {res_data.text}")

        result = res_data.json()
        response = result.get("message")

        return response

    except requests.exceptions.RequestException as e:
        logger.exception(f"Error while fetching data from central db: {e}")
        raise e
    except Exception as e:
        logger.exception(f"An unexpected error occurred in fetch_data_central_db: {e}")
        raise e