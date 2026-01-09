import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

class SpotifyService:
    def __init__(self):
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
        
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope="playlist-modify-public"
        ))

    def create_flight_playlist(self, artists, flight_duration_minutes, flight_number, country_name):
        # 1. BESTÄM LÄNGD: Alltid 5 timmar (300 minuter)
        fixed_hours = 5
        target_duration_ms = fixed_hours * 60 * 60 * 1000
        
        print(f"--- Skapar spellista: Mål {fixed_hours} timmar ({target_duration_ms} ms) ---")
        
        current_duration_ms = 0
        track_uris = [] 
        
        for artist_name in artists:
            # Har vi fyllt 5 timmar än?
            if current_duration_ms >= target_duration_ms:
                break
                
            try:
                # Sök artist
                results = self.sp.search(q='artist:' + artist_name, type='artist', limit=1)
                items = results['artists']['items']
                if not items: continue 
                
                artist_id = items[0]['id']
                top_tracks = self.sp.artist_top_tracks(artist_id, country='SE')
                
                added_count = 0
                for track in top_tracks['tracks']:
                    # VIKTIGT: Öka gränsen så vi hinner fylla 5 timmar!
                    # Om vi tar max 10 låtar per artist behöver vi färre artister totalt.
                    if added_count >= 10: break 
                    
                    # Undvik dubbletter
                    if track['uri'] in track_uris: continue

                    track_uris.append(track['uri'])
                    current_duration_ms += track['duration_ms']
                    added_count += 1
                    
                    if current_duration_ms >= target_duration_ms: break
                        
            except Exception as e:
                print(f"Fel med artist {artist_name}: {e}")

        # 2. SKAPA SPELLISTAN
        if not track_uris:
            print("Inga låtar hittades.")
            return None 

        try:
            user_id = self.sp.me()['id']
            
            # Namnet blir snyggt: "Espotifly SK123 to SE"
            playlist_name = f"Espotifly {flight_number} to {country_name}"
            new_playlist = self.sp.user_playlist_create(user_id, playlist_name, public=True)
            
            # Spotify tillåter max 100 låtar per anrop. 
            # 5 timmar musik kan vara mer än 100 låtar, så vi delar upp det i bitar (chunks).
            for i in range(0, len(track_uris), 100):
                chunk = track_uris[i:i + 100]
                self.sp.playlist_add_items(new_playlist['id'], chunk)
            
            print(f"Spellista klar! Länk: {new_playlist['external_urls']['spotify']}")
            print(f"Total längd: {current_duration_ms / 1000 / 60} minuter.")
            
            return new_playlist['external_urls']['spotify']

        except Exception as e:
            print(f"Kunde inte skapa spellista: {e}")
            return None