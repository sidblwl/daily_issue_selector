# scripts/send_daily.py
import sys
import os
import smtplib
import ssl
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

# --- Load .env from repo root or src/.env ---
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
env_path_root = os.path.join(repo_root, ".env")
env_path_src = os.path.join(repo_root, "src", ".env")

if os.path.exists(env_path_root):
    load_dotenv(env_path_root)
elif os.path.exists(env_path_src):
    load_dotenv(env_path_src)
else:
    load_dotenv()  # fallback: current directory

# Make src/ importable
sys.path.append(os.path.join(repo_root, "src"))

from news_api import fetch_trending_articles
from issue_selector import filter_articles
from llm_generator import generate_llm_output


def _choose_story_with_email(articles):
    """
    For each filtered article, ask the LLM for fundraising output.
    Pick the first one that parses cleanly.
    Returns (article, llm_result) or (None, None).
    """
    fallbacks = []
    for art in articles:
        llm = generate_llm_output(art)
        if isinstance(llm, dict) and "error" not in llm and llm.get("email"):
            return art, llm
        fallbacks.append((art, llm))

    if fallbacks:
        for art, llm in fallbacks:
            if isinstance(llm, dict) and llm.get("email"):
                return art, llm
        return fallbacks[0]

    return None, None


def _build_email_parts(article, llm_result):
    """
    Create subject, plaintext, and HTML bodies for the one-story daily email.
    """
    run_date = date.today()
    title = article.get("title", "(untitled)")
    url = article.get("url", "")
    source = article.get("source_id", "")
    issue_from_article = article.get("issue") or "unknown"
    issue_from_llm = llm_result.get("issue") or issue_from_article
    local_stat = llm_result.get("local_stat") or ""
    donor_email = llm_result.get("email") or ""

    subject = f"Daily Pick — {issue_from_llm.title()}: {title}"

    # Plaintext
    text = (
        f"Daily News Pick — {run_date:%Y-%m-%d}\n\n"
        f"Title: {title}\n"
        f"Issue: {issue_from_llm}\n"
        f"Source: {source}\n"
        f"Link: {url}\n\n"
        f"Local impact:\n{local_stat}\n\n"
        f"Fundraising email draft:\n\n{donor_email}\n"
    )

    # Simple HTML
    html = f"""
    <div style="font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;line-height:1.5;">
      <h2 style="margin:0 0 12px 0;">Daily News Pick — {run_date:%A, %B %d, %Y}</h2>
      <h3 style="margin:0 0 6px 0;">{title}</h3>
      <div style="color:#666;margin-bottom:8px;">
        Issue: <strong>{issue_from_llm}</strong> &nbsp;•&nbsp; Source: <strong>{source}</strong>
      </div>
      <div style="margin:6px 0 14px 0;">
        <a href="{url}">{url}</a>
      </div>
      <div style="margin:14px 0;">
        <div style="font-weight:600;margin-bottom:4px;">Local impact</div>
        <div>{local_stat}</div>
      </div>
      <hr style="border:none;border-top:1px solid #e5e7eb;margin:16px 0;">
      <div style="font-weight:600;margin-bottom:6px;">Fundraising email draft</div>
      <div style="white-space:pre-wrap;">{donor_email}</div>
      <div style="color:#777;margin-top:16px;font-size:12px;">
        Sent automatically by the daily selector script.
      </div>
    </div>
    """
    return subject, text, html


def _send_email(subject, text_body, html_body):
    """
    Send a multipart/alternative email using SMTP env vars.
    Works with SendGrid or any SMTP provider.
    """
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    sender = os.getenv("EMAIL_SENDER")
    recipient = os.getenv("EMAIL_RECIPIENT")
    cc = [e.strip() for e in os.getenv("EMAIL_CC", "").split(",") if e.strip()]
    bcc = [e.strip() for e in os.getenv("EMAIL_BCC", "").split(",") if e.strip()]

    missing = [k for k, v in {
        "SMTP_HOST": smtp_host, "SMTP_USER": smtp_user, "SMTP_PASS": smtp_pass,
        "EMAIL_SENDER": sender, "EMAIL_RECIPIENT": recipient
    }.items() if not v]
    if missing:
        raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")

    msg = MIMEMultipart("alternative")
    msg["From"] = sender
    msg["To"] = recipient
    if cc:
        msg["Cc"] = ", ".join(cc)
    msg["Subject"] = subject

    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    to_addrs = [recipient] + cc + bcc

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
        server.starttls(context=context)
        server.login(smtp_user, smtp_pass)
        server.sendmail(sender, to_addrs, msg.as_string())


def _collect_up_to_four():
    """
    Fetch up to 4 relevant articles (like run_selector.py).
    """
    filtered_articles = []
    seen_content = set()
    iteration_count = 0
    max_iterations = 4

    while len(filtered_articles) < 4 and iteration_count < max_iterations:
        data = fetch_trending_articles()
        articles = data.get("results", [])
        iteration_count += 1

        if not articles:
            break

        new_filtered = filter_articles(articles)
        for article in new_filtered:
            if len(filtered_articles) >= 4:
                break
            title = article.get('title') or ''
            desc = article.get('description') or ''
            key = (title.lower(), (desc or '').lower())
            if key not in seen_content:
                filtered_articles.append(article)
                seen_content.add(key)

    return filtered_articles


def main():
    articles = _collect_up_to_four()
    if not articles:
        print("⛔ No relevant articles found today; not sending an email.")
        return 2

    article, llm = _choose_story_with_email(articles)
    if not article or not isinstance(llm, dict) or not llm.get("email"):
        print("⛔ Could not generate a usable fundraising email; not sending.")
        return 3

    subject, text_body, html_body = _build_email_parts(article, llm)

    try:
        _send_email(subject, text_body, html_body)
        print(f"✅ Sent daily pick: {subject}")
        return 0
    except Exception as e:
        print(f"🛑 Email send failed: {e}")
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
