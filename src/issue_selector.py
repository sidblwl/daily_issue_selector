import yaml

# Keywords that define each issue area
ISSUE_KEYWORDS = {
    "policies": [
        "national", "federal", "america", "american", "united states", "nationwide", "country",
        "administration", "congress", "senate", "house of representatives", "bill", "legislation",
        "executive order", "white house", "supreme court", "federal court", "department of justice",

        # Government roles
        "executive branch", "judicial branch", "legislative branch", "speaker of the house",
        "majority leader", "minority leader", "attorney general", "chief justice", "federal judge",
        "cabinet", "secretary of state",

        # Federal agencies
        "irs", "fbi", "cia", "nsa", "epa", "cdc", "dhs", "doj", "doe", "fda",
        "department of homeland security", "department of defense", "department of education",
        "state department", "homeland security", "veterans affairs",

        # Legal / court language
        "trial", "impeachment", "federal charges", "prosecution", "grand jury",
        "special counsel", "lawsuit", "appeals court", "ruling", "verdict", "subpoena",

        # Policy signals
        "national security", "domestic policy", "foreign policy", "public policy", "government program",
        "tax reform", "border security", "infrastructure bill", "defense spending", "education reform",
        "student loan forgiveness", "healthcare reform", "medicare", "gun reform",
        "energy policy", "climate bill", "immigration policy", "trade policy",

        # Existing issue keywords
        "climate", "wildfire", "hurricane", "carbon", "flood", "heat", "healthcare",
        "medicaid", "hospital", "insurance", "abortion", "school", "college", "student",
        "education", "tuition", "debt", "unemployment", "job", "labor", "wage",
        "hiring", "employment", "gun", "shooting", "violence", "firearm", "border",
        "immigration", "migrant", "asylum", "inflation", "cost of living", "price",
        "gas", "ai", "artificial intelligence", "tech", "social media", "privacy",
        "ukraine", "israel", "china", "nato", "war", "conflict", "crime", "police",
        "safety", "law enforcement",

        # Global/diplomatic
        "g7", "g20", "un", "united nations", "ambassador", "foreign relations", "state visit",
        "sanctions", "tariffs", "trade war", "arms deal", "military aid"
    ],
    "Trump": [
        "trump", "donald trump", "trump administration", "maga", "republican",
        "republican primary", "presidential election", "indictment",
        "mar-a-lago", "classified documents", "white house", "administration",
        "executive order", "presidential", "oval office", "cabinet"
    ]
}

REQUIRED_CONTEXT = [
    "national", "federal", "america", "american", "united states",
    "nationwide", "country", "administration"
]

CATEGORICAL_ISSUES = {
    "climate": ["climate", "wildfire", "hurricane", "carbon", "flood", "heat"],
    "healthcare": ["healthcare", "medicaid", "hospital", "insurance", "abortion"],
    "education": ["school", "college", "student", "education", "tuition", "debt"],
    "jobs": ["unemployment", "job", "labor", "wage", "hiring", "employment"],
    "gun safety": ["gun", "shooting", "violence", "firearm"],
    "immigration": ["border", "immigration", "migrant", "asylum"],
    "inflation": ["inflation", "cost of living", "price", "gas"],
    "technology": ["ai", "artificial intelligence", "tech", "social media", "privacy"],
    "foreign policy": ["ukraine", "israel", "china", "nato", "war", "conflict"],
    "public safety": ["crime", "police", "safety", "law enforcement"]
}

SHARED_KEYWORDS_REQUIRED = 1

def get_issue_label(article):
    title = article.get('title') or ''
    desc = article.get('description') or ''
    text = f"{title} {desc}".lower()

    for issue, keywords in CATEGORICAL_ISSUES.items():
        if any(keyword in text for keyword in keywords):
            return issue
    return None

def has_enough_overlap(title, desc):
    if not desc.strip():  # if description is empty, just use title
        return True
    title_words = set(title.lower().split())
    desc_words = set(desc.lower().split())
    shared = title_words & desc_words
    return len(shared) >= SHARED_KEYWORDS_REQUIRED

def filter_articles(articles):
    relevant_articles = []
    seen_content = set()

    print(f"\nFiltering {len(articles)} articles...")

    for article in articles:
        title = article.get('title') or ''
        desc = article.get('description') or ''
        text = f"{title} {desc}".lower()

        has_trump = any(keyword in text for keyword in ISSUE_KEYWORDS["Trump"])
        has_national_context = any(context in text for context in REQUIRED_CONTEXT)
        has_policy = any(keyword in text for keyword in ISSUE_KEYWORDS["policies"])
        overlap_ok = has_enough_overlap(title, desc)

        print(f"\nAnalyzing article: {title}")
        print(f"Has Trump keywords: {has_trump}")
        print(f"Has national context: {has_national_context}")
        print(f"Has policy keywords: {has_policy}")
        print(f"Title/desc keyword overlap sufficient: {overlap_ok}")

        if has_policy and has_trump and overlap_ok:
            content_key = (title.lower(), desc.lower())
            if content_key not in seen_content:
                issue = get_issue_label(article)
                article["issue"] = issue if issue else "unknown"
                relevant_articles.append(article)
                seen_content.add(content_key)
                print("✓ Article accepted")
            else:
                print("✗ Article rejected (duplicate)")
        else:
            print("✗ Article rejected (not relevant)")

    return relevant_articles
