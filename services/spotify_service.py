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
        # Fixed lenght: always 5 hours (300 minutes)
        fixed_hours = 5
        target_duration_ms = fixed_hours * 60 * 60 * 1000
        
        print(f"Creating playlist: Target {fixed_hours} hours ({target_duration_ms} ms)")
        
        current_duration_ms = 0
        track_uris = [] 
        
        for artist_name in artists:
            # Checks if 5 hours has been filled
            if current_duration_ms >= target_duration_ms:
                break
                
            try:
                # search for artist
                results = self.sp.search(q='artist:' + artist_name, type='artist', limit=1)
                items = results['artists']['items']
                if not items: continue 
                
                artist_id = items[0]['id']
                top_tracks = self.sp.artist_top_tracks(artist_id, country='SE')
                
                added_count = 0
                for track in top_tracks['tracks']:
                    # Increase limit so we make sure to fill 5 hours!
                    # if we take maximum 10 songs per artist we need less artists in total
                    if added_count >= 10: break 
                    
                    # Avoid duplicates
                    if track['uri'] in track_uris: continue

                    track_uris.append(track['uri'])
                    current_duration_ms += track['duration_ms']
                    added_count += 1
                    
                    if current_duration_ms >= target_duration_ms: break
                        
            except Exception as e:
                print(f"wrong artist {artist_name}: {e}")

        # Create the playlist
        if not track_uris:
            print("No songs found.")
            return None 

        try:
            user_id = self.sp.me()['id']
            
            # Format the name to look nice and tidy: "Espotifly SK123 to SE"
            playlist_name = f"Espotifly {flight_number} to {country_name}"
            new_playlist = self.sp.user_playlist_create(user_id, playlist_name, public=True)
            
            # Spotify allows maimum 100 songs per fetch 
            # 5 hours of music could be more than 100 songs, so we divide it into chunks.
            for i in range(0, len(track_uris), 100):
                chunk = track_uris[i:i + 100]
                self.sp.playlist_add_items(new_playlist['id'], chunk)
            
            print(f"Playlist ready, Link: {new_playlist['external_urls']['spotify']}")
            print(f"Total duration: {current_duration_ms / 1000 / 60} minutes.")
            
            return new_playlist['external_urls']['spotify']

        except Exception as e:
            print(f"Could not create playlist: {e}")
            return None