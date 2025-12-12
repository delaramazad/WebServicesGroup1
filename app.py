import os
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
import requests
from services.aviation_service import get_flight_data

app = Flask(__name__)

# --- HÄR ÄR DINA ROUTES (MÅSTE VARA FÖRE APP.RUN) ---

@app.route("/")
def root_index():
    """Renders the landing page."""
    return render_template("index.html")

# Fixad route: Rätt URL och placerad här uppe
@app.route('/get_flight_info', methods=['POST'])
def get_flight_info():
    data = request.get_json() # Hämta JSON från JS
    flight_number = data.get('flightNumber')
    
    # Hämta data från din service
    flight_data = get_flight_data(flight_number)
    
    # Skicka tillbaka som JSON
    return jsonify(flight_data)

# --- STARTA SERVERN SIST ---
if __name__ == "__main__":
    # Denna kod körs sist och blockerar, så inget får ligga under här
    app.run(host="127.0.0.1", port=8081, debug=True)