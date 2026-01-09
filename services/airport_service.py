import airportsdata

class AirportService:
    def __init__(self):
        # Laddar databasen snabbt
        self.airports = airportsdata.load('IATA')

    def get_country_code(self, iata_code):
        airport = self.airports.get(iata_code)
        
        if airport:
            # Returnerar bara lands-koden, t.ex. "SE" eller "TR"
            return airport.get('country')
        else:
            return None