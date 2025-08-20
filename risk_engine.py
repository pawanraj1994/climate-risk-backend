# risk_engine.py

def compute_risk_score(hazard_data, sector):
    """
    Compute final risk score and category using Composite Hazard and sector weight.
    """

    sector_weights = {
        "Chemical": 1.0,
        "Pharma": 1.0,
        "Automotive": 0.5,
        "Engineering": 0.5,
        "ICT": 0.4,
        "Logistics": 0.4,
        "MSME": 0.3,
    }

    weight = sector_weights.get(sector, 0.5)  # default if not listed
    composite_hazard = hazard_data["Composite_Hazard"]

    final_score = round(weight * composite_hazard, 4)

    if final_score < 0.2:
        category = "Low"
    elif final_score < 0.5:
        category = "Medium"
    else:
        category = "High"

    return {
        "Final_Score": final_score,
        "Category": category,
        "Weight": weight,
        "Composite_Hazard": composite_hazard,
    }
