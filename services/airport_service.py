import airportsdata

class AirportService:
    def __init__(self):
        # Loads the databse quickly
        self.airports = airportsdata.load('IATA')

    def get_location_info(self, iata_code):
        airport = self.airports.get(iata_code)
        
        if airport:
            # Only returns the country code e.g. "SE" or "TR"
            return airport.get('country'), airport.get('city')  
        else:
            return None, None