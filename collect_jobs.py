"""
collect_jobs.py - Kumpulkan lowongan IT dari JSearch (RapidAPI).
Dioptimalkan untuk menambah porsi deskripsi bilingual (MIX) dan Bahasa Indonesia (ID)
pada 8 bidang IT tanpa merusak alur resume atau batas kuota API.
"""
import argparse
import json
import os
import random
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

# ----------------------------------------------------------------------------
# KONFIGURASI (.env)
# ----------------------------------------------------------------------------
API_KEY = os.getenv("RAPIDAPI_KEY", "").strip()
HOST = "jsearch.p.rapidapi.com"
BASE = f"https://{HOST}"
SEARCH_PATH = os.getenv("SEARCH_PATH", "/search-v2").strip()
COUNTRY = os.getenv("COUNTRY", "id").strip()
LANGUAGE = os.getenv("LANGUAGE", "").strip()
DATE_POSTED = os.getenv("DATE_POSTED", "").strip()
TARGET_PER_ROLE = int(os.getenv("TARGET_PER_ROLE", "150"))
MAX_PAGES = int(os.getenv("MAX_PAGES", "3"))
MAX_REQUESTS = int(os.getenv("MAX_REQUESTS", "100"))
MIN_REMAINING = int(os.getenv("MIN_REMAINING", "3"))
SLEEP_MIN, SLEEP_MAX = 0.8, 2.0

OUT_DIR = Path("data")
RAW_FILE = OUT_DIR / "raw_jobs.jsonl"
DONE_FILE = OUT_DIR / "done_searches.txt"

# 8 Bidang IT dengan variasi frasa Indonesia-Inggris untuk memicu lowongan MIX/ID
ROLES = {
    "frontend": [
        "lowongan frontend developer", "dibutuhkan web developer", 
        "kualifikasi react developer", "front end developer indonesia",
        "lowongan vue developer"
    ],
    "backend": [
        "lowongan backend engineer", "dibutuhkan laravel developer", 
        "kualifikasi node.js developer", "backend developer indonesia",
        "lowongan java developer"
    ],
    "data_analyst": [
        "lowongan data analyst", "dibutuhkan analis data", 
        "kualifikasi business intelligence", "data analyst indonesia",
        "lowongan bi developer"
    ],
    "data_scientist": [
        "lowongan data scientist", "dibutuhkan machine learning engineer", 
        "kualifikasi ai engineer", "data scientist indonesia",
        "lowongan nlp engineer"
    ],
    "uiux": [
        "lowongan ui ux designer", "dibutuhkan product designer", 
        "kualifikasi ux designer", "ui ux designer indonesia",
        "lowongan graphic designer ui"
    ],
    "devops": [
        "lowongan devops engineer", "dibutuhkan cloud engineer", 
        "kualifikasi system administrator", "devops engineer indonesia",
        "lowongan site reliability engineer"
    ],
    "network": [
        "lowongan network engineer", "dibutuhkan network administrator", 
        "kualifikasi teknisi jaringan", "network engineer indonesia",
        "lowongan infrastructure engineer"
    ],
    "qa_tester": [
        "lowongan qa engineer", "dibutuhkan software tester", 
        "kualifikasi quality assurance", "qa tester indonesia",
        "lowongan automation tester"
    ]
}

LOCATIONS = [
    "Jakarta", "Bandung", "Surabaya", "Yogyakarta", "Semarang",
    "Medan", "Bali", "Indonesia"
]

HEADERS = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": HOST}

request_count = 0
last_remaining = None


class BudgetReached(Exception):
    pass


def api_get(path, params=None, retries=3):
    global request_count, last_remaining
    for attempt in range(retries):
        if request_count >= MAX_REQUESTS:
            raise BudgetReached()
        request_count += 1
        try:
            r = requests.get(BASE + path, headers=HEADERS, params=params, timeout=40)
        except requests.RequestException as e:
            print(f"  [!] Error jaringan: {e}. Coba lagi...")
            time.sleep(5 * (attempt + 1))
            continue

        rem = r.headers.get("x-ratelimit-requests-remaining")
        if rem and rem.strip().isdigit():
            last_remaining = int(rem.strip())

        if r.status_code == 200:
            try:
                return r.json()
            except ValueError:
                print("  [!] Respons bukan JSON valid.")
                return None
        if r.status_code == 429:
            wait = 30 * (attempt + 1)
            print(f"  [!] 429 (terlalu cepat / kuota). Tunggu {wait} dtk...")
            time.sleep(wait)
            continue
        if r.status_code in (401, 403):
            sys.exit(f"[X] {r.status_code}: API key salah, belum subscribe JSearch, "
                     f"atau kuota habis. Detail: {r.text[:200]}")
        if r.status_code in (400, 404):
            print(f"  [!] {r.status_code} (parameter ditolak/tidak ada): {r.text[:200]}")
            return None
        print(f"  [!] HTTP {r.status_code}: {r.text[:150]}")
        time.sleep(5)
    return None


def search(query, cursor=None):
    params = {"query": query, "num_pages": 1}
    if COUNTRY:
        params["country"] = COUNTRY
    if cursor:
        params["cursor"] = cursor
    if LANGUAGE:
        params["language"] = LANGUAGE
    if DATE_POSTED:
        params["date_posted"] = DATE_POSTED
    return api_get(SEARCH_PATH, params)


def find_next_cursor(data, current=None):
    if isinstance(data, dict):
        for key in ("next_cursor", "nextCursor", "cursor", "next_page_cursor", "next"):
            val = data.get(key)
            if val and isinstance(val, (str, int)) and str(val) != str(current):
                return str(val)
        for key in ("data", "meta", "pagination", "paging"):
            if isinstance(data.get(key), dict):
                found = find_next_cursor(data[key], current)
                if found:
                    return found
    return None


def extract_jobs(data):
    if isinstance(data, dict):
        if data.get("status") not in (None, "OK"):
            print(f"  [!] Status API: {data.get('status')} {str(data.get('error'))[:150]}")
            return []
        d = data.get("data")
        if isinstance(d, list):
            return [x for x in d if isinstance(x, dict)]
        if isinstance(d, dict):
            for key in ("jobs", "results", "items", "hits"):
                if isinstance(d.get(key), list):
                    return [x for x in d[key] if isinstance(x, dict)]
            for val in d.values():
                if isinstance(val, list) and val and isinstance(val[0], dict):
                    return val
    return []


def load_state():
    OUT_DIR.mkdir(exist_ok=True)
    seen, counts = set(), Counter()
    if RAW_FILE.exists():
        with open(RAW_FILE, encoding="utf-8") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                seen.add(rec["job_id"])
                counts[rec["role_group"]] += 1
    done = set()
    if DONE_FILE.exists():
        done = set(DONE_FILE.read_text(encoding="utf-8").split("\n"))
    return seen, counts, done


def save_job(job_id, role, query, job):
    rec = {
        "job_id": job_id,
        "role_group": role,
        "query": query,
        "fetched_at": datetime.now().isoformat(timespec="seconds"),
        "raw": job
    }
    with open(RAW_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def mark_done(key):
    with open(DONE_FILE, "a", encoding="utf-8") as f:
        f.write(key + "\n")


def pause():
    time.sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))


def make_query(kw, loc):
    if loc == "Indonesia" or "indonesia" in kw.lower():
        return kw
    return f"{kw} in {loc}"


def probe(query):
    data = search(query)
    if data is None:
        print("Tidak ada respons valid.")
        return
    print("Parameter diterima API:", data.get("parameters"))
    if isinstance(data, dict):
        print("Kunci level atas respons:", list(data.keys()))
    jobs = extract_jobs(data)
    print(f"Jumlah lowongan di halaman 1: {len(jobs)}")
    for j in jobs[:5]:
        desc = j.get("job_description") or ""
        print(f" - [{j.get('job_country')}] {j.get('job_title')} | {j.get('employer_name')} | "
              f"deskripsi: {len(desc)} karakter")


def main():
    global COUNTRY, LANGUAGE
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", metavar="QUERY", help="uji satu pencarian, tanpa menyimpan")
    ap.add_argument("--country", help="override COUNTRY")
    ap.add_argument("--language", help="override LANGUAGE")
    args = ap.parse_args()

    if args.country is not None:
        COUNTRY = args.country.strip()
    if args.language is not None:
        LANGUAGE = args.language.strip()

    if not API_KEY:
        sys.exit("[X] RAPIDAPI_KEY kosong. Isi di file .env.")

    if args.probe:
        probe(args.probe)
        return

    seen, counts, done = load_state()
    print(f"Mulai. Tersimpan saat ini: {len(seen)} lowongan. Per peran: {dict(counts)}")

    combos = [
        (role, kw, loc)
        for role, kws in ROLES.items()
        for kw in kws
        for loc in LOCATIONS
    ]
    random.Random(42).shuffle(combos)

    try:
        for role, kw, loc in combos:
            if counts[role] >= TARGET_PER_ROLE:
                continue
            key = f"{role}|{kw}|{loc}"
            if key in done:
                continue
            query = make_query(kw, loc)
            cursor = None
            failed = False
            for page in range(1, MAX_PAGES + 1):
                if last_remaining is not None and last_remaining <= MIN_REMAINING:
                    print(f"Sisa kuota API tinggal {last_remaining}. Berhenti.")
                    raise BudgetReached()

                data = search(query, cursor)
                if data is None:
                    failed = True
                    break

                jobs = extract_jobs(data)
                if not jobs:
                    break

                new = [
                    j for j in jobs
                    if j.get("job_id") and j["job_id"] not in seen and j.get("job_description")
                ]

                for j in new:
                    if counts[role] >= TARGET_PER_ROLE:
                        break
                    save_job(j["job_id"], role, query, j)
                    seen.add(j["job_id"])
                    counts[role] += 1

                rem = f" | sisa kuota: {last_remaining}" if last_remaining is not None else ""
                print(f"[{role}] '{query}' hal.{page}: {len(jobs)} hasil, {len(new)} baru "
                      f"| request: {request_count}/{MAX_REQUESTS}{rem}")

                next_cursor = find_next_cursor(data, cursor)
                if not new or counts[role] >= TARGET_PER_ROLE or not next_cursor:
                    break
                cursor = next_cursor
                pause()

            if not failed:
                mark_done(key)
    except BudgetReached:
        print("\nBerhenti (batas request/kuota). Jalankan lagi nanti untuk melanjutkan.")
    except KeyboardInterrupt:
        print("\nDihentikan manual. Progres tersimpan.")

    print(f"\nTotal tersimpan: {len(seen)} | per peran: {dict(counts)}")
    print(f"Request dipakai pada run ini: {request_count}")


if __name__ == "__main__":
    main()