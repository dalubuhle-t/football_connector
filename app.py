from flask import Flask, jsonify, request
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
app = Flask(__name__)

# Base connector to your live Render API
CONNECTOR_URL = "https://football-connector-1.onrender.com"

# Utility: Safe connector fetch
def fetch_from_connector(endpoint, params=None):
    try:
        response = requests.get(f"{CONNECTOR_URL}{endpoint}", params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e), "source": endpoint}


@app.route("/")
def home():
    return jsonify({
        "status": "UFP Connector Live ✅",
        "source": CONNECTOR_URL,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })


@app.route("/fixtures/today")
def fixtures_today():
    today = datetime.utcnow().strftime("%Y-%m-%d")
    data = fetch_from_connector("/fixtures", {"date": today})
    return jsonify({"date": today, "fixtures": data})


@app.route("/fixtures/live")
def fixtures_live():
    data = fetch_from_connector("/fixtures/live")
    return jsonify(data)


@app.route("/routes")
def routes():
    import urllib
    output = []
    for rule in app.url_map.iter_rules():
        methods = ",".join(rule.methods)
        output.append(urllib.parse.unquote(f"{rule.endpoint}: {methods} {rule}"))
    return jsonify({"available_routes": output})


# ==========================================================
# 🔹 UFP PREMATCH ANALYSIS ENGINE
# ==========================================================
@app.route("/ufp/analyze/<int:fixture_id>")
def analyze_fixture(fixture_id):
    """
    Combines fixture info, form, injuries, and player stats
    into a simplified probability model output.
    """
    # Step 1: Fetch Fixture Details
    fixture = fetch_from_connector("/fixtures", {"id": fixture_id})
    if not fixture or "response" not in fixture or len(fixture["response"]) == 0:
        return jsonify({"error": "Fixture not found", "fixture_id": fixture_id})

    fixture_data = fixture["response"][0]
    home = fixture_data["teams"]["home"]
    away = fixture_data["teams"]["away"]
    home_id, away_id = home["id"], away["id"]

    # Step 2: Fetch Supporting Data
    home_form = fetch_from_connector("/teams/statistics", {"team": home_id})
    away_form = fetch_from_connector("/teams/statistics", {"team": away_id})
    home_inj = fetch_from_connector("/injuries", {"team": home_id})
    away_inj = fetch_from_connector("/injuries", {"team": away_id})

    # Step 3: Simplified UFP Calculation
    try:
        home_recent = home_form["response"].get("form", "")
        away_recent = away_form["response"].get("form", "")
        home_win_ratio = home_recent.count("W") / max(1, len(home_recent))
        away_win_ratio = away_recent.count("W") / max(1, len(away_recent))
    except Exception:
        home_win_ratio = away_win_ratio = 0.5

    injury_factor = 1 - (len(home_inj.get("response", [])) * 0.05)
    away_injury_factor = 1 - (len(away_inj.get("response", [])) * 0.05)

    # Weighted probabilities
    home_prob = round((home_win_ratio * 0.6 + injury_factor * 0.4) * 100, 2)
    away_prob = round((away_win_ratio * 0.6 + away_injury_factor * 0.4) * 100, 2)
    draw_prob = round(100 - ((home_prob + away_prob) / 2), 2)

    # Normalize
    total = home_prob + away_prob + draw_prob
    home_prob = round((home_prob / total) * 100, 2)
    draw_prob = round((draw_prob / total) * 100, 2)
    away_prob = round((away_prob / total) * 100, 2)

    # Over/Under and BTTS estimation
    avg_goals = (home_form["response"].get("goals", {}).get("for", {}).get("average", {}).get("total", 1.2)
                 + away_form["response"].get("goals", {}).get("for", {}).get("average", {}).get("total", 1.1)) / 2
    over25_prob = min(95, max(40, avg_goals * 30))
    btts_prob = min(90, max(35, (avg_goals * 28)))

    # Step 4: Final Structured UFP Output
    prediction = {
        "fixture_id": fixture_id,
        "match": f"{home['name']} vs {away['name']}",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "probabilities": {
            "home_win_%": home_prob,
            "draw_%": draw_prob,
            "away_win_%": away_prob,
            "BTTS_%": btts_prob,
            "Over_2.5_%": over25_prob
        },
        "recommendations": {
            "value_bet": "Over 2.5 Goals" if over25_prob > 60 else "BTTS",
            "safe_bet": "Double Chance (1X)" if home_prob > 50 else "X2",
            "high_risk": "Correct Score 2-1" if home_prob > away_prob else "1-2"
        },
        "layers_used": {
            "form": True,
            "injuries": True,
            "goals": True
        }
    }

    return jsonify(prediction)


# ==========================================================
# Run Server
# ==========================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))


