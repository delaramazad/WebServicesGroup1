#ansvarar för att hämta flygdata
import requests
import os
from dotenv import load_dotenv


load_dotenv()

def get_flight_data(flight_number):
    api_key = os.getenv("AVIATION_API_KEY")
    base_url = f"https://api.aviationstack.com/v1/flights?access_key={api_key}&limit=100&offset=0&flight_iata={flight_number}"
    response = requests.get(base_url)
    flight_data = response.json()

    return flight_data