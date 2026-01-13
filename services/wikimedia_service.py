import requests

class WikimediaService:
    
    def get_city_image(self, city_name):
        if not city_name:
            return None
            
        # Search on english version wikipedia API for pictures. 
        url = "https://en.wikipedia.org/w/api.php"
        
        params = {
            "action": "query",
            "format": "json",
            "prop": "pageimages",
            "piprop": "original", # specifies that we want the original picture with high quality
            "titles": city_name,
            "pithumbsize": 1000
        }
        
        headers = {'User-Agent': 'Espotifly/1.0 (student-project)'}

        try:
            print(f"looking for image {city_name} on Wikipedia...")
            response = requests.get(url, params=params, headers=headers, timeout=5)
            data = response.json()
            
            # Wikipedia returns the data nested and we look for the image URL
            pages = data.get("query", {}).get("pages", {})
            
            for page_id, page_data in pages.items():
                if "original" in page_data:
                    image_url = page_data["original"]["source"]
                    print(f"image found: {image_url}")
                    return image_url
            
            print("No image found on Wikipedia.")
            image_url = "https://media1.tenor.com/images/f0e8e9237c710dda55a2a86a7c73b40b/tenor.gif"
            return image_url

        except Exception as e:
            print(f"error fetching image: {e}")
            return None
