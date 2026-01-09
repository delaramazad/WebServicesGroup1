import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_flight_data(flight_number):
    api_key = os.getenv("AVIATION_API_KEY")
    # Vi tar bort offset, limit 100 räcker
    base_url = f"https://api.aviationstack.com/v1/flights?access_key={api_key}&limit=100&flight_iata={flight_number}"
    
    try:
        response = requests.get(base_url)
        json_response = response.json()

        if 'data' in json_response and len(json_response['data']) > 0:
            # --- NY LOGIK: Hitta bästa datan ---
            
            # 1. Försök hitta en rad som faktiskt har en IATA-kod för ankomst
            for flight in json_response['data']:
                arrival = flight.get('arrival')
                if arrival and arrival.get('iata'):
                    print(f"Hittade flygdata MED IATA: {arrival.get('iata')}")
                    return flight
            
            # 2. Om ingen har IATA, returnera den första ändå (vi får lita på namnsökning)
            print("Ingen IATA hittades, returnerar första träffen.")
            return json_response['data'][0] 
            
        else:
            return None
    except Exception as e:
        print(f"Error fetching flight data: {e}")
        return None