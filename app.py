from flask import Flask, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

API_KEY = os.getenv("API_FOOTBALL_KEY")
BASE_URL = "https://v3.football.api-sports.io"
headers = {"x-apisports-key": API_KEY}


@app.route("/")
def home():
    return jsonify({"status": "Football API Connector Running ✅"})


@app.route("/fixtures/today")
def fixtures_today():
    url = f"{BASE_URL}/fixtures?date=2025-10-12"
    response = requests.get(url, headers=headers)
    return jsonify(response.json())


@app.route("/fixtures/live")
def fixtures_live():
    url = f"{BASE_URL}/fixtures?live=all"
    response = requests.get(url, headers=headers)
    return jsonify(response.json())


@app.route("/fixtures/league/<league_id>")
def fixtures_by_league(league_id):
    url = f"{BASE_URL}/fixtures?league={league_id}&next=10"
    response = requests.get(url, headers=headers)
    return jsonify(response.json())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
