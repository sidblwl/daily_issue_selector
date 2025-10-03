import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def clean_json_response(raw):
    """
    Remove Markdown-style code blocks or formatting.
    """
    lines = raw.strip().splitlines()
    cleaned = []

    for line in lines:
        if line.strip().startswith("```"):
            continue  # skip code fences
        cleaned.append(line)

    return "\n".join(cleaned)

def generate_llm_output(article, location="Washington, DC"):
    title = article.get("title", "")
    source = article.get("source_id", "")
    full_text = article.get("full_text") or f"{title}\n\n{article.get('description', '')}"

    prompt = f"""
You are an expert political strategist helping a Democratic campaign.

Your job is to analyze national news articles and generate persuasive fundraising emails for donors. The emails must feel **locally relevant**, emotionally compelling, and must highlight contrasts with Republican inaction — especially Trump and the GOP.

Please complete these steps:

1. Identify the main national issue in the article. Use broad categories like:
   climate, healthcare, education, jobs, gun safety, immigration, inflation, technology, foreign policy, public safety.

2. Generate a single **locally relevant stat or impact sentence** about this issue in {location}. Make it sound specific and real, as if it came from a report, government source, or journalistic investigation. Be creative, but grounded. 
Turn this stat into a powerful, emotionally resonant message.
• Humanize it so it’s felt, not just understood.
• Apply the storytelling principles of Chip & Dan Heath’s Made to Stick (concrete anchors, vivid analogies), the surprising-reality framing of Hans Rosling’s Factfulness, and the visual, audience-first clarity of Cole Knaflic’s Storytelling with Data.
• Use analogies, real-world equivalents, and a brief narrative vignette that puts a face on the number.
• Make it sound like a standout line from a great political speech or nonprofit campaign.
• Audience: Describe the group — e.g., swing voters, working parents, major donors, policy-makers, etc...

3. Write a fundraising email encouraging support for Democrats. The tone should be urgent, emotional, and local. Make it sound real and tailored to DC residents. End with a call to donate. Follow this template, replace the rainfall issue with the issue in the article:
Rainfall has increased by 10 inches in your state over the last year.
That’s why I wasn’t surprised to read about the flooding disaster in your state this week:
”[Quote from local article]”
Meanwhile, my opponent voted against funding climate resilience for local communities.
I’m working to reverse that by fighting for [Policy X, Y, Z].
Will you chip in $[X] to help us take this fight to Congress?
P.S. If you haven’t read the article, it’s worth your time: [link]

Use this JSON format in your response (no markdown or code blocks):

{{
  "issue": "name of issue",
  "local_stat": "locally relevant stat or impact sentence",
  "email": "donor email message"
}}

ARTICLE FROM {source}:
{full_text}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.85
        )

        raw = response.choices[0].message.content.strip()
        cleaned = clean_json_response(raw)

        try:
            parsed = json.loads(cleaned)
            return parsed
        except json.JSONDecodeError:
            return {"error": "Could not parse response as JSON.", "raw": raw}

    except Exception as e:
        return {"error": str(e)}


# Describe statistics in more impactful formats/easier to understand for the human mind (instead of 90,000 describe it as 2 stadiums full of people, etc...)
# Look for a system prompt that can help with this (a prompt to humanize statistics/numbers)
# What is medicaid? Explain what they used to get and what they lose now. Explain what the impact is on the individual in household terms