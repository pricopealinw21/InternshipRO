# InternshipRO

Agregator de internshipuri din România care colectează automat anunțuri reale de pe **Hipo.ro**, **eJobs.ro** și **Bestjobs.eu**.

![InternshipRO Screenshot](screenshot.png)

## Ce face

- Scrapeaza automat 150+ internshipuri în timp real din 3 surse
- Interfață inspirată din LinkedIn cu filtrare, căutare și paginare
- Salvare joburi favorite în browser (localStorage)
- Re-scraping automat la fiecare 6 ore în background
- Highlight termeni căutați în rezultate

## Tech Stack

| Layer | Tehnologie |
|-------|-----------|
| Backend | Python, Flask |
| Scraping | Playwright (headless Chromium), BeautifulSoup4 |
| Baza de date | SQLite |
| Frontend | HTML, CSS, JavaScript (vanilla) |

## Instalare

```bash
# 1. Cloneaza repo-ul
git clone https://github.com/pricopealinw21/InternshipRO.git
cd InternshipRO

# 2. Instaleaza dependentele
pip install -r requirements.txt
playwright install chromium

# 3. Porneste aplicatia
py app.py
```

Deschide **http://localhost:5000** în browser.

La pornire, aplicația scrapeaza automat toate sursele și afișează joburile în timp real.

## Structura proiectului

```
InternshipRO/
├── app.py                  # Flask server + background scraping
├── scrapers/
│   ├── hipo.py             # Scraper Hipo.ro
│   ├── ejobs.py            # Scraper eJobs.ro
│   └── bestjobs.py         # Scraper Bestjobs.eu
├── database/
│   └── db.py               # SQLite (upsert, query)
├── templates/
│   └── index.html          # UI principal
└── static/
    ├── css/style.css
    └── js/app.js           # Filtrare, paginare, salvare joburi
```

## Autor

**Alin Pricope** — student Cibernetică, Statistică și Informatică Economică @ ASE București
