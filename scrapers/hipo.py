from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime

URLS = [
    "https://www.hipo.ro/locuri-de-munca/cautajobfiltre/Toate-Domeniile/Toate-Orasele/0/internship",
    "https://www.hipo.ro/locuri-de-munca/cautajobfiltre/Toate-Domeniile/Bucuresti/0/internship",
    "https://www.hipo.ro/locuri-de-munca/cautajobfiltre/Toate-Domeniile/Toate-Orasele/0/stagiu",
]

def scrape() -> list[dict]:
    jobs = []
    seen_urls = set()

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ))

            for url in URLS:
                try:
                    page.goto(url, wait_until="networkidle", timeout=25000)
                    page.wait_for_timeout(2000)

                    try:
                        page.click("text=Accept cookie", timeout=2000)
                        page.wait_for_timeout(500)
                    except:
                        pass

                    soup = BeautifulSoup(page.content(), "html.parser")

                    for card in soup.select("div.row.g-4"):
                        try:
                            title_el   = card.select_one("a.job-title h5, a.job-title")
                            company_el = card.select_one("p.company-name span, p.company-name")
                            link_el    = card.select_one("a.job-title")
                            loc_els    = card.select("span.text-truncate")
                            date_el    = card.select_one("small")

                            if not title_el or not link_el:
                                continue

                            href = link_el.get("href","")
                            full_url = href if href.startswith("http") else f"https://www.hipo.ro{href}"

                            if full_url in seen_urls:
                                continue
                            seen_urls.add(full_url)

                            location = ""
                            for loc in loc_els:
                                t = loc.get_text(strip=True)
                                if t and not any(x in t for x in ["-07-", "-06-", "-05-", "2026", "2025"]):
                                    location = t
                                    break

                            jobs.append({
                                "title":     title_el.get_text(strip=True),
                                "company":   company_el.get_text(strip=True) if company_el else "Nedefinit",
                                "location":  location or "Romania",
                                "url":       full_url,
                                "source":    "Hipo",
                                "tags":      [],
                                "posted_at": datetime.now().isoformat(),
                            })
                        except Exception:
                            continue

                except Exception as e:
                    print(f"[Hipo] Eroare la {url}: {e}")

            browser.close()

    except Exception as e:
        print(f"[Hipo] Eroare generala: {e}")

    print(f"[Hipo] {len(jobs)} anunturi gasite")
    return jobs
