import threading
import time
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from database.db import upsert_jobs, get_jobs, get_stats
from scrapers import hipo, ejobs, bestjobs

app = Flask(__name__)

# Scraping
def run_scrapers():
    print(f"[Scraper] Start la {datetime.now().strftime('%H:%M:%S')}")
    all_jobs = []
    for scraper in [hipo, ejobs, bestjobs]:
        try:
            all_jobs.extend(scraper.scrape())
        except Exception as e:
            print(f"[Scraper] Eroare: {e}")

    if all_jobs:
        upsert_jobs(all_jobs)
        print(f"[Scraper] {len(all_jobs)} anunturi salvate in DB")
    else:
        print("[Scraper] Nu s-a gasit niciun anunt")

def background_loop():
    run_scrapers()
    while True:
        time.sleep(6 * 3600)  # Re-scrapeaza la fiecare 6 ore
        run_scrapers()

# Porneste scraping-ul in background
threading.Thread(target=background_loop, daemon=True).start()

# Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/jobs")
def api_jobs():
    jobs = get_jobs()
    return jsonify({"jobs": jobs, "count": len(jobs)})

@app.route("/api/stats")
def api_stats():
    stats = get_stats()
    stats["last_update"] = datetime.now().strftime("%H:%M")
    return jsonify(stats)

@app.route("/api/scrape", methods=["POST"])
def api_scrape():
    threading.Thread(target=run_scrapers, daemon=True).start()
    return jsonify({"status": "started"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
