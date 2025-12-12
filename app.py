#filen som startar servern

import os
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
import requests
from services.aviation_service import get_flight_data

app = Flask(__name__)

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



@app.route('/get_flight_info', methods=['POST'])
def get_flight_info():
    data = request.get_json() # Hämta data som skickades från JS
    flight_number = data.get('flightNumber')
    
    flight_data = get_flight_data(flight_number)
    
    # Skicka tillbaka datan som JSON istället för en HTML-sida
    return jsonify(flight_data)

