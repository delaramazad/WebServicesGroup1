import requests

class WikimediaService:
    
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
            image_url = "https://media1.tenor.com/images/f0e8e9237c710dda55a2a86a7c73b40b/tenor.gif"
            return image_url

        except Exception as e:
            print(f"Fel vid bildhämtning: {e}")
            return None
