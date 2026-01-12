import os
import json
from datetime import datetime
from urllib.parse import quote
from urllib.request import Request, urlopen

from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

# Importera tjänster
from services.aviation_service import get_flight_data
from services.airport_service import AirportService
from services.musicbrainz_service import MusicBrainzService
from services.spotify_service import SpotifyService
from services.wikimedia_service import WikimediaService

load_dotenv()

# Initiera tjänster
airport_service = AirportService()
music_service = MusicBrainzService()
spotify_service = SpotifyService()
wikimedia_service = WikimediaService()

app = Flask(__name__)


@app.route("/")
def root_index():
    return render_template("index.html")


# ---------- Wikipedia helpers ----------
def _http_get_json(url: str):
    try:
        req = Request(
            url,
            headers={
                "User-Agent": "Espotifly/1.0 (student project)",
                "Accept": "application/json"
            }
        )
        with urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw)
    except Exception as e:
        print(f"HTTP GET failed: {e}")
        return None


def get_wikipedia_summary(city: str) -> dict:
    if not city:
        return {
            "title": "Unknown",
            "extract": "No city provided.",
            "thumbnail": None,
            "wikipedia_url": None
        }

    title = city.strip()
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(title)}"
    data = _http_get_json(url)

    if not data or data.get("type") == "https://mediawiki.org/wiki/HyperSwitch/errors/not_found":
        return {
            "title": title,
            "extract": f"No Wikipedia summary found for {title}.",
            "thumbnail": None,
            "wikipedia_url": f"https://en.wikipedia.org/wiki/{quote(title.replace(' ', '_'))}"
        }

    extract = data.get("extract")
    thumb = None
    if isinstance(data.get("thumbnail"), dict):
        thumb = data["thumbnail"].get("source")

    page_url = None
    if isinstance(data.get("content_urls"), dict):
        desktop = data["content_urls"].get("desktop", {})
        page_url = desktop.get("page")

    return {
        "title": data.get("title", title),
        "extract": extract,
        "thumbnail": thumb,
        "wikipedia_url": page_url
    }


def get_wikipedia_sights(city: str, limit: int = 8) -> dict:
    if not city:
        return {"items": []}

    # Wikipedia search query for attractions
    query = f"{city} tourist attractions"
    url = (
        "https://en.wikipedia.org/w/api.php"
        f"?action=query&list=search&srsearch={quote(query)}"
        "&format=json"
    )

    data = _http_get_json(url)
    if not data or "query" not in data or "search" not in data["query"]:
        return {"items": []}

    items = []
    for hit in data["query"]["search"][:limit]:
        title = hit.get("title")
        if not title:
            continue
        page_url = f"https://en.wikipedia.org/wiki/{quote(title.replace(' ', '_'))}"
        items.append({"name": title, "url": page_url})

    return {"items": items}


# ---------- Main API ----------
@app.route('/api/flights/<flight_number>', methods=['GET'])
def get_flight_info(flight_number):
    # (Vi hämtar inte längre genres här eftersom GET bara hämtar data)
    print(f"Fetching data for flight: {flight_number}")

    flight_data = get_flight_data(flight_number)
    if not flight_data:
        return jsonify({"error": "No flight data found"}), 404

    arrival = flight_data.get('arrival', {})
    arrival_iata = arrival.get('iata')

    country_display_name = "Unknown"
    city_name = "Unknown City"
    image_url = None
    iso_code = None

    if arrival_iata:
        iso_code, city_name_from_service = airport_service.get_location_info(arrival_iata)
        country_display_name = iso_code or "Unknown"
        city_name = city_name_from_service or arrival.get('city') or "Unknown City"

        if city_name and city_name != "Unknown City":
            image_url = wikimedia_service.get_city_image(city_name)

    # Vi returnerar data, men ingen spellista än!
    return jsonify({
        "flight": flight_data,
        "destination_country": country_display_name,
        "destination_city": city_name,
        "city_image": image_url,
        "iso_code": iso_code # Vi skickar med iso_code så frontend kan använda den sen
    })

# NY ENDPOINT: Skapar resursen 'playlist'
@app.route('/api/flights/<flight_number>/playlists', methods=['POST'])
def create_flight_playlist(flight_number):
    data = request.get_json()
    genres = data.get('genres', [])
    iso_code = data.get('iso_code')
    
    # Här kan vi behöva hämta flygdatan igen eller lita på frontends info
    # För enkelhetens skull kör vi skapandet här:
    flight_data = get_flight_data(flight_number)
    
    # Beräkna flygtid (samma logik som förut)
    flight_duration_minutes = 120
    try:
        dep_str = flight_data.get('departure', {}).get('scheduled')
        arr_str = flight_data.get('arrival', {}).get('scheduled')
        if dep_str and arr_str:
            dep_time = datetime.fromisoformat(dep_str.replace("Z", "+00:00"))
            arr_time = datetime.fromisoformat(arr_str.replace("Z", "+00:00"))
            flight_duration_minutes = (arr_time - dep_time).total_seconds() / 60
    except: pass

    music_data = music_service.get_artists_by_country(iso_code, genres)
    playlist_url = spotify_service.create_flight_playlist(
        music_data, flight_duration_minutes, flight_number, iso_code
    )

    # REST-standard: Returnera 201 Created när en resurs har skapats
    return jsonify({"playlist_url": playlist_url}), 201


# ---------- Facts & Sights API ----------
# Vi gör staden till en del av sökvägen (path parameter)
@app.route("/api/cities/<city_name>/facts")
def city_facts(city_name):
    return jsonify(get_wikipedia_summary(city_name))

@app.route("/api/cities/<city_name>/sights")
def city_sights(city_name):
    return jsonify(get_wikipedia_sights(city_name))


##################### ABOUT US PAGE #######################
@app.route("/about-us")
def about_us_page():
    return render_template("about.html")


# START SERVER LAST
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8081, debug=True)
