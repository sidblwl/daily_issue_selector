
from datetime import datetime, timedelta

# Dummy donor email interaction history
donor_history = [
    {"date": datetime.now() - timedelta(weeks=1), "action": "clicked", "cta": "petition"},
    {"date": datetime.now() - timedelta(weeks=3), "action": "donated", "cta": "donation"},
    {"date": datetime.now() - timedelta(weeks=5), "action": "ignored", "cta": "informational"},
    {"date": datetime.now() - timedelta(weeks=6), "action": "clicked", "cta": "volunteer"},
    {"date": datetime.now() - timedelta(weeks=8), "action": "ignored", "cta": "petition"},
]

# Action scores
action_scores = {
    "clicked": 1,
    "clicked_multiple": 2,  # example, not used here
    "donated": 5,
    "ignored": -1,
    "opened_no_click": 0,
}

# CTA weights
cta_weights = {
    "informational": 1.0,
    "petition": 1.5,
    "volunteer": 2.0,
    "donation": 2.5
}

# Exponential decay factor
def decay(weeks):
    return (0.9) ** weeks

# Calculate score
def calculate_score(donor_history):
    total_score = 0
    for email in donor_history:
        weeks_ago = (datetime.now() - email["date"]).days // 7
        a_ul = action_scores[email["action"]]
        w_i = cta_weights[email["cta"]]
        k_i = weeks_ago
        score = a_ul * w_i * decay(k_i)
        total_score += score
    return total_score

score = calculate_score(donor_history)
print(f"Donor interest score: {score:.2f}")

if score > 5:
    print("Super Interested")
elif score > 2:
    print("Interested")
elif score < 0:
    print("Disinterested")
else:
    print("Neutral")
