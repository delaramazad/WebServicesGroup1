#search for country information based on IATA code using Wikidata SPARQL endpoint
import requests

class WikimediaService:
    def get_country_data(self, iata_code):
        url = "https://query.wikidata.org/sparql"

        #SPARQL query to find country and ISO2 code based on IATA code
        #inserts parameter iata_code into the query dynamically using f-string

        query = f"""
        SELECT ?countryLabel ?iso2 WHERE {{
            ?airport wdt:P238 "{iata_code}" .
            ?airport wdt:P17 ?country .
            OPTIONAL {{ ?country wdt:P297 ?iso2 . }}
            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT 1
        """ 

        #Make request to Wikidata SPARQL endpoint, sending query as a parameter in JSON format
        params = {
            "query": query,
            "format": "json"
        }

        #User agent to avoid being blocked by the server, as per Wikidata SPARQL endpoint guidelines
        headers = {
            'User-Agent' : 'WebServiceGroup1/1.0 (delaram.azad99@gmail.com)' 
        }

        try:
            response = requests.get(url, params=params, headers=headers)
            data = response.json()

            #extracrt relevant information from the response
            results = data.get ("results", {}).get("bindings", [])

            if results:
                #get the first match
                match = results[0]
                country = match.get("countryLabel", {}).get('value') #country name
                iso2 = match.get("iso2", {}).get('value') #ISO2 code
                return country, iso2
            else:
                return None, None
        except Exception as e:
            print(f"Error fetching country data: {e}")
            return None, None
            

        