def calculate_risk(indicators, sector):
    er = indicators["ER100"]
    rp = indicators["RP100"]
    d = indicators["P_D1"]

    norm_er = min(er / 0.1, 1.0)
    norm_rp = min(rp / 300.0, 1.0)
    norm_d = min(d / 0.3, 1.0)

    score = round((norm_er + norm_rp + norm_d) / 3.0, 3)

    if score >= 0.75:
        risk = "High"
    elif score >= 0.5:
        risk = "Medium"
    else:
        risk = "Low"

    return {
        "final_score": score,
        "risk_category": risk,
        **indicators
    }
