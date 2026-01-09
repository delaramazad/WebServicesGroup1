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
    """Renders the landing page."""
    return render_template("index.html")

@app.route('/get_flight_info', methods=['POST'])
def get_flight_info():
    data = request.get_json() # get JSON from JS
    flight_number = data.get('flightNumber')
    
    print(f"finding flight: {flight_number}")

    # step 1: get flight data from Aviationstack
    flight_data = get_flight_data(flight_number)
    
    if not flight_data:
        return jsonify({"error": "No flight data found"}), 404

    # we need the IATA code for the arrival airport to find the country
    arrival_iata = flight_data.get('arrival', {}).get('iata')
    print(f"Found arrival IATA: {arrival_iata}")

    country_name = "Unknown"
    music_data = []

    if arrival_iata:
        # step 2: Get country and ISO code (Wikidata SPARQL) 
        country_name, iso_code = wiki_service.get_country_data(arrival_iata)
        print(f"Flight is going to: {country_name} (ISO: {iso_code})")
        
        if iso_code:
            # step 3: Get artists from the country (MusicBrainz) 
            # Here we send the ISO code (ex'JP' or 'SE'), MusicBrainz uses ISO codes for countries
            music_data = music_service.get_artists_by_country(iso_code)
        else:
            print("No ISO code found for the destination country.")

    # step 4: Return combined data as JSON
    response_data = {
        "flight": flight_data,
        "destination_country": country_name,
        "music_recommendations": music_data
    }
    
    return jsonify(response_data)

##################### ABOUT US PAGE #######################

@app.route("/about-us")
def about_us_page():
    """Renders a general information page about the project."""
    return render_template("about.html")

# START SERVER LAST 
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8081, debug=True)