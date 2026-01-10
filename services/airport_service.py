import airportsdata

class AirportService:
    def __init__(self):
        # Laddar databasen snabbt
        self.airports = airportsdata.load('IATA')

    def get_location_info(self, iata_code):
        airport = self.airports.get(iata_code)
        
        if airport:
            # Returnerar bara lands-koden, t.ex. "SE" eller "TR"
            return airport.get('country'), airport.get('city')  
        else:
            return None, None