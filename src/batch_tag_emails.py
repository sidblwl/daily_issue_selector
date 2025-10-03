#!/usr/bin/env python3
import os
import json
import csv
import time
import re
from typing import Dict, Any, List, Optional

from openai import OpenAI
from dotenv import load_dotenv

# ---------------------------
# Setup
# ---------------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Path to input JSON (same directory as this file)
JSON_FILE = os.path.join(os.path.dirname(__file__), "all_emails_full.json")
OUTPUT_CSV = os.path.join(os.path.dirname(__file__), "tagged_emails2.csv")

# Use a deterministic model
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# ---------------------------
# Categories (fixed key set)
# ---------------------------
ALLOWED_KEYS: List[str] = [
    "Climate Change",
    "Healthcare Access",
    "Reproductive Rights",
    "Public Education",
    "Gun Safety",
    "Voting Rights",
    "Criminal Justice Reform",
    "Immigration",
    "Jobs & Wages",
    "Affordable Housing",
    "Infrastructure",
    "LGBTQ+ Rights",
    "Childcare & Paid Leave",
    "Racial Equity",
    "Tax Fairness",
    "Rural Investment",
    "Clean Energy",
    "Small Business Support",
    "Disability Rights",
    "National Security",
    "Trump Overreach",
    "Beat Republicans",
    "Raffle/Opportunity",
    "Urgency/End of Quarter",
]

# Short category descriptions for the model (no emojis, no "Issue:" prefixes)
CATEGORIES_TEXT = """
Climate Change — Mitigate and adapt to environmental changes
Healthcare Access — Expand affordable care, especially rural and mental health
Reproductive Rights — Protect abortion and reproductive care
Public Education — Fund schools and improve equity
Gun Safety — Enact common-sense reforms
Voting Rights — Oppose voter suppression
Criminal Justice Reform — End mass incarceration, address police abuse
Immigration — Ensure humane, fair immigration policy
Jobs & Wages — Raise minimum wage, support unions
Affordable Housing — Address rent inflation and homelessness
Infrastructure — Invest in roads, transit, water, broadband
LGBTQ+ Rights — Protect civil rights and access to care
Childcare & Paid Leave — Lower costs and support working families
Racial Equity — Close systemic gaps
Tax Fairness — Make tax code progressive
Rural Investment — Support underserved rural areas
Clean Energy — Accelerate renewable transition
Small Business Support — Revitalize local economies
Disability Rights — Expand access and inclusion
National Security — Strengthen democratic alliances
Trump Overreach — Federal government going beyond allowed powers
Beat Republicans — Support Democrats or oppose GOP candidates
Raffle/Opportunity — Sweepstakes, meet-and-greet, or special donor opportunities
Urgency/End of Quarter — End-of-period urgency framing
""".strip()


# ---------------------------
# Prompt builder & normalizer
# ---------------------------
def build_prompt(email: Dict[str, Any]) -> str:
    rules = f"""
SCORING RULES (strict):
- Only return the following keys exactly (case and spacing must match): {ALLOWED_KEYS}.
- Do NOT add, remove, rename, or reorder keys. If a category is not relevant, set it to 0.
- 4–5 ONLY if the main call-to-action, purpose, or argument centers on that category.
- 1–2 for secondary/background mentions that support the main point but are not the focus.
- 0 if not mentioned or only indirectly implied.
- At most THREE categories may be ≥ 3.
- Use ONLY integers 0–5.
- Respond with ONLY valid JSON (no markdown fences, no commentary).

Example: An email mainly about voting in the midterms that briefly mentions healthcare:
"Voting Rights": 5, "Healthcare Access": 1.
""".strip()

    prompt = f"""
You are an issue classification assistant for progressive campaigns. Classify the MAIN topics of the email and rate each category from 0 (not relevant) to 5 (highly relevant). Return ONLY valid JSON.

CATEGORIES:
{CATEGORIES_TEXT}

EMAIL:
Subject: {email.get('subject','')}

{email.get('body','')}

{rules}

Return JSON in this exact shape (keys MUST match the list above), e.g.:
{{
  "Climate Change": 0,
  "Healthcare Access": 0,
  ...
}}
""".strip()
    return prompt


def normalize_scores(raw_dict: Dict[str, Any]) -> Dict[str, int]:
    """
    - Keep only allowed keys.
    - Coerce values to ints and clamp 0..5.
    - Enforce at most 3 categories >= 3 (demote extras to 2).
    """
    normalized: Dict[str, int] = {k: 0 for k in ALLOWED_KEYS}
    for k, v in list(raw_dict.items()):
        if k in ALLOWED_KEYS:
            try:
                iv = int(v)
            except Exception:
                iv = 0
            iv = max(0, min(5, iv))  # clamp
            normalized[k] = iv

    # Enforce ≤3 categories ≥3
    high_keys = sorted(
        [k for k, val in normalized.items() if val >= 3],
        key=lambda k: normalized[k],
        reverse=True,
    )
    if len(high_keys) > 3:
        for k in high_keys[3:]:
            normalized[k] = 2  # demote incidental to "background"

    return normalized


# ---------------------------
# Helpers
# ---------------------------
def extract_json(s: str) -> Optional[str]:
    """
    Extract JSON object from a string that may contain code fences or extra text.
    Finds the first '{' and the last '}' and returns that slice if valid.
    """
    if not s:
        return None

    # Strip typical code fences
    s = s.strip()
    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?", "", s, flags=re.IGNORECASE).strip()
        if s.endswith("```"):
            s = s[:-3].strip()

    # Try direct parse first
    try:
        json.loads(s)
        return s
    except Exception:
        pass

    # Fallback: slice from first '{' to last '}'
    start = s.find("{")
    end = s.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = s[start : end + 1]
        try:
            json.loads(candidate)
            return candidate
        except Exception:
            return None
    return None


def call_openai(prompt: str) -> str:
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You classify campaign emails into issue relevance scores. Only respond in valid JSON. No explanations.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )
    return resp.choices[0].message.content.strip()


# ---------------------------
# Core tagging
# ---------------------------
def tag_email(email: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    prompt = build_prompt(email)
    try:
        raw = call_openai(prompt)
        print("🟡 RAW RESPONSE:")
        print(raw)

        json_text = extract_json(raw)
        if not json_text:
            print("❌ Could not extract JSON from model output.")
            return None

        parsed = json.loads(json_text)

        # Remove any stray keys (like "Subject") before normalization
        scores_only = {k: v for k, v in parsed.items() if k in ALLOWED_KEYS}

        normalized = normalize_scores(scores_only)
        normalized["Subject"] = email.get("subject", "")
        return normalized

    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return None
    except Exception as e:
        print(f"❌ OpenAI request failed: {e}")
        return None


# ---------------------------
# Main
# ---------------------------
def main() -> None:
    # Load emails
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            emails = json.load(f)
            print(f"✅ Loaded {len(emails)} emails from {JSON_FILE}")
    except Exception as e:
        print(f"❌ Failed to load emails from file: {e}")
        return

    results: List[Dict[str, Any]] = []

    for i, email in enumerate(emails, 1):
        print(f"\n🔄 Tagging email {i}/{len(emails)}...")
        result = tag_email(email)
        if result:
            results.append(result)
        else:
            print(f"⚠️ Skipping email {i} due to error.")
        time.sleep(1)  # Gentle pacing; adjust if needed

    if not results:
        print("⚠️ No results to save.")
        return

    # Write CSV with fixed header
    fieldnames = ["Subject"] + ALLOWED_KEYS
    try:
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in results:
                writer.writerow({k: row.get(k, 0) for k in fieldnames})
        print(f"✅ Done! Saved results to '{OUTPUT_CSV}'")
    except Exception as e:
        print(f"❌ Failed to write CSV: {e}")


if __name__ == "__main__":
    main()
