import os
import json
import csv
import time
from openai import OpenAI
from dotenv import load_dotenv

# Load API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Category list from your existing script
CATEGORIES = """
🌍 Issue: Climate Change
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

# Add your 25 messages here
messages = [
    "Hey , it's Tim Walz – Governor of Minnesota, former Chair of the Democratic Governors Association, and former VP candidate. As of yesterday, Donald Trump has officially taken office as president – with the backing of a GOP trifecta and a Supreme Court packed with extremist judges. Make no mistake: 𝗪𝗲 𝗵𝗮𝘃𝗲 𝗮 𝗱𝗶𝗳𝗳𝗶𝗰𝘂𝗹𝘁 𝗿𝗼𝗮𝗱 𝗮𝗵𝗲𝗮𝗱 𝗼𝗳 𝘂𝘀...",
    "🚨 Barack Obama Alert for  🚨 Did you hear what former President Barack Obama had to say about this election?! \"𝐓𝐡𝐞 𝐨𝐮𝐭𝐜𝐨𝐦𝐞 𝐨𝐟 𝐭𝐡𝐞 𝐞𝐥𝐞𝐜𝐭𝐢𝐨𝐧 𝐢𝐧 𝐍𝐨𝐯𝐞𝐦𝐛𝐞𝐫 𝐰𝐢𝐥𝐥 𝐝𝐞𝐭𝐞𝐫𝐦𝐢𝐧𝐞 𝐀𝐦𝐞𝐫𝐢𝐜𝐚'𝐬 𝐟𝐮𝐭𝐮𝐫𝐞 𝐟𝐨𝐫 𝐠𝐞𝐧𝐞𝐫𝐚𝐭𝐢𝐨𝐧𝐬 𝐭𝐨 𝐜𝐨𝐦𝐞.\"",
    "We've asked at least 3 times this month to confirm your party status! We've asked at least 10 times if you endorse Kamala Harris! Now, we're asking for at least the 4th time: Are you planning to vote this November?",
    "Dr. Mary Trump here, niece of Donald J. Trump. 𝐓𝐡𝐞𝐫𝐞 𝐚𝐫𝐞 𝐨𝐧𝐥𝐲 𝟐𝟎 𝐝𝐚𝐲𝐬 𝐮𝐧𝐭𝐢𝐥 𝐄𝐥𝐞𝐜𝐭𝐢𝐨𝐧 𝐃𝐚𝐲...",
    "We're not texting to ask for money – we just need your input. With just 3 DAYS until Election Day, we're asking you again: Have you already voted in the 2024 elections?",
    "While the end result wasn't what we wanted, Kamala Harris ran a historic and monumental campaign for president. So right now, we're asking 50,000 Democrats to sign on and thank her for her leadership.",
    "🗳️ 𝗗𝗚𝗔 𝗘𝗫𝗜𝗧 𝗣𝗢𝗟𝗟 🗳️ , polls have officially closed across the country. So now, we’re surveying our top supporters for our internal exit poll...",
    "We're not texting to ask for money - we just need your input. With exactly 11 days left until Election Day, we want to know: Have you already voted in the 2024 elections?",
    ", have you voted yet?? Over 28 MILLION ballots have already been cast – was yours one of them?",
    "we need your help. We're combing through the data after the 2024 election to help us prepare for future campaigns. We need you to update your record ASAP. Please confirm: Did you vote for Kamala Harris?",
    "Barack Obama. Michelle Obama. Bill Clinton. Wes Moore. Gavin Newsom. Gretchen Whitmer. And SO many more Dems are hitting the road to support Kamala Harris!",
    "We've asked at least 3 times this month to confirm your party status! We've asked at least 10 times if you endorse Kamala Harris! Now, we're asking for at least the 4th time: Are you planning to vote this November?",
    "We're not texting to ask for money – we just need your input. With just 3 DAYS until Election Day, we're asking you again: Have you already voted in the 2024 elections?",
    "is there ANYTHING we can say to get you to confirm your 2024 vote?? We NEED to hear from our top supporters. Confirm now: Are you voting for Kamala?",
    "after weeks of neck-and-neck polling, Kamala Harris is UP in key swing states! Now we need to hear from you. Please, respond to this urgent live poll before midnight...",
    "Are you ignoring us, ?! Kamala Harris AND Tim Walz called on top Democrats like you at least THREE TIMES!",
    "polls have officially closed across the country. So now, we’re surveying our top supporters for our internal exit poll...",
    "𝐊𝐚𝐦𝐚𝐥𝐚 𝐇𝐚𝐫𝐫𝐢𝐬 called on top Democrats like you. 𝐓𝐢𝐦 𝐖𝐚𝐥𝐳 called on top Democrats like you. 𝐃𝐨𝐮𝐠 𝐄𝐦𝐡𝐨𝐟𝐟 called on top Democrats like you...",
    "after weeks of neck-and-neck polling, Kamala Harris is UP in key swing states! Now we need to hear from you. Please, respond to this urgent live poll before midnight...",
    "We're not texting to ask for money – we just need your input. With just 3 DAYS until Election Day, we're asking you again: Have you already voted in the 2024 elections?"
]

# Tagging function
def tag_message(message):
    prompt = f"""You are an issue classification assistant for progressive campaigns. Based on the categories below, classify the following message and rate each issue from 1 (not relevant) to 5 (highly relevant). Only respond in JSON.

Categories:
{CATEGORIES}

Message:
\"\"\"{message}\"\"\"

Respond with JSON in this format:
{{
  "Climate Change": 3,
  "Healthcare Access": 1,
  ...
}}
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You classify campaign messages into issue relevance scores."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    return response.choices[0].message.content


# Main batch tagging
results = []
for i, msg in enumerate(messages, 1):
    print(f"Tagging message {i}/{len(messages)}...")
    try:
        raw_response = tag_message(msg)
        scores = json.loads(raw_response)
        scores["Message"] = msg
        results.append(scores)
        time.sleep(1)  # Optional: avoids hitting rate limits
    except Exception as e:
        print(f"❌ Error tagging message {i}: {e}")
        continue

# Save results to CSV
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
