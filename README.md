# InternshipRO

Aplicatie web care strange intr-un singur loc internship-urile de pe **Hipo.ro**, **eJobs.ro** si **Bestjobs.eu**.

Am facut-o pentru ca, atunci cand cautam internship, trebuia sa intru pe 3 site-uri diferite si sa caut acelasi lucru de fiecare data.

## Ce face

- ia anunturile de internship/stagiu de pe cele 3 site-uri (scraping cu Playwright)
- le salveaza intr-o baza de date SQLite, fara duplicate
- cautare, filtre si paginare
- poti salva anunturile care iti plac (raman in browser, cu localStorage)
- reface scraping-ul automat la fiecare 6 ore

## Tehnologii

- Python + Flask (backend)
- Playwright + BeautifulSoup (scraping)
- SQLite
- HTML, CSS si JavaScript simplu (fara framework)

## Cum il rulezi

```bash
git clone https://github.com/pricopealinw21/InternshipRO.git
cd InternshipRO

pip install -r requirements.txt
playwright install chromium

py app.py
```

Apoi deschizi http://localhost:5000. La pornire face primul scraping, dureaza putin pana apar anunturile.

## Structura

```
app.py          - serverul Flask + scraping-ul in background
scrapers/       - cate un fisier pentru fiecare site (hipo, ejobs, bestjobs)
database/db.py  - lucrul cu SQLite
templates/      - pagina HTML
static/         - CSS si JavaScript
```

## Probleme cunoscute

- daca un site isi schimba structura HTML, scraper-ul pentru el trebuie actualizat

---

Alin Pricope, student la Cibernetica, Statistica si Informatica Economica, ASE Bucuresti
