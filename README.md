# HTML Extractor (VC Scraper)

A lightweight Python-based scraper to extract structured data about investors (Venture Capitalists, Angels, etc.) from HTML files and convert it into a clean dataset (CSV-ready for PostgreSQL, Google Sheets, or APIs).

---

## 🚀 Features

* 📄 Parses multiple HTML files (bulk processing)
* 🧠 Intelligent data extraction:

  * Name
  * Email
  * Phone
  * Social links (LinkedIn, Twitter/X, Facebook)
  * Investor Type
  * Investment Stages
  * Investment Focuses
  * Address
  * Past Investments
* 🧹 Cleans messy UI data (merged text, duplicates, "+X more")
* 🔁 Deduplicates records
* 📊 Outputs clean CSV
* 🐳 Docker support (no local Python dependency needed)

---

## 📁 Project Structure

```
html_extractor/
│
├── app/
│   └── scraper.py          # Main scraping script
│
├── html_files/             # Input HTML files
│   ├── file1.html
│   ├── file2.html
│   └── ...
│
├── investor_data.csv       # Output file
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker setup
├── docker-compose.yml      # Container orchestration
└── README.md
```

---

## ⚙️ Requirements

If running locally:

* Python 3.10+
* pip

If using Docker (recommended):

* Docker
* Docker Compose

---

## 🐳 Run with Docker (Recommended)

### 1. Build and start container

```bash
docker compose up --build
```

### 2. Output

* Extracted data will be saved to:

```
/app/investor_data.csv
```

---

## 💻 Run Locally (Optional)

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run scraper

```bash
python app/scraper.py
```

---

## 📊 Output Format (CSV)

```csv
Name,Email,Phone,LinkedIn,Twitter/X,Facebook,Investor Type,Investment Stages,Investment Focuses,Address,Past Investments
Daniel Kim,daniel.kim@..., +1..., http://linkedin..., Angel,"Seed, Series A","FinTech, Software",USA,SlidePay
```

---

## 🧠 How It Works

1. Loads HTML files from `/html_files`
2. Identifies investor cards using DOM structure
3. Extracts structured fields using:

   * BeautifulSoup (HTML parsing)
   * Regex (emails, phones, cleanup)
4. Cleans messy UI data:

   * Fixes merged text (e.g., `SeedSeriesA`)
   * Removes noise like `+11 more`
5. Deduplicates entries
6. Exports final dataset to CSV

---

## ⚠️ Known Challenges (Handled)

* Nested HTML cards → filtered to avoid duplicates
* Missing structured tags → fallback regex extraction
* UI-merged text → custom split logic
* Duplicate entries → deduplication using unique keys

---

## 🔮 Future Improvements

* ⚡ Async processing for large datasets (100+ files)
* 🗄️ PostgreSQL integration (`asyncpg`)
* 📡 FastAPI endpoint (`/scrape`)
* 📊 Direct Google Sheets export (`gspread`)
* 🔍 Logging & monitoring

---

## 🧑‍💻 Author

**AoneTech**
**Akshat**
CEO | Full Stack AI Developer

---

## 📜 License

This project is for educational and internal use. Modify as needed.
