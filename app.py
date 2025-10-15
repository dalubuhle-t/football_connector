from flask import Flask, jsonify, request
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
app = Flask(__name__)

# --- Configuration ---
API_KEY = os.getenv("API_FOOTBALL_KEY")
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY}

# --- Utility: Example Prediction Logic ---
def generate_prediction(fixture):
    """
    Simplified hybrid Poisson + Elo simulation placeholder.
    Returns a dict with pre-match prediction markets.
    """
    home_team = fixture.get("teams", {}).get("home", {}).get("name", "Home")
    away_team = fixture.get("teams", {}).get("away", {}).get("name", "Away")

    # Example probability logic (replace with full UFP v2.0 logic as needed)
    home_prob = 0.55
    draw_prob = 0.20
    away_prob = 0.25

    # Convert probabilities to decimal odds
    home_odds = round(1 / home_prob, 2)
    draw_odds = round(1 / draw_prob, 2)
    away_odds = round(1 / away_prob, 2)

    return {
        "fixture": f"{home_team} vs {away_team}",
        "1X2": {
            "home_win": {"probability": home_prob, "odds": home_odds},
            "draw": {"probability": draw_prob, "odds": draw_odds},
            "away_win": {"probability": away_prob, "odds": away_odds}
        },
        "BTTS": {"yes": 0.6, "no": 0.4},
        "Over/Under 2.5": {"over": 0.55, "under": 0.45},
        "Correct Score (most likely)": "1-0",
        "Best Value Bet": "Home Win",
        "Hidden Upset Angle": "Low chance away win, high variance possible"
    }

# --- Routes ---

@app.route("/")
def home():
    return jsonify({"status": "Football API Connector Running ✅"})

@app.route("/fixtures/today")
def fixtures_today():
    today_str = datetime.today().strftime("%Y-%m-%d")
    url = f"{BASE_URL}/fixtures?date={today_str}"
    response = requests.get(url, headers=HEADERS)
    return jsonify(response.json())

@app.route("/fixtures/live")
def fixtures_live():
    url = f"{BASE_URL}/fixtures?live=all"
    response = requests.get(url, headers=HEADERS)
    return jsonify(response.json())

@app.route("/predict/top/<int:n>")
def predict_top_matches(n):
    """
    Fetch today's fixtures and return top N high-confidence predictions.
    """
    today_str = datetime.today().strftime("%Y-%m-%d")
    url = f"{BASE_URL}/fixtures?date={today_str}"
    response = requests.get(url, headers=HEADERS)
    data = response.json().get("response", [])

    # Generate predictions for top N fixtures
    predictions = [generate_prediction(fix) for fix in data[:n]]
    return jsonify({"top_predictions": predictions})

@app.route("/routes")
def list_routes():
    """
    Display all registered routes in this Flask app.
    """
    import urllib
    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = urllib.parse.unquote(f"{rule.endpoint}: {methods} {rule}")
        output.append(line)
    return jsonify({"available_routes": output})

# --- Run App ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


