from flask import Flask, request, jsonify
from flask_cors import CORS
from rainfall_module import extract_rainfall_indicators
from risk_engine import compute_risk_score

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "✅ Climate Risk API is running!"

@app.route("/risk", methods=["POST"])
def risk():
    try:
        # Get input JSON
        data = request.get_json()
        lat = float(data.get("latitude"))
        lon = float(data.get("longitude"))
        sector = data.get("sector", "Other")

        # Step 1: Extract preprocessed hazards
        hazard_data = extract_rainfall_indicators(lat, lon)

        # Step 2: Compute sector-weighted risk
        risk_result = compute_risk_score(hazard_data, sector)

        # Step 3: Build full response
        response = {
            "location": {"lat": hazard_data["LAT"], "lon": hazard_data["LON"]},
            "sector": sector,
            "hazards": {
                "ER100": hazard_data["ER100"],
                "ER150": hazard_data["ER150"],
                "ER_Prob": hazard_data["ER_Prob"],
                "RP10": hazard_data["RP10"],
                "RP20": hazard_data["RP20"],
                "RP50": hazard_data["RP50"],
                "RP100": hazard_data["RP100"],
                "RP_Avg": hazard_data["RP_Avg"],
                "RP_Prob": hazard_data["RP_Prob"],
                "P_D1": hazard_data["P_D1"],
                "P_D2": hazard_data["P_D2"],
                "P_D3": hazard_data["P_D3"],
                "P_D4": hazard_data["P_D4"],
                "Drought_Prob": hazard_data["Drought_Prob"],
                "Composite_Hazard": hazard_data["Composite_Hazard"]
            },
            "risk_result": risk_result
        }
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
