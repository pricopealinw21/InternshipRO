import threading
import time
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
from database.db import upsert_jobs, get_jobs, get_stats
from scrapers import hipo, ejobs, bestjobs

app = Flask(__name__)

# ── Demo data (fallback daca scraperele nu gasesc nimic) ──────────────────────
def h(hours=0): return (datetime.now() - timedelta(hours=hours)).isoformat()
def d(days=0):  return (datetime.now() - timedelta(days=days)).isoformat()

DEMO_JOBS = [
    {"title": "Student Trainee – Software Development",  "company": "Orange Romania",        "location": "Bucuresti", "url": "https://hipo.ro/job/1",  "source": "Hipo",     "tags": ["Python","DevOps","AI"],            "posted_at": h(0)},
    {"title": "Internship – Data Analyst",               "company": "ING Bank Romania",      "location": "Bucuresti", "url": "https://ejobs.ro/job/2",  "source": "eJobs",    "tags": ["SQL","Data","Finance","Excel"],     "posted_at": h(2)},
    {"title": "Junior Frontend Developer Internship",    "company": "Endava",                "location": "Cluj",      "url": "https://bestjobs.eu/1",  "source": "Bestjobs", "tags": ["React","JavaScript","IT"],          "posted_at": h(4)},
    {"title": "Internship – Cybersecurity Analyst",      "company": "Bitdefender",           "location": "Bucuresti", "url": "https://hipo.ro/job/3",  "source": "Hipo",     "tags": ["Cybersecurity","Python","IT"],      "posted_at": h(6)},
    {"title": "Internship – Python Developer",           "company": "Stefanini Romania",     "location": "Bucuresti", "url": "https://ejobs.ro/job/4",  "source": "eJobs",    "tags": ["Python","Django","IT","SQL"],       "posted_at": h(8)},
    {"title": "Stagiu Practica – HR & Recruitment",      "company": "Vodafone Romania",      "location": "Bucuresti", "url": "https://ejobs.ro/job/5",  "source": "eJobs",    "tags": ["HR","Comunicare","Marketing"],      "posted_at": h(10)},
    {"title": "Internship – Backend Java Developer",     "company": "Accenture Romania",     "location": "Bucuresti", "url": "https://bestjobs.eu/2",  "source": "Bestjobs", "tags": ["Java","Spring Boot","IT","SQL"],    "posted_at": h(12)},
    {"title": "Marketing Intern – Digital & Social",     "company": "Procter & Gamble",      "location": "Bucuresti", "url": "https://hipo.ro/job/6",  "source": "Hipo",     "tags": ["Marketing","Social Media"],         "posted_at": h(14)},
    {"title": "Internship – Machine Learning Engineer",  "company": "Adobe Romania",         "location": "Bucuresti", "url": "https://ejobs.ro/job/6",  "source": "eJobs",    "tags": ["Python","ML","Data","IT"],          "posted_at": h(18)},
    {"title": "Practica – Analiza Financiara",           "company": "BCR",                   "location": "Bucuresti", "url": "https://bestjobs.eu/3",  "source": "Bestjobs", "tags": ["Finance","Excel","Banking"],        "posted_at": h(20)},
    {"title": "Internship – DevOps Engineer",            "company": "Continental Romania",   "location": "Iasi",      "url": "https://hipo.ro/job/7",  "source": "Hipo",     "tags": ["DevOps","Linux","Docker","IT"],     "posted_at": d(1)},
    {"title": "Stagiu – Business Intelligence",          "company": "Deloitte Romania",      "location": "Bucuresti", "url": "https://ejobs.ro/job/7",  "source": "eJobs",    "tags": ["SQL","Power BI","Data","Finance"],  "posted_at": d(1)},
    {"title": "Internship – iOS Developer",              "company": "UiPath",                "location": "Bucuresti", "url": "https://bestjobs.eu/4",  "source": "Bestjobs", "tags": ["Swift","iOS","IT"],                 "posted_at": d(1)},
    {"title": "Internship – Cloud & Infrastructure",     "company": "Microsoft Romania",     "location": "Bucuresti", "url": "https://hipo.ro/job/8",  "source": "Hipo",     "tags": ["Azure","Cloud","DevOps","IT"],      "posted_at": d(2)},
    {"title": "Practica – Contabilitate & Audit",        "company": "PwC Romania",           "location": "Bucuresti", "url": "https://ejobs.ro/job/8",  "source": "eJobs",    "tags": ["Finance","Audit","Excel"],          "posted_at": d(2)},
    {"title": "Internship – Full Stack Developer",       "company": "Tremend Software",      "location": "Timisoara", "url": "https://bestjobs.eu/5",  "source": "Bestjobs", "tags": ["React","Node.js","IT","SQL"],       "posted_at": d(2)},
    {"title": "Stagiu – Analiza Risc & Compliance",      "company": "BRD Groupe Societe",    "location": "Bucuresti", "url": "https://hipo.ro/job/9",  "source": "Hipo",     "tags": ["Finance","Risk","Banking","Excel"], "posted_at": d(3)},
    {"title": "Internship – Android Developer",          "company": "TypingDNA",             "location": "Cluj",      "url": "https://ejobs.ro/job/9",  "source": "eJobs",    "tags": ["Kotlin","Android","IT"],            "posted_at": d(3)},
    {"title": "Intern – Supply Chain & Logistics",       "company": "Kaufland Romania",      "location": "Bucuresti", "url": "https://bestjobs.eu/6",  "source": "Bestjobs", "tags": ["Logistica","Excel","Operatiuni"],   "posted_at": d(3)},
    {"title": "Internship – QA Test Engineer",           "company": "Luxoft Romania",        "location": "Bucuresti", "url": "https://hipo.ro/job/10", "source": "Hipo",     "tags": ["QA","Testing","IT","Java"],         "posted_at": d(4)},
    {"title": "Stagiu Practica – Marketing Digital",     "company": "eMAG",                  "location": "Bucuresti", "url": "https://ejobs.ro/job/10", "source": "eJobs",   "tags": ["Marketing","SEO","Google Ads"],     "posted_at": d(4)},
    {"title": "Internship – Embedded Systems",           "company": "Bosch Romania",         "location": "Cluj",      "url": "https://bestjobs.eu/7",  "source": "Bestjobs", "tags": ["C/C++","Embedded","IT"],            "posted_at": d(4)},
    {"title": "Internship – Network Security",           "company": "Cisco Romania",         "location": "Bucuresti", "url": "https://hipo.ro/job/11", "source": "Hipo",     "tags": ["Networking","Cybersecurity","IT"],  "posted_at": d(5)},
    {"title": "Stagiu – Corporate Finance",              "company": "EY Romania",            "location": "Bucuresti", "url": "https://ejobs.ro/job/11", "source": "eJobs",   "tags": ["Finance","M&A","Excel","Banking"],  "posted_at": d(5)},
    {"title": "Internship – AI & NLP Engineer",          "company": "Telekom Romania",       "location": "Bucuresti", "url": "https://bestjobs.eu/8",  "source": "Bestjobs", "tags": ["Python","NLP","AI","ML"],           "posted_at": d(5)},
    {"title": "Practica – Dezvoltare Produs",            "company": "Dacia Renault Group",   "location": "Pitesti",   "url": "https://hipo.ro/job/12", "source": "Hipo",     "tags": ["Inginerie","CAD","Automotive"],     "posted_at": d(6)},
    {"title": "Internship – SAP Consultant",             "company": "Capgemini Romania",     "location": "Bucuresti", "url": "https://ejobs.ro/job/12", "source": "eJobs",   "tags": ["SAP","IT","Finance","ERP"],         "posted_at": d(6)},
    {"title": "Stagiu – Comunicare & PR",                "company": "Coca-Cola HBC Romania", "location": "Bucuresti", "url": "https://bestjobs.eu/9",  "source": "Bestjobs", "tags": ["PR","Comunicare","Marketing"],      "posted_at": d(6)},
    {"title": "Internship – Game Developer",             "company": "Amber Studio",          "location": "Bucuresti", "url": "https://hipo.ro/job/13", "source": "Hipo",     "tags": ["Unity","C#","IT","Gaming"],         "posted_at": d(7)},
    {"title": "Internship – Data Science",               "company": "Ursus Breweries",       "location": "Bucuresti", "url": "https://ejobs.ro/job/13", "source": "eJobs",   "tags": ["Python","Data","SQL","ML"],         "posted_at": d(7)},
    {"title": "Stagiu – Operatiuni Bancare",             "company": "Raiffeisen Bank",       "location": "Bucuresti", "url": "https://bestjobs.eu/10", "source": "Bestjobs", "tags": ["Banking","Finance","Excel"],        "posted_at": d(7)},
    {"title": "Internship – UI/UX Designer",             "company": "Yonder",                "location": "Cluj",      "url": "https://hipo.ro/job/14", "source": "Hipo",     "tags": ["Figma","UI/UX","Design"],           "posted_at": d(8)},
    {"title": "Practica – Resurse Umane",                "company": "Lidl Romania",          "location": "Bucuresti", "url": "https://ejobs.ro/job/14", "source": "eJobs",   "tags": ["HR","Recrutare","Comunicare"],      "posted_at": d(8)},
    {"title": "Internship – Blockchain Developer",       "company": "MultiversX",            "location": "Bucuresti", "url": "https://bestjobs.eu/11", "source": "Bestjobs", "tags": ["Blockchain","Rust","IT","Web3"],    "posted_at": d(8)},
    {"title": "Stagiu – Analiza Date & Raportare",       "company": "Allianz Tiriac",        "location": "Bucuresti", "url": "https://hipo.ro/job/15", "source": "Hipo",     "tags": ["Excel","SQL","Finance","Data"],     "posted_at": d(9)},
    {"title": "Internship – .NET Developer",             "company": "Atos Romania",          "location": "Timisoara", "url": "https://ejobs.ro/job/15", "source": "eJobs",   "tags": ["C#",".NET","IT","SQL"],             "posted_at": d(9)},
    {"title": "Intern – Brand & Trade Marketing",        "company": "Philip Morris Romania", "location": "Bucuresti", "url": "https://bestjobs.eu/12", "source": "Bestjobs", "tags": ["Marketing","Brand","Excel"],        "posted_at": d(9)},
    {"title": "Internship – Penetration Tester",         "company": "Crowdstrike Romania",   "location": "Remote",    "url": "https://hipo.ro/job/16", "source": "Hipo",     "tags": ["Cybersecurity","Ethical Hacking"],  "posted_at": d(10)},
    {"title": "Stagiu – Logistica & Achizitii",          "company": "DHL Romania",           "location": "Bucuresti", "url": "https://ejobs.ro/job/16", "source": "eJobs",   "tags": ["Logistica","Supply Chain"],         "posted_at": d(10)},
    {"title": "Internship – Power BI Developer",         "company": "KPMG Romania",          "location": "Bucuresti", "url": "https://bestjobs.eu/13", "source": "Bestjobs", "tags": ["Power BI","SQL","Data","Finance"],  "posted_at": d(10)},
]

# ── Scraping ──────────────────────────────────────────────────────────────────
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
        print("[Scraper] Niciun anunt real — folosim demo data")
        upsert_jobs(DEMO_JOBS)

def background_loop():
    run_scrapers()
    while True:
        time.sleep(6 * 3600)  # Re-scrapeaza la fiecare 6 ore
        run_scrapers()

# Porneste scraping-ul in background
threading.Thread(target=background_loop, daemon=True).start()

# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/jobs")
def api_jobs():
    jobs = get_jobs()
    if not jobs:
        jobs = DEMO_JOBS
    return jsonify({"jobs": jobs, "count": len(jobs)})

@app.route("/api/stats")
def api_stats():
    stats = get_stats()
    if stats["total"] == 0:
        stats = {"total": len(DEMO_JOBS), "today": 5, "companies": 30}
    stats["last_update"] = datetime.now().strftime("%H:%M")
    return jsonify(stats)

@app.route("/api/scrape", methods=["POST"])
def api_scrape():
    threading.Thread(target=run_scrapers, daemon=True).start()
    return jsonify({"status": "started"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
