#search for artists from a specific country using MusicBrainz API
import requests

class MusicBrainzService:
    def get_artists_by_country(self, iso_code):
        url = "https://musicbrainz.org/ws/2/artist/"

        params = {
            "query": f"country:{iso_code}",
            "fmt": "json",
            "limit": 10  #test med 10 artister
        }   
        
        #User agent to avoid being blocked by the server, as per MusicBrainz API guidelines
        headers = {
            'User-Agent': 'WebServiceGroup1/1.0 (delaram.azad99@gmail.com)'
        }

        response = requests.get(url, params=params, headers=headers)
        data = response.json()
