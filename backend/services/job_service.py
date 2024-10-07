import os
import requests
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

API_KEY = os.getenv('APIJOBS_API_KEY')  # Load the API key from the environment
HEADERS = {
    'apikey': API_KEY,
    'Content-Type': 'application/json',
}


def search_jobs(query):
    """Fetch job listings from the API."""
    data = f'{{"q": "{query}"}}'  # Adjust query format if needed
    try:
        response = requests.post(
            'https://api.apijobs.dev/v1/job/search', headers=HEADERS, data=data)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()  # Return the job listings data
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
        return None
    except Exception as err:
        print(f"An error occurred: {err}")
        return None
