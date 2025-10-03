# Auto-generated script to tag campaign messages
import os
import json
import csv
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CATEGORIES = """🌍 Issue: Climate Change
Description: Mitigate and adapt to environmental changes
Local Examples: Rainfall, heatwaves, flood zones, wildfire risk

🏥 Issue: Healthcare Access
Description: Expand affordable care, especially rural and mental health
Local Examples: Hospital closures, uninsured rates, wait times

⚖️ Issue: Reproductive Rights
Description: Protect abortion and reproductive care
Local Examples: Distance to provider, state-level bans, clinic closures

🏫 Issue: Public Education
Description: Fund schools and improve equity
Local Examples: Per-pupil funding, teacher shortages, test score disparities

🔫 Issue: Gun Safety
Description: Enact common-sense reforms
Local Examples: Local shootings, youth gun deaths, red flag law failures

🗳️ Issue: Voting Rights
Description: Oppose voter suppression
Local Examples: Poll closures, voter ID laws, wait times to vote

🚔 Issue: Criminal Justice Reform
Description: End mass incarceration, address police abuse
Local Examples: Jail population stats, policing by race

🌐 Issue: Immigration
Description: Ensure humane, fair immigration policy
Local Examples: ICE raids, asylum backlogs, DACA recipients in state

💼 Issue: Jobs & Wages
Description: Raise minimum wage, support unions
Local Examples: Local minimum wage, union drives, unemployment

🏘️ Issue: Affordable Housing
Description: Address rent inflation and homelessness
Local Examples: Median rent increases, eviction filings

🛠️ Issue: Infrastructure
Description: Invest in roads, transit, water, broadband
Local Examples: Unsafe bridges, delayed transit, broadband deserts

🏳️‍🌈 Issue: LGBTQ+ Rights
Description: Protect civil rights and access to care
Local Examples: Anti-LGBTQ bills, hate crime rates, youth care bans

👶 Issue: Childcare & Paid Leave
Description: Lower costs and support working families
Local Examples: Cost of childcare, paid leave access, provider shortages

✊🏾 Issue: Racial Equity
Description: Close systemic gaps
Local Examples: Homeownership by race, maternal mortality rates

💰 Issue: Tax Fairness
Description: Make tax code progressive
Local Examples: % using EITC, billionaire subsidies, tax loopholes

🌾 Issue: Rural Investment
Description: Support underserved rural areas
Local Examples: Broadband access, federal dollars per capita

🔋 Issue: Clean Energy
Description: Accelerate renewable transition
Local Examples: Solar/wind jobs, emissions levels, grid resilience

🏪 Issue: Small Business Support
Description: Revitalize local economies
Local Examples: SBA loans, vacancy rates, closures post-COVID

♿ Issue: Disability Rights
Description: Expand access and inclusion
Local Examples: ADA violations, special ed funding, waitlists

🪖 Issue: National Security
Description: Strengthen democratic alliances
Local Examples: Military base closures, veteran benefits funding

🚨 Issue: Urgency/End of Quarter
"""

messages = [
    "Hey , it's Tim Walz \u2013 Governor of Minnesota...",
    "\ud83d\udea8 Barack Obama Alert for  \ud83d\udea8 Did you hear what former President Barack Obama had to say...",
    "We've asked at least 3 times this month to confirm your party status...",
    "Dr. Mary Trump here, niece of Donald J. Trump. \ud835\udc13\ud835\udc21\ud835\udc1e\ud835\udc2b\ud835\udc1e \ud835\udc1a\ud835\udc2b\ud835\udc1e \ud835\udc28\ud835\udc27\ud835\udc25\ud835\udc32 \ud835\udfd0\ud835\udfce \ud835\udc1d\ud835\udc1a\ud835\udc32\ud835\udc2c...",
    "We're not texting to ask for money \u2013 we just need your input. With just 3 DAYS until Election Day...",
    "While the end result wasn't what we wanted, Kamala Harris ran a historic and monumental campaign...",
    "\ud83d\uddf3\ufe0f \ud835\uddd7\ud835\uddda\ud835\uddd4 \ud835\uddd8\ud835\uddeb\ud835\udddc\ud835\udde7 \ud835\udde3\ud835\udde2\ud835\udddf\ud835\udddf \ud83d\uddf3\ufe0f , polls have officially closed...",
    "We're not texting to ask for money - we just need your input. With exactly 11 days left...",
    ", have you voted yet?? Over 28 MILLION ballots have already been cast...",
    "we need your help. We're combing through the data after the 2024 election...",
    "Barack Obama. Michelle Obama. Bill Clinton. Wes Moore...",
    "We've asked at least 3 times this month to confirm your party status!",
    "We're not texting to ask for money \u2013 we just need your input. With just 3 DAYS...",
    "is there ANYTHING we can say to get you to confirm your 2024 vote??",
    "after weeks of neck-and-neck polling, Kamala Harris is UP in key swing states...",
    "Are you ignoring us, ?! Kamala Harris AND Tim Walz called on top Democrats...",
    "polls have officially closed across the country. So now, we\u2019re surveying...",
    "\ud835\udc0a\ud835\udc1a\ud835\udc26\ud835\udc1a\ud835\udc25\ud835\udc1a \ud835\udc07\ud835\udc1a\ud835\udc2b\ud835\udc2b\ud835\udc22\ud835\udc2c called on top Democrats like you...",
    "after weeks of neck-and-neck polling, Kamala Harris is UP...",
    "We're not texting to ask for money \u2013 we just need your input. With just 3 DAYS..."
]


def tag_message(message):
    prompt = f"""You are an issue classification assistant for progressive campaigns. Based on the categories below, classify the following message and rate each issue from 1 (not relevant) to 5 (highly relevant). Only respond in JSON.

Categories:
{CATEGORIES}

Message:
"""{message}"""

Respond with ONLY valid JSON. Do not add any explanations or text before or after.
Return your response in this format:
{{
  "Climate Change": 3,
  "Healthcare Access": 1,
  ...
}}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You classify campaign messages into issue relevance scores. Only respond in valid JSON. No explanations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        raw = response.choices[0].message.content.strip()
        print("🟡 RAW RESPONSE:")
        print(raw)

        parsed = json.loads(raw)
        return parsed

    except json.JSONDecodeError as e:
        print(f"❌ JSON decoding error: {e}")
        print(f"⚠️ Raw output was:\n{repr(raw)}")
        return None
    except Exception as e:
        print(f"❌ OpenAI request failed: {e}")
        return None

results = []
for i, msg in enumerate(messages, 1):
    print(f"\n🔄 Tagging message {i}/{len(messages)}...")
    scores = tag_message(msg)
    if scores:
        scores["Message"] = msg
        results.append(scores)
    else:
        print(f"⚠️ Skipping message {i} due to error.")
    time.sleep(1)

if results:
    all_keys = list(results[0].keys())
    issue_keys = [k for k in all_keys if k != "Message"]
    fieldnames = ["Message"] + issue_keys

    with open("tagged_messages.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print("✅ Done! Saved results to 'tagged_messages.csv'")
else:
    print("⚠️ No results to save.")
