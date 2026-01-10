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
        "IAH": ("United States", "US"),
        "DXB": ("United Arab Emirates", "AE"),
        "CDG": ("France", "FR"),
        "AMS": ("Netherlands", "NL"),
        "FRA": ("Germany", "DE"),
        "BCN": ("Spain", "ES"),
        "YYZ": ("Canada", "CA")
    }
    
    def get_country_data(self, iata, icao, name):
        # --- STEG 1: KOLLA DIN BACKUP-LISTA FÖRST ---
        if iata and iata in self.AIRPORT_BACKUPS:
            return self.AIRPORT_BACKUPS[iata]
        # ---------------------------------------------

        url = "https://query.wikidata.org/sparql"
        sparql_condition = ""

        if iata:
            sparql_condition = f'?airport wdt:P238 "{iata}" .'
        elif icao:
            sparql_condition = f'?airport wdt:P239 "{icao}" .'
        elif name:
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
            response = requests.get(url, params=params, headers=headers, timeout=5)
            if response.status_code != 200:
                return None, None

            data = response.json()
            results = data.get("results", {}).get("bindings", [])

            if results:
                match = results[0]
                country = match.get("countryLabel", {}).get('value')
                iso2 = match.get("iso2", {}).get('value')
                return country, iso2
            else:
                return None, None

        except Exception as e:
            print(f"Error fetching country data: {e}")
            return None, None

    # --- HÄR ÄR DEN NYA FUNKTIONEN SOM SAKNADES ---
    def get_city_image(self, city_name):
        if not city_name:
            return None
            
        # Vi söker på engelska Wikipedia API för bilder
        url = "https://en.wikipedia.org/w/api.php"
        
        params = {
            "action": "query",
            "format": "json",
            "prop": "pageimages",
            "piprop": "original", # Vi vill ha originalbilden (hög kvalitet)
            "titles": city_name,
            "pithumbsize": 1000
        }
        
        headers = {'User-Agent': 'Espotifly/1.0 (student-project)'}

        try:
            print(f"Letar efter bild på {city_name} via Wikipedia...")
            response = requests.get(url, params=params, headers=headers, timeout=5)
            data = response.json()
            
            # Wikipedia returnerar datan lite nästlat, vi måste gräva
            pages = data.get("query", {}).get("pages", {})
            
            for page_id, page_data in pages.items():
                if "original" in page_data:
                    image_url = page_data["original"]["source"]
                    print(f"Hittade bild: {image_url}")
                    return image_url
            
            print("Ingen bild hittades på Wikipedia.")
            return None

        except Exception as e:
            print(f"Fel vid bildhämtning: {e}")
            return None