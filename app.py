import os
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
import requests

from services.aviation_service import get_flight_data
from services.wikimedia_service import WikimediaService
from services.musicbrainz_service import MusicBrainzService

wiki_service = WikimediaService()
music_service = MusicBrainzService()
app = Flask(__name__)


@app.route("/")
def root_index():
    return render_template("index.html")

@app.route('/get_flight_info', methods=['POST'])
def get_flight_info():
    data = request.get_json() 
    flight_number = data.get('flightNumber')
    
    print(f"finding flight: {flight_number}")

    # step 1: get flight data 
    flight_data = get_flight_data(flight_number)
    
    if not flight_data:
        return jsonify({"error": "No flight data found"}), 404

    # Hämta ALL info vi kan om ankomsten
    arrival = flight_data.get('arrival', {})
    arrival_iata = arrival.get('iata')
    arrival_icao = arrival.get('icao')
    arrival_name = arrival.get('airport') # Flygplatsens namn

    print(f"Arrival Data -> IATA: {arrival_iata}, ICAO: {arrival_icao}, Name: {arrival_name}")

    country_name = "Unknown"
    music_data = []

    # Om vi har IATA, ICAO eller Namn - kör sökningen
    if arrival_iata or arrival_icao or arrival_name:
        
        # step 2: Skicka in alla tre till funktionen
        country_name, iso_code = wiki_service.get_country_data(arrival_iata, arrival_icao, arrival_name)
        
        if country_name:
            print(f"Flight is going to: {country_name} (ISO: {iso_code})")
        
        if iso_code:
            # step 3: Get artists from the country
            music_data = music_service.get_artists_by_country(iso_code)
        else:
            print("No ISO code found/returned.")

    # step 4: Return combined data
    response_data = {
        "flight": flight_data,
        "destination_country": country_name,
        "music_recommendations": music_data
    }
    
    return jsonify(response_data)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8081, debug=True)