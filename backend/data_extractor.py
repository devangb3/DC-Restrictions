import csv
import json
from bs4 import BeautifulSoup

HTML_FILE = "tercero.html"
CSV_FILE  = "menu2.csv"

# ---------- parse the HTML ----------
with open(HTML_FILE, encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

tabs = soup.find("div", id="tabs")
if not tabs:
    raise RuntimeError("Could not find the menu tab container")

rows = []

day_divs = tabs.find_all(
    "div",
    id=lambda x: x and x.startswith("tab") and x.endswith("content")
)

for day_div in day_divs:
    day_header = day_div.find("h3")
    if not day_header:
        continue
    day_text = day_header.get_text(strip=True)

    for meal_h4 in day_div.find_all("h4"):
        meal_name = meal_h4.get_text(strip=True).lower()
        if meal_name not in {"breakfast", "lunch", "dinner"}:
            continue

        recipe_dict = {}

        # walk forward until the next h4/h3
        for sib in meal_h4.find_all_next():
            if sib.name in {"h4", "h3"}:
                break
            if sib.name != "li" or "trigger" not in sib.get("class", []):
                continue

            # ----- recipe name(s) -----
            spans = [
                s for s in sib.find_all("span")
                if "collapsible-heading-status" not in s.get("class", [])
            ]
            if not spans:
                continue
            raw_title = spans[0].get_text(" ", strip=True)
            titles = [t.strip() for t in raw_title.split("||") if t.strip()]

            # ----- nutrition details -----
            data = {}
            for h6 in sib.find_all("h6"):
                label = h6.get_text(strip=True).rstrip(":")
                val   = h6.find_next("p")
                if val:
                    data[label] = val.get_text(strip=True).lstrip(":").strip()

            # save the same nutrition block under every title in this line
            for title in titles:
                if data:                       # only store non‑empty entries
                    recipe_dict[title] = data

        if recipe_dict:
            rows.append({
                "Day": day_text,
                "Meal Time": meal_name.title(),
                "Recipe Dict": json.dumps(recipe_dict, ensure_ascii=False)
            })

# ---------- write CSV ----------
with open(CSV_FILE, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["Day", "Meal Time", "Recipe Dict"])
    writer.writeheader()
    writer.writerows(rows)

print(f"✓ Extracted {len(rows)} meal blocks → {CSV_FILE}")
