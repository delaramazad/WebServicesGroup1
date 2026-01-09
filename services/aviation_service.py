#responsible for getting flight data from Aviationstack API
import requests
import os
from dotenv import load_dotenv


load_dotenv()

#get flight data from Aviationstack API
#Returns the JSON response from the API
#param flight_number

def get_flight_data(flight_number):
    api_key = os.getenv("AVIATION_API_KEY")
    base_url = f"https://api.aviationstack.com/v1/flights?access_key={api_key}&limit=100&offset=0&flight_iata={flight_number}"
    
    try:
        response = requests.get(base_url)
        json_response = response.json()

        if 'data' in json_response and len(json_response['data']) > 0:
            return json_response['data'][0]  #return the first matching flight
        else:
            return None
    except Exception as e:
        print(f"Error fetching flight data: {e}")
        return None
   