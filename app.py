import os
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

# Om du redan har en fungerande service-funktion: behåll den.
# Den ska ta en flightNumber-sträng och returnera dict/list (JSON-kompatibelt).
from services.aviation_service import get_flight_data

load_dotenv()

def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")

    @app.get("/")
    def index():
        # Landing / route page
        return render_template("index.html")

    @app.post("/")
    def index_post():
        flight_number = (request.form.get("flightNumber") or "").strip()
        flight_data = None
        error = None

        if not flight_number:
            error = "Skriv in ett flight number (t.ex. AA2730)."
        else:
            try:
                flight_data = get_flight_data(flight_number)
            except Exception as exc:  # noqa: BLE001
                # Visa ett användarvänligt fel i UI
                error = f"Kunde inte hämta flight-data för {flight_number}."
                # Logga detaljer i terminalen för debugging
                app.logger.exception("get_flight_data failed: %s", exc)

        return render_template("index.html", flight_number=flight_number, flight_data=flight_data, error=error)

    @app.get("/api/flight")
    def api_flight():
        flight_number = (request.args.get("flightNumber") or "").strip()
        if not flight_number:
            return jsonify({"error": "Missing flightNumber"}), 400

        try:
            data = get_flight_data(flight_number)
            return jsonify({"flightNumber": flight_number, "data": data})
        except Exception as exc:  # noqa: BLE001
            app.logger.exception("api_flight failed: %s", exc)
            return jsonify({"error": "Failed to fetch flight data"}), 502

    return app


app = create_app()

if __name__ == "__main__":
    # Anpassa port om du vill
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "8081")), debug=True)
