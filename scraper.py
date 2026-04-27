import csv
import re
from pathlib import Path
from typing import List, Dict

from bs4 import BeautifulSoup

# 📁 Folder containing HTML files
HTML_DIR = Path(__file__).parent / "html_files"

# 📄 Output CSV
OUTPUT_CSV = Path(__file__).parent / "investor_data.csv"

# 🔍 Regex patterns
PHONE_REGEX = re.compile(r"(?:\+\d{1,3}[\s-]?)?(?:\(?\d{2,4}\)?[\s-]?)?\d{3}[\s-]?\d{3,4}")

SOCIAL_PATTERNS = {
    "LinkedIn": re.compile(r"linkedin\.com", re.I),
    "Twitter/X": re.compile(r"twitter\.com|x\.com", re.I),
    "Facebook": re.compile(r"facebook\.com", re.I),
}

# 🎯 Controlled values
VALID_STAGES = [
    "Pre-Seed", "Seed", "Series A", "Series B",
    "Series C", "Series D", "Early Stage Venture",
    "Late Stage Venture"
]

VALID_FOCUS = [
    "FinTech", "Financial Services", "Software",
    "Health Care", "Media and Entertainment",
    "Education", "Real Estate", "Venture Capital",
    "Insurance", "Consumer Internet", "Mobile",
    "Information Technology", "E-Commerce"
]

# 🧩 Helpers
def safe_text(el):
    return el.get_text(strip=True) if el else ""


def extract_social_links(card) -> Dict[str, str]:
    links = {key: "" for key in SOCIAL_PATTERNS}

    for a in card.find_all("a", href=True):
        href = a["href"].strip()

        for name, pattern in SOCIAL_PATTERNS.items():
            if pattern.search(href):
                links[name] = href

    return links


def extract_section(card, label: str) -> str:
    for el in card.find_all(string=re.compile(label, re.I)):
        parent = el.parent
        texts = []

        for sib in parent.find_next_siblings():
            txt = sib.get_text(" ", strip=True)

            if not txt:
                continue

            if ":" in txt and len(txt) < 40:
                break

            texts.append(txt)

        if texts:
            return " ".join(texts)

    return ""


def smart_split(text: str) -> List[str]:
    if not text:
        return []

    text = re.sub(r"\+\d+\s*more", "", text)

    # Split camelCase joins
    text = re.sub(r"(?<=[a-z])(?=[A-Z])", "|", text)

    return [p.strip() for p in text.split("|") if p.strip()]


def clean_past_investments(text: str) -> str:
    if not text:
        return ""

    text = re.sub(r"\+\d+\s*more", "", text)

    # FIX: Only split if it's clearly concatenated
    words = re.findall(r"[A-Z][a-zA-Z]+", text)

    if len(words) > 1:
        return ", ".join(words)

    return text


# 🧾 Parse single investor
def parse_investor_card(card) -> Dict[str, str]:
    data = {
        "Name": "",
        "Email": "",
        "Phone": "",
        "LinkedIn": "",
        "Twitter/X": "",
        "Facebook": "",
        "Investor Type": "",
        "Investment Stages": "",
        "Investment Focuses": "",
        "Address": "",
        "Past Investments": "",
    }

    # 🔹 Name
    name_el = card.select_one("[class*='investorName']") or card.find(["h1", "h2", "h3"])
    name = safe_text(name_el)
    name = re.sub(r"Verified", "", name, flags=re.I).strip()
    data["Name"] = name

    if not name:
        return None  # 🚫 skip invalid cards

    # 🔹 Socials
    data.update(extract_social_links(card))

    # 🔹 Full text
    card_text = card.get_text(" ", strip=True)

    # 🔹 Email (strict)
    for a in card.find_all("a", href=True):
        if a["href"].startswith("mailto:"):
            data["Email"] = a["href"].replace("mailto:", "").strip()
            break

    # 🔹 Phone
    phone_match = PHONE_REGEX.search(card_text)
    if phone_match:
        data["Phone"] = phone_match.group(0)

    # 🔹 Investor Type
    type_match = re.search(
        r"(venture capital|angel|micro vc|private equity|investor)",
        card_text,
        re.I
    )
    if type_match:
        data["Investor Type"] = type_match.group(0).title()

    # 🔹 Investment Stages
    stage_text = extract_section(card, "Investment stages")
    stages = [s for s in VALID_STAGES if s.lower() in stage_text.lower()]
    data["Investment Stages"] = ", ".join(stages)

    # 🔹 Investment Focuses
    focus_text = extract_section(card, "Investment focuses")
    split_focus = smart_split(focus_text)

    focuses = []
    for f in VALID_FOCUS:
        if any(f.lower() in part.lower() for part in split_focus):
            focuses.append(f)

    data["Investment Focuses"] = ", ".join(focuses)

    # 🔹 Past Investments (FIXED)
    past_text = extract_section(card, "Past investments")
    data["Past Investments"] = clean_past_investments(past_text)

    # 🔹 Address
    address_match = re.search(
        r"(San Francisco|London|New York|Berlin|Paris|India|USA|UK|Toronto|Chicago)",
        card_text,
        re.I
    )
    if address_match:
        data["Address"] = address_match.group(0)

    return data


# 📂 Process all files
def scrape_html_files() -> List[Dict[str, str]]:
    investors = []
    seen = set()  # 🔥 deduplication

    for html_path in HTML_DIR.glob("*.html"):
        print(f"Processing: {html_path.name}")

        with open(html_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "lxml")

        # 🎯 CRITICAL FIX: target real cards only
        cards = soup.select("div[class*='card'], div[class*='investor']")

        for card in cards:
            inv = parse_investor_card(card)

            if not inv:
                continue

            # 🔥 dedupe key
            key = (inv["Name"], inv["Email"], inv["LinkedIn"])

            if key not in seen:
                seen.add(key)
                investors.append(inv)

    return investors


# 📄 Write CSV
def write_to_csv(investors: List[Dict[str, str]]):
    if not investors:
        print("❌ No data extracted.")
        return

    fieldnames = list(investors[0].keys())

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(investors)

    print(f"✅ Extracted {len(investors)} investors → {OUTPUT_CSV}")


# 🚀 Run
if __name__ == "__main__":
    data = scrape_html_files()

    for d in data[:3]:
        print("\n--- SAMPLE ---")
        for k, v in d.items():
            print(f"{k}: {v}")

    write_to_csv(data)