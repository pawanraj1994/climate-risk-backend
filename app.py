from flask import Flask, request, jsonify
from flask_cors import CORS
from rainfall_module import extract_rainfall_indicators
from risk_engine import calculate_risk

app = Flask(__name__)
CORS(app)

@app.route("/risk", methods=["POST"])
def calculate_risk_api():
    try:
        data = request.get_json()
        lat = float(data.get("latitude"))
        lon = float(data.get("longitude"))
        sector = data.get("sector")

        if lat is None or lon is None or sector is None:
            return jsonify({"error": "Missing one or more required parameters"}), 400

        indicators = extract_rainfall_indicators(lat, lon)
        result = calculate_risk(indicators, sector)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
