from flask import Flask, jsonify, request
import requests
import os
from dotenv import load_dotenv
from datetime import date

load_dotenv()
app = Flask(__name__)

API_KEY = os.getenv("API_FOOTBALL_KEY")
BASE_URL = "https://v3.football.api-sports.io"
headers = {"x-apisports-key": API_KEY}


@app.route("/")
def home():
    return jsonify({"status": "Football API Connector Running ✅"})


# ✅ Dynamic date route — you can request any date (YYYY-MM-DD)
@app.route("/fixtures/date/<string:match_date>")
def fixtures_by_date(match_date):
    """
    Example:
      /fixtures/date/2025-10-15
      /fixtures/date/2024-12-01
    """
    url = f"{BASE_URL}/fixtures?date={match_date}"
    response = requests.get(url, headers=headers)
    return jsonify(response.json())


# ✅ Today's fixtures (uses system date)
@app.route("/fixtures/today")
def fixtures_today():
    today = date.today().isoformat()  # auto-gets current date
    url = f"{BASE_URL}/fixtures?date={today}"
    response = requests.get(url, headers=headers)
    return jsonify(response.json())


# ✅ Live fixtures
@app.route("/fixtures/live")
def fixtures_live():
    url = f"{BASE_URL}/fixtures?live=all"
    response = requests.get(url, headers=headers)
    return jsonify(response.json())


# ✅ Route list
@app.route("/routes")
def list_routes():
    """
    Display all registered routes in this Flask app
    """
    import urllib
    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = urllib.parse.unquote(f"{rule.endpoint}: {methods} {rule}")
        output.append(line)
    return jsonify({"available_routes": output})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
