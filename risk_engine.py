# risk_engine.py

def compute_risk_score(hazard_data, sector):
    """
    Compute final risk score using sector-specific weights.
    """
    # Sector weight mapping
    sector_weights = {
        "Chemical": 1.0,
        "Pharma": 0.8,
        "Automobile": 0.5,
        "Engineering": 0.5,
        "MSME": 0.35,        # mid-point of 0.3–0.4
        "ICT": 0.35,
        "Logistics": 0.35,
        "Other": 1.0         # neutral
    }

    # Pick weight, default = 1.0
    weight = sector_weights.get(sector, 1.0)

    # Composite hazard from preprocessed dataset
    composite_hazard = hazard_data["Composite_Hazard"]

    # Final score
    final_score = composite_hazard * weight

    # Risk categorization
    if final_score < 0.33:
        category = "Low"
    elif final_score < 0.66:
        category = "Medium"
    else:
        category = "High"

    return {
        "Final_Score": round(final_score, 4),
        "Composite_Hazard": round(composite_hazard, 4),
        "Weight": weight,
        "Category": category
    }

