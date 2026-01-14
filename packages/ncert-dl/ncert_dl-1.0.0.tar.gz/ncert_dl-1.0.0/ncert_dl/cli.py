#!/usr/bin/env python3
import requests
import time
import hashlib
import argparse
from pathlib import Path
from tqdm import tqdm

# ================= CONFIG =================
BASE_URL = "https://ncert.nic.in/textbook/pdf/"
HEADERS = {"User-Agent": "Mozilla/5.0"}
DELAY = 1.5
RETRIES = 3

# ================= CHAPTER NAMES =================
# Only Class 10 fully filled (authoritative)
CHAPTER_NAMES = {
    10: {
        "Mathematics": {
            1: "Real Numbers",
            2: "Polynomials",
            3: "Pair of Linear Equations in Two Variables",
            4: "Quadratic Equations",
            5: "Arithmetic Progressions",
            6: "Triangles",
            7: "Coordinate Geometry",
            8: "Introduction to Trigonometry",
            9: "Some Applications of Trigonometry",
            10: "Circles",
            11: "Constructions",
            12: "Areas Related to Circles",
            13: "Surface Areas and Volumes",
            14: "Statistics",
        },
        "Science": {
            1: "Chemical Reactions and Equations",
            2: "Acids, Bases and Salts",
            3: "Metals and Non-metals",
            4: "Carbon and its Compounds",
            5: "Life Processes",
            6: "Control and Coordination",
            7: "How do Organisms Reproduce",
            8: "Heredity and Evolution",
            9: "Light – Reflection and Refraction",
            10: "The Human Eye and the Colourful World",
            11: "Electricity",
            12: "Magnetic Effects of Electric Current",
            13: "Our Environment",
            14: "Sources of Energy",
            15: "Management of Natural Resources",
            16: "Water Resources",
        },
        "SST": {
            "History": {
                1: "The Rise of Nationalism in Europe",
                2: "Nationalism in India",
                3: "The Making of a Global World",
                4: "The Age of Industrialisation",
                5: "Print Culture and the Modern World",
            },
            "Geography": {
                1: "Resources and Development",
                2: "Forest and Wildlife Resources",
                3: "Water Resources",
                4: "Agriculture",
                5: "Minerals and Energy Resources",
                6: "Manufacturing Industries",
                7: "Lifelines of National Economy",
            },
            "Political_Science": {
                1: "Power Sharing",
                2: "Federalism",
                3: "Gender, Religion and Caste",
                4: "Political Parties",
                5: "Outcomes of Democracy",
                6: "Challenges to Democracy",
                7: "Democracy and Diversity",
                8: "Popular Struggles and Movements",
            },
            "Economics": {
                1: "Development",
                2: "Sectors of the Indian Economy",
                3: "Money and Credit",
                4: "Globalisation and the Indian Economy",
                5: "Consumer Rights",
            },
        }
    }
}

# ================= SYLLABUS STRUCTURE =================
CLASSES = {
    10: {
        "Mathematics": ("jemh1", 14),
        "Science": ("jesc1", 16),
        "SST": {
            "History": (1, 5),
            "Geography": (2, 7),
            "Political_Science": (3, 8),
            "Economics": (4, 5),
        }
    },
    # 6–9, 11–12 can be added progressively
}

# ================= HELPERS =================
def safe_name(text):
    return text.replace(" ", "_").replace("–", "-")

def is_valid_pdf(url):
    try:
        r = requests.get(url, headers=HEADERS, stream=True, timeout=15)
        ok = r.status_code == 200 and "application/pdf" in r.headers.get("Content-Type", "")
        r.close()
        return ok
    except Exception:
        return False

def download(url, dest):
    for attempt in range(RETRIES):
        try:
            with requests.get(url, headers=HEADERS, stream=True, timeout=30) as r:
                if "application/pdf" not in r.headers.get("Content-Type", ""):
                    raise RuntimeError
                total = int(r.headers.get("Content-Length", 0))
                with open(dest, "wb") as f, tqdm(
                    total=total,
                    unit="B",
                    unit_scale=True,
                    desc=dest.name,
                    leave=False,
                ) as bar:
                    for chunk in r.iter_content(8192):
                        if chunk:
                            f.write(chunk)
                            bar.update(len(chunk))
            return True
        except Exception:
            time.sleep(2 ** attempt)
    return False

def try_medium(filename):
    for lang in ("e", "h"):
        if filename.startswith("je"):
            candidate = "j" + lang + filename[2:]
        else:
            candidate = filename
        if is_valid_pdf(BASE_URL + candidate):
            return candidate
        time.sleep(0.5)
    return None

# ================= MAIN =================
def main():
    parser = argparse.ArgumentParser(description="NCERT textbook downloader (Class 6–12)")
    parser.add_argument("cls", type=int, help="Class number (6–12)")
    parser.add_argument("--out", default="NCERT", help="Output directory")
    args = parser.parse_args()

    if args.cls not in CLASSES:
        print("Class not yet fully mapped. Contributions welcome.")
        return

    root = Path(args.out) / f"Class_{args.cls}"
    root.mkdir(parents=True, exist_ok=True)

    print(f"\n📚 NCERT Class {args.cls}\n")

    # Maths / Science
    for subject, data in CLASSES[args.cls].items():
        if subject == "SST":
            continue

        prefix, chapters = data
        subj_dir = root / subject
        subj_dir.mkdir(exist_ok=True)

        for ch in range(1, chapters + 1):
            base = f"{prefix}{str(ch).zfill(2)}.pdf"
            fname = try_medium(base)
            if not fname:
                continue

            chapter_name = CHAPTER_NAMES[args.cls][subject][ch]
            new_name = f"{str(ch).zfill(2)}_{safe_name(chapter_name)}.pdf"
            dest = subj_dir / new_name

            if dest.exists():
                continue

            download(BASE_URL + fname, dest)
            time.sleep(DELAY)

    # SST
    sst_root = root / "Social_Science"
    sst_root.mkdir(exist_ok=True)

    for subject, (code, chapters) in CLASSES[args.cls]["SST"].items():
        subj_dir = sst_root / subject
        subj_dir.mkdir(exist_ok=True)

        for ch in range(1, chapters + 1):
            base = f"jess{code}0{ch}.pdf"
            fname = try_medium(base)
            if not fname:
                continue

            chapter_name = CHAPTER_NAMES[args.cls]["SST"][subject][ch]
            new_name = f"{str(ch).zfill(2)}_{safe_name(chapter_name)}.pdf"
            dest = subj_dir / new_name

            if dest.exists():
                continue

            download(BASE_URL + fname, dest)
            time.sleep(DELAY)

    print("\n✅ Done.")

if __name__ == "__main__":
    main()
