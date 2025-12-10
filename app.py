#filen som startar servern

import os
from flask import Flask, jsonify, render_template
from dotenv import load_dotenv
import requests

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