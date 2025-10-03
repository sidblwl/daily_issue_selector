import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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


# Example usage:
if __name__ == "__main__":
    test_message = "We need to fix the rising cost of rent and address the housing crisis affecting families in our city."
    result = tag_message(test_message)
    print(result)
