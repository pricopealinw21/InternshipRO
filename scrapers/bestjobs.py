from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime

PAGES = [
    "https://www.bestjobs.eu/locuri-de-munca/internship",
    "https://www.bestjobs.eu/locuri-de-munca/internship?page=2",
    "https://www.bestjobs.eu/locuri-de-munca/stagiu-de-practica",
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

                    for _ in range(4):
                        page.evaluate("window.scrollBy(0, 800)")
                        page.wait_for_timeout(700)
                    page.wait_for_timeout(1500)

                    soup = BeautifulSoup(page.content(), "html.parser")
                    card_links = soup.select("a.absolute.inset-0")

                    if not card_links:
                        continue

                    for link_el in card_links:
                        try:
                            card = link_el.parent

                            href = link_el.get("href", "")
                            full_url = href if href.startswith("http") else f"https://www.bestjobs.eu{href}"

                            if full_url in seen_urls:
                                continue
                            seen_urls.add(full_url)

                            title_el   = card.select_one("h2")
                            company_el = card.select_one("div.col-span-7 div.mt-2.line-clamp-1")
                            loc_el     = card.select_one("a[href*='locuri-de-munca-in-']")

                            if not title_el:
                                continue

                            jobs.append({
                                "title":     title_el.get_text(strip=True),
                                "company":   company_el.get_text(strip=True) if company_el else "Nedefinit",
                                "location":  loc_el.get_text(strip=True) if loc_el else "Romania",
                                "url":       full_url,
                                "source":    "Bestjobs",
                                "tags":      [],
                                "posted_at": datetime.now().isoformat(),
                            })
                        except Exception:
                            continue

                except Exception as e:
                    print(f"[Bestjobs] Eroare la {url}: {e}")

            browser.close()

    except Exception as e:
        print(f"[Bestjobs] Eroare generala: {e}")

    print(f"[Bestjobs] {len(jobs)} anunturi gasite")
    return jobs
