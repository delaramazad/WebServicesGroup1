import os
from datetime import datetime
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

# Importera tjänster
from services.aviation_service import get_flight_data
from services.airport_service import AirportService
from services.musicbrainz_service import MusicBrainzService
from services.spotify_service import SpotifyService

load_dotenv()

# Initiera tjänster
airport_service = AirportService()
music_service = MusicBrainzService()
spotify_service = SpotifyService()

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
    
    country_display_name = "Unknown"
    music_data = []
    playlist_url = None
    iso_code = None

    # 2. Hämta Landskod (ISO)
    if arrival_iata:
        iso_code = airport_service.get_country_code(arrival_iata)
        
        if iso_code:
            print(f"Flight is going to country code: {iso_code}")
            country_display_name = iso_code # Vi visar koden på hemsidan också
            
            # 3. Hämta artister
            music_data = music_service.get_artists_by_country(iso_code)
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

    # 4. Skapa Spellista
    if music_data and iso_code:
        # Här skickar vi 'iso_code' som sista parameter!
        # Då blir namnet: "Espotifly [FLYGNR] to [SE]"
        playlist_url = spotify_service.create_flight_playlist(
            music_data, 
            flight_duration_minutes, 
            flight_number, 
            iso_code 
        )

    response_data = {
        "flight": flight_data,
        "destination_country": country_display_name,
        "music_recommendations": music_data,
        "playlist_url": playlist_url
    }
    
    return jsonify(response_data)

##################### ABOUT US PAGE #######################

@app.route("/about-us")
def about_us_page():
    """Renders a general information page about the project."""
    return render_template("about.html")


#################### DESTINNATION PAGE ###############

@app.route("/destination")
def destination_page():
    # Hämta flygnumret från URL:en (t.ex. /destination?flightNumber=FM891)
    flight_number = request.args.get('flightNumber')
    
    if not flight_number:
        return render_template("index.html")

    # 1. Hämta flygdata via din befintliga tjänst (från aviation_service.py)
    flight_data = get_flight_data(flight_number)
    if not flight_data:
        return "Flyget hittades inte", 404

    # 2. Hämta ankomstdata
    arrival = flight_data.get('arrival', {})
    arrival_iata = arrival.get('iata')
    
    # FÖRBÄTTRAD LOGIK FÖR STADSNAMN:
    # Om API:et inte ger en stad, tar vi flygplatsnamnet och rensar bort 
    # ord som "International" för att bild-tjänsten ska hitta rätt.
    city_name = arrival.get('city')
    if not city_name:
        raw_airport = arrival.get('airport', "Unknown City")
        city_name = raw_airport.replace("International", "").replace("Airport", "").strip()
    
    # 3. Hämta landskod (t.ex. HU eller SE) via din airport_service
    country_display = "Unknown"
    if arrival_iata:
        iso_code = airport_service.get_country_code(arrival_iata)
        if iso_code:
            country_display = iso_code

    # 4. Rendera destination.html med all insamlad data
    return render_template("destination.html", 
                           city=city_name, 
                           country=country_display,
                           flight_number=flight_number)
# START SERVER LAST 
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8081, debug=True)
