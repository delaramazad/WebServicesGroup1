#filen som startar servern

import os
from flask import Flask, jsonify, render_template
from dotenv import load_dotenv
import requests
from services.aviation_service import get_flight_data

app = Flask(__name__)

@app.get("/")
def fetch_flight_number(request):
    flight_number = request.args.get("flightNumber")
    if not flight_number:
        return jsonify({"error": "Missing flightNumber parameter"}), 400

    # Example API call to fetch flight data (replace with actual API and parameters)
    api_url = f"https://api.example.com/flights/{flight_number}"
    response = requests.get(api_url)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch flight data"}), response.status_code

    flight_data = response.json()
    return jsonify(flight_data)

@app.route("/")
def root_index():
    """
    Function that renders the web application's landing page.

    Returns: 
        template: index.html
    """
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8081, debug=True)