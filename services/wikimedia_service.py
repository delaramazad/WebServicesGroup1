import requests

class WikimediaService:
    
    # Din manuella databas (Backup)
    AIRPORT_BACKUPS = {
        "IST": ("Turkey", "TR"),
        "SAW": ("Turkey", "TR"),
        "ARN": ("Sweden", "SE"),
        "BMA": ("Sweden", "SE"),
        "GOT": ("Sweden", "SE"),
        "CPH": ("Denmark", "DK"),
        "LHR": ("United Kingdom", "GB"),
        "LGW": ("United Kingdom", "GB"),
        "JFK": ("United States", "US"),
        "EWR": ("United States", "US"),
        "IAH": ("United States", "US"), # George Bush Intercontinental
        "DXB": ("United Arab Emirates", "AE"),
        "CDG": ("France", "FR"),
        "AMS": ("Netherlands", "NL"),
        "FRA": ("Germany", "DE"),
        "BCN": ("Spain", "ES")
    }
    
    def get_country_data(self, iata, icao, name):
        # --- STEG 1: KOLLA DIN BACKUP-LISTA FÖRST ---
        # Detta är den nya delen som saknades!
        if iata and iata in self.AIRPORT_BACKUPS:
            print(f"Hittade {iata} i backup-listan! Hoppar över Wikidata.")
            # Hämtar datan direkt från din lista
            return self.AIRPORT_BACKUPS[iata]
        # ---------------------------------------------

        url = "https://query.wikidata.org/sparql"
        sparql_condition = ""

        if iata:
            print(f"Searching Wikidata by IATA: {iata}")
            sparql_condition = f'?airport wdt:P238 "{iata}" .'
        elif icao:
            print(f"Searching Wikidata by ICAO: {icao}")
            sparql_condition = f'?airport wdt:P239 "{icao}" .'
        elif name:
            print(f"Searching Wikidata by Name: {name}")
            sparql_condition = f'''
                ?airport rdfs:label ?label .
                FILTER(CONTAINS(LCASE(?label), LCASE("{name}")))
                ?airport wdt:P31 wdt:Q1248784 . 
            '''
        else:
            return "Unknown", None

        query = f"""
        SELECT ?countryLabel ?iso2 WHERE {{
            {sparql_condition}
            ?airport wdt:P17 ?country .
            OPTIONAL {{ ?country wdt:P297 ?iso2 . }}
            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT 1
        """ 

        params = { "query": query, "format": "json" }
        headers = { 'User-Agent': 'FlightMusicApp/1.0 (student_project_test)' }

        try:
            print("Sending request to Wikidata...")
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            print(f"Wikidata response status: {response.status_code}")

            if response.status_code != 200:
                print(f"Wikidata error text: {response.text}")
                return None, None

            data = response.json()
            results = data.get("results", {}).get("bindings", [])

            if results:
                match = results[0]
                country = match.get("countryLabel", {}).get('value')
                iso2 = match.get("iso2", {}).get('value')
                return country, iso2
            else:
                print("No match found in Wikidata")
                return None, None

        except Exception as e:
            print(f"Error fetching country data: {e}")
            return None, None