"""
build_corpus.py - Ubah data mentah (data/raw_jobs.jsonl) menjadi korpus bersih (CSV).

Langkah: parse field JSearch -> bersihkan teks -> deteksi bahasa (ID/EN/MIX)
         -> filter negara & panjang -> buang duplikat -> data/corpus_jobs.csv

Cara pakai:
    python build_corpus.py
    python build_corpus.py --min-chars 400 --country ID
    python build_corpus.py --indonesia-only
"""
import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from bs4 import BeautifulSoup
from langdetect import DetectorFactory, detect
from langdetect.lang_detect_exception import LangDetectException

DetectorFactory.seed = 0

RAW_FILE = Path("data/raw_jobs.jsonl")
OUT_FILE = Path("data/corpus_jobs.csv")

COLUMNS = ["job_id", "job_title", "company", "location", "country", "job_type",
           "posted_at", "description", "role_group", "source", "language",
           "id_ratio", "url"]

# Kata kunci indikator struktural Bahasa Indonesia
ID_KEYWORDS = re.compile(
    r"\b(dibutuhkan|kualifikasi|persyaratan|pengalaman|gaji|lokasi|pria|wanita|"
    r"tanggung\s*jawab|tugas|deskripsi|manfaat|tentang\s*kami|kirim|pelamar|"
    r"pendidikan|minimal|maksimal|kemampuan|menguasai|melakukan|minimal)\b", re.IGNORECASE
)

# Kata kunci indikator struktural Bahasa Inggris
EN_KEYWORDS = re.compile(
    r"\b(requirements?|responsibilities|qualifications?|must\s*have|nice\s*to\s*have|"
    r"about\s*us|about\s*the\s*role|job\s*description|benefits|skills|experience|"
    r"work\s*location|full\s*time|part\s*time|years?\s*of\s*experience)\b", re.IGNORECASE
)


def clean_text(raw):
    """Kembalikan (teks_rata, teks_dengan_baris). Menangani teks biasa maupun HTML."""
    if not raw:
        return "", ""
    s = str(raw)
    if "<" in s and ">" in s:
        s = BeautifulSoup(s, "html.parser").get_text(separator="\n")
    s = s.replace("•", "\n").replace("·", "\n")
    with_lines = re.sub(r"[ \t]+", " ", s)
    with_lines = re.sub(r"\n\s*\n+", "\n", with_lines).strip()
    flat = re.sub(r"\s+", " ", with_lines).strip()
    return flat, with_lines


def detect_language(text_with_lines):
    """
    Deteksi per kalimat/baris + pemeriksaan indikator bilingual (ID/EN/MIX).
    Dirancang presisi untuk menangkap fenomena code-switching pada lowongan kerja di Indonesia.
    """
    parts = re.split(r"\n+|(?<=[.!?])\s+", text_with_lines)
    chunks = [c.strip() for c in parts if len(c.strip()) >= 20][:60]

    text_lower = text_with_lines.lower()
    has_id_kw = bool(ID_KEYWORDS.search(text_lower))
    has_en_kw = bool(EN_KEYWORDS.search(text_lower))

    if not chunks:
        if has_id_kw and has_en_kw:
            return "MIX", 0.5
        elif has_id_kw:
            return "ID", 1.0
        return "EN", 0.0

    langs = []
    for c in chunks:
        try:
            langs.append(detect(c))
        except LangDetectException:
            continue

    if not langs:
        if has_id_kw and has_en_kw:
            return "MIX", 0.5
        elif has_id_kw:
            return "ID", 1.0
        return "EN", 0.0

    total = len(langs)
    id_count = sum(1 for l in langs if l == "id")
    en_count = sum(1 for l in langs if l == "en")

    id_ratio = id_count / total
    en_ratio = en_count / total

    # Logika Klasifikasi Pemilahan Bahasa (Penyempurnaan MIX)
    # 1. Rasio campuran kalimat berada pada rentang 15% - 75%
    if 0.15 <= id_ratio <= 0.75:
        label = "MIX"
    # 2. Kalimat dominan EN, tetapi terdapat struktur pengantar/administrasi Bahasa Indonesia
    elif en_ratio > 0.75 and has_id_kw:
        label = "MIX"
    # 3. Kalimat dominan ID, tetapi terdapat section header / requirement Bahasa Inggris
    elif id_ratio > 0.75 and has_en_kw:
        label = "MIX"
    # 4. Murni dominan Bahasa Indonesia
    elif id_ratio > 0.75:
        label = "ID"
    # 5. Murni Bahasa Inggris
    else:
        label = "EN"

    return label, round(id_ratio, 3)


ID_PLACES = ["indonesia", "jakarta", "bandung", "surabaya", "yogyakarta", "semarang",
             "medan", "bali", "denpasar", "tangerang", "bekasi", "depok", "bogor",
             "malang", "batam", "makassar", "palembang", "solo", "jawa", "sumatera",
             "kalimantan", "sulawesi", "banten", "daerah khusus", "kabupaten", "kota "]


def looks_indonesian(location):
    loc = str(location or "").lower()
    return any(k in loc for k in ID_PLACES)


def clean_location(loc):
    """'Jakarta, DKI Jakarta • melalui LinkedIn' -> 'Jakarta, DKI Jakarta'."""
    return re.split(r"\s*•\s*", str(loc or ""))[0].strip()


def pick(d, *keys):
    for k in keys:
        v = d.get(k)
        if v:
            return v
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-chars", type=int, default=300)
    ap.add_argument("--country", default="ID",
                    help="simpan hanya negara ini (kosongkan untuk semua); "
                         "baris tanpa info negara tetap disimpan")
    ap.add_argument("--indonesia-only", action="store_true",
                    help="buang lowongan yang negaranya bukan ID DAN lokasinya tidak "
                         "mengandung nama tempat Indonesia")
    args = ap.parse_args()

    if not RAW_FILE.exists():
        raise SystemExit(f"{RAW_FILE} tidak ditemukan. Jalankan collect_jobs.py dulu.")

    rows, seen_ids, seen_sigs = [], set(), set()
    dropped = Counter()

    with open(RAW_FILE, encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                dropped["json_rusak"] += 1
                continue
            d = rec.get("raw") or {}
            jid = rec["job_id"]
            if jid in seen_ids:
                dropped["id_duplikat"] += 1
                continue

            country = (d.get("job_country") or "").upper()
            if args.country and country and country != args.country.upper():
                dropped["negara_lain"] += 1
                continue

            if args.indonesia_only and country != "ID" and not looks_indonesian(
                    pick(d, "job_location", "location")):
                dropped["bukan_indonesia"] += 1
                continue

            title = str(pick(d, "job_title")).strip()
            company = d.get("employer_name") or ""
            if not company and isinstance(d.get("company"), dict):
                company = d["company"].get("name", "")
            flat, with_lines = clean_text(pick(d, "job_description", "description"))

            if len(flat) < args.min_chars:
                dropped["terlalu_pendek"] += 1
                continue

            sig1 = (title.lower(), str(company).lower())
            sig2 = hashlib.md5(flat[:500].lower().encode("utf-8")).hexdigest()
            if sig1 in seen_sigs or sig2 in seen_sigs:
                dropped["isi_duplikat"] += 1
                continue

            seen_ids.add(jid)
            seen_sigs.update([sig1, sig2])

            lang, id_ratio = detect_language(with_lines)
            rows.append({
                "job_id": jid,
                "job_title": title,
                "company": company,
                "location": clean_location(pick(d, "job_location", "location")),
                "country": country,
                "job_type": pick(d, "job_employment_type", "job_type"),
                "posted_at": pick(d, "job_posted_at_datetime_utc", "creation_date"),
                "description": flat,
                "role_group": rec["role_group"],
                "source": d.get("job_publisher") or "JSearch",
                "language": lang,
                "id_ratio": id_ratio,
                "url": pick(d, "job_apply_link", "indeed_final_url"),
            })

    OUT_FILE.parent.mkdir(exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)

    print(f"Korpus bersih: {len(rows)} lowongan -> {OUT_FILE}")
    print("Dibuang:", dict(dropped))
    print("Per peran:", dict(Counter(r["role_group"] for r in rows)))
    print("Per bahasa:", dict(Counter(r["language"] for r in rows)))
    print("Per negara:", dict(Counter(r["country"] or "?" for r in rows)))


if __name__ == "__main__":
    main()