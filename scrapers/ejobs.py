import re
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime

PAGES = [
    "https://www.ejobs.ro/locuri-de-munca/internship",
    "https://www.ejobs.ro/locuri-de-munca/internship?page=2",
    "https://www.ejobs.ro/locuri-de-munca/internship?page=3",
    "https://www.ejobs.ro/locuri-de-munca/stagiu",
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

            cookie_accepted = False
            for url in PAGES:
                try:
                    page.goto(url, wait_until="networkidle", timeout=30000)
                    page.wait_for_timeout(2000)

                    if not cookie_accepted:
                        try:
                            page.click("text=Accept", timeout=2000)
                            page.wait_for_timeout(1000)
                            cookie_accepted = True
                        except:
                            pass

                    for _ in range(5):
                        page.evaluate("window.scrollBy(0, 800)")
                        page.wait_for_timeout(600)
                    page.wait_for_timeout(1000)

                    soup = BeautifulSoup(page.content(), "html.parser")
                    cards = soup.select("li.job-card-wrapper")

                    if not cards:
                        continue

                    for card in cards:
                        try:
                            title_el   = card.select_one(".job-card-content-middle__title")
                            company_el = card.select_one(".job-card-content-middle__info--darker")
                            link_el    = card.select_one(".job-card-content-middle__title a")
                            loc_els    = card.select(".job-card-content-middle__info:not(.job-card-content-middle__info--darker)")

                            if not title_el or not link_el:
                                continue

                            href = link_el.get("href", "")
                            full_url = href if href.startswith("http") else f"https://www.ejobs.ro{href}"

                            if full_url in seen_urls:
                                continue
                            seen_urls.add(full_url)

                            location = ""
                            for loc in loc_els:
                                t = loc.get_text(strip=True)
                                if t and len(t) > 1:
                                    t = re.sub(r"și alte\d+ orașe", "", t).strip().rstrip(",")
                                    if t:
                                        location = t
                                        break

                            jobs.append({
                                "title":     title_el.get_text(strip=True),
                                "company":   company_el.get_text(strip=True) if company_el else "Nedefinit",
                                "location":  location or "Romania",
                                "url":       full_url,
                                "source":    "eJobs",
                                "tags":      [],
                                "posted_at": datetime.now().isoformat(),
                            })
                        except Exception:
                            continue

                except Exception as e:
                    print(f"[eJobs] Eroare la {url}: {e}")

            browser.close()

    except Exception as e:
        print(f"[eJobs] Eroare generala: {e}")

    print(f"[eJobs] {len(jobs)} anunturi gasite")
    return jobs
