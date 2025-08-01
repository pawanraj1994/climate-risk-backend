def calculate_risk(indicators, sector):
    er = indicators["ER100"]
    rp = indicators["RP100"]
    d = indicators["P_D1"]

    # Normalize hazard indicators
    norm_er = min(er / 0.1, 1.0)
    norm_rp = min(rp / 300.0, 1.0)
    norm_d = min(d / 0.3, 1.0)

    # Sector-specific weights
    sector_weights = {
        "Chemical": 1.0,
        "Pharmaceutical": 0.9,
        "Textile": 0.7,
        "Engineering": 0.6,
        "Food Processing": 0.5,
        "Other": 0.4
    }

    # Default weight if sector not recognized
    weight = sector_weights.get(sector, 0.5)

    raw_score = (norm_er + norm_rp + norm_d) / 3.0
    score = round(weight * raw_score, 3)

    # Risk classification
    if score >= 0.75:
        risk = "High"
    elif score >= 0.5:
        risk = "Medium"
    else:
        risk = "Low"

    # Return format that matches frontend expectations
    return {
        "ER100": indicators["ER100"],
        "ER150": indicators["ER150"], 
        "RP100": indicators["RP100"],
        "P_D1": indicators["P_D1"],
        "P_D2": indicators["P_D2"],
        "P_D3": indicators["P_D3"],
        "P_D4": indicators["P_D4"],
        "risk_category": risk,
        "final_score": score
    }