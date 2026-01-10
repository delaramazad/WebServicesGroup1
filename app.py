import os
from datetime import datetime
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

# Importera tjänster
from services.aviation_service import get_flight_data
from services.airport_service import AirportService
from services.musicbrainz_service import MusicBrainzService
from services.spotify_service import SpotifyService
# VIKTIGT: Denna saknades!
from services.wikimedia_service import WikimediaService 

load_dotenv()

# Initiera tjänster
airport_service = AirportService()
music_service = MusicBrainzService()
spotify_service = SpotifyService()
wikimedia_service = WikimediaService() # VIKTIGT: Starta denna tjänst

app = Flask(__name__)

@app.route("/")
def root_index():
    return render_template("index.html")

@app.route('/get_flight_info', methods=['POST'])
def get_flight_info():
    data = request.get_json() 
    flight_number = data.get('flightNumber')
    
    print(f"Finding flight: {flight_number}")

    # 1. Hämta flygdata
    flight_data = get_flight_data(flight_number)
    if not flight_data:
        return jsonify({"error": "No flight data found"}), 404

    # Hämta ankomst-IATA
    arrival = flight_data.get('arrival', {})
    arrival_iata = arrival.get('iata')
    
    # Initiera variabler så de inte kraschar om de är tomma
    country_display_name = "Unknown"
    city_name = "Unknown City" # Standardvärde
    image_url = None
    music_data = []
    playlist_url = None
    iso_code = None

    # 2. Hämta Landskod OCH Stad
    if arrival_iata:
        # FÖRSÖK 1: Använd AirportService (Om du uppdaterat den filen)
        try:
            # OBS: Detta kräver att du har uppdaterat services/airport_service.py 
            # enligt instruktionen tidigare!
            iso_code, city_name_from_service = airport_service.get_location_info(arrival_iata)
            
            if iso_code:
                country_display_name = iso_code
            if city_name_from_service:
                city_name = city_name_from_service

        except AttributeError:
            # Fallback: Om du har den GAMLA airport_service.py kvar
            iso_code = airport_service.get_country_code(arrival_iata)
            country_display_name = iso_code or "Unknown"
            # Försök ta staden från flygdatan istället
            city_from_flight = arrival.get('city')
            if city_from_flight:
                city_name = city_from_flight

        if iso_code:
            print(f"Flight is going to: {city_name} ({iso_code})")
            
            # 3. Hämta artister
            music_data = music_service.get_artists_by_country(iso_code)

            # 4. Hämta bild på staden (NYTT)
            if city_name and city_name != "Unknown City":
                # Använd wikimedia-tjänsten
                image_url = wikimedia_service.get_city_image(city_name)
        else:
            print(f"Ingen landskod hittades för: {arrival_iata}")

    # --- Beräkna flygtid ---
    flight_duration_minutes = 120 
    try:
        dep_str = flight_data.get('departure', {}).get('scheduled')
        arr_str = flight_data.get('arrival', {}).get('scheduled')
        if dep_str and arr_str:
            dep_time = datetime.fromisoformat(dep_str.replace("Z", "+00:00"))
            arr_time = datetime.fromisoformat(arr_str.replace("Z", "+00:00"))
            flight_duration_minutes = (arr_time - dep_time).total_seconds() / 60
    except Exception as e:
        print(f"Tidsberäkning misslyckades: {e}")

    # 5. Skapa Spellista
    if music_data and iso_code:
        playlist_url = spotify_service.create_flight_playlist(
            music_data, 
            flight_duration_minutes, 
            flight_number, 
            iso_code 
        )

    # Bygg svaret (Här kraschade din gamla kod för att variablerna inte fanns)
    response_data = {
        "flight": flight_data,
        "destination_country": country_display_name,
        "destination_city": city_name, # Nu är denna definierad!
        "city_image": image_url,       # Vi döper nyckeln till city_image för att matcha JS
        "music_recommendations": music_data,
        "playlist_url": playlist_url
    }
    
    return jsonify(response_data)

##################### ABOUT US PAGE #######################
@app.route("/about-us")
def about_us_page():
    return render_template("about.html")

# START SERVER LAST 
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8081, debug=True)