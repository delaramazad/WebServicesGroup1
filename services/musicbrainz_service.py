import requests

class MusicBrainzService:
    
    # --- RESERVLISTA (FALLBACK) ---
    # Denna används nu BARA om API:et misslyckas eller ger 0 träffar.
    MUSIC_BACKUPS = {
        "SE": ["ABBA", "Avicii", "Zara Larsson", "Roxette", "Swedish House Mafia"],
        "TR": ["Tarkan", "Sezen Aksu", "Müslüm Gürses", "Sertab Erener", "Hadise"],
        "US": ["Michael Jackson", "Taylor Swift", "Eminem", "Beyoncé", "Elvis Presley"],
        "GB": ["The Beatles", "Adele", "Queen", "Ed Sheeran", "Coldplay"],
        "DK": ["Lukas Graham", "MØ", "Volbeat", "Aqua"],
        "NO": ["Kygo", "A-ha", "Alan Walker", "Aurora"],
        "ES": ["Enrique Iglesias", "Rosalía", "Julio Iglesias"],
        "FR": ["Daft Punk", "David Guetta", "Édith Piaf"],
        "DE": ["Rammstein", "Scorpions", "Kraftwerk"],
        "IT": ["Måneskin", "Andrea Bocelli", "Eros Ramazzotti"]
    }

    def get_artists_by_country(self, iso_code):
        # Inställningar för API-anropet
        url = "https://musicbrainz.org/ws/2/artist/"
        
        # Sök efter land OCH populära genrer (för att filtrera bort okända band)
        query = f"country:{iso_code} AND (tag:pop OR tag:rock OR tag:dance OR tag:electronic OR tag:hip-hop)"

        params = {
            "query": query,
            "fmt": "json",
            "limit": 40 # Vi tar lite fler för att kunna rensa bort dubbletter
        }   
        
        headers = {
            'User-Agent': 'WebServiceGroup1/1.0 (delaram.azad99@gmail.com)'
        }

        # --- FÖRSÖK 1: API (PRIORITERAT) ---
        try:
            print(f"Anropar MusicBrainz API för landskod: {iso_code}...")
            response = requests.get(url, params=params, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                artists_raw = data.get("artists", [])
                
                artist_names = []
                for artist in artists_raw:
                    name = artist.get("name")
                    # Spara namnet om det finns och inte redan ligger i listan
                    if name and name not in artist_names:
                        artist_names.append(name)
                
                # OM vi fick träffar: Returnera dem direkt!
                if artist_names:
                    print(f"Hittade {len(artist_names)} artister via API.")
                    for artist in artist_names:
                        print(f"- {artist}")
                    return artist_names # return artists
                else:
                    print("API fungerade men gav inga relevanta artister.")
            
            else:
                print(f"MusicBrainz API error: {response.status_code}")

        except Exception as e:
            print(f"Kunde inte nå MusicBrainz API: {e}")

        # --- FÖRSÖK 2: BACKUP-LISTA (OM API MISSLYCKADES) ---
        print("Går över till reservlistan (Backup)...")
        
        if iso_code in self.MUSIC_BACKUPS:
            return self.MUSIC_BACKUPS[iso_code]

        # Om varken API eller Backup har data:
        return ["Inga artister hittades"]