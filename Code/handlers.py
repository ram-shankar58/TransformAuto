import os
import subprocess
import json
import sqlite3
from datetime import datetime
from llm import query_llm
from utils import count_weekdays, extract_markdown_titles

DATA_DIR = "data"

def process_task(task):
    """
    Handles different automation tasks based on the given natural language description.
    """
    if "install uv" in task and "run" in task:
        return run_uv_and_generate_data(task)

    elif "format" in task and "prettier" in task:
        return format_file_with_prettier(task)

    elif "count the number of" in task:
        return count_specific_weekday(task)

    elif "sort contacts" in task:
        return sort_contacts_json()

    elif "recent log files" in task:
        return extract_recent_logs()

    elif "extract markdown titles" in task:
        return generate_markdown_index()

    elif "extract email sender" in task:
        return extract_email_sender()

    elif "extract credit card number" in task:
        return extract_credit_card_number()

    elif "find similar comments" in task:
        return find_similar_comments()

    elif "calculate total sales" in task:
        return calculate_ticket_sales()

    else:
        raise ValueError("Unknown task. Cannot process.")

def run_uv_and_generate_data(task):
    """Installs UV (if necessary) and runs the data generation script."""
    subprocess.run(["pip", "install", "--upgrade", "uv"], check=True)
    script_url = "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py"
    user_email = "23f1002296@ds.study.iitm.ac.in"  # TODO: Extract email from task
    subprocess.run(["python3", script_url, user_email], check=True)
    return "Data generated successfully."

def format_file_with_prettier(task):
    """Formats Markdown files using Prettier."""
    filepath = os.path.join(DATA_DIR, "format.md")
    subprocess.run(["npx", "prettier", "--write", filepath], check=True)
    return "Formatted successfully."

def count_specific_weekday(task):
    """Counts occurrences of a specific weekday from a date file."""
    date_file = os.path.join(DATA_DIR, "dates.txt")
    weekday = task.split()[-1]  # Extract weekday from task
    count = count_weekdays(date_file, weekday)
    return f"{weekday} occurs {count} times."

def sort_contacts_json():
    """Sorts contacts.json by last_name and first_name."""
    input_file = os.path.join(DATA_DIR, "contacts.json")
    output_file = os.path.join(DATA_DIR, "contacts-sorted.json")

    with open(input_file) as f:
        contacts = json.load(f)

    contacts.sort(key=lambda c: (c.get("last_name", ""), c.get("first_name", "")))

    with open(output_file, "w") as f:
        json.dump(contacts, f, indent=4)

    return "Contacts sorted successfully."

def extract_recent_logs():
    """Extracts recent log files."""
    log_dir = os.path.join(DATA_DIR, "logs")
    recent_logs = []
    for log_file in os.listdir(log_dir):
        if log_file.endswith(".log"):
            with open(os.path.join(log_dir, log_file)) as f:
                recent_logs.append(f.read())
    return "\n".join(recent_logs)

def generate_markdown_index():
    """Generates an index of Markdown titles."""
    markdown_dir = os.path.join(DATA_DIR, "docs")
    index = extract_markdown_titles(markdown_dir)
    return index

def extract_email_sender():
    """Extracts the sender from an email file."""
    email_file = os.path.join(DATA_DIR, "email.txt")
    with open(email_file) as f:
        for line in f:
            if line.startswith("From:"):
                return line.strip()
    return "Sender not found."

def extract_credit_card_number():
    """Extracts credit card number from an image."""
    image_file = os.path.join(DATA_DIR, "credit_card.png")
    # Assuming OCR is used to extract text from the image
    import pytesseract
    text = pytesseract.image_to_string(image_file)
    return text

def find_similar_comments():
    """Finds similar comments from a comments file."""
    comments_file = os.path.join(DATA_DIR, "comments.txt")
    with open(comments_file) as f:
        comments = f.readlines()
    similar_comments = query_llm(comments)
    return similar_comments

def calculate_ticket_sales():
    """Calculates total sales from an SQLite database."""
    db_path = os.path.join(DATA_DIR, "ticket-sales.db")
    output_file = os.path.join(DATA_DIR, "ticket-sales-gold.txt")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(units * price) FROM tickets WHERE type = 'Gold'")
    total_sales = cursor.fetchone()[0] or 0

    with open(output_file, "w") as f:
        f.write(str(total_sales))

    conn.close()
    return f"Total sales for Gold tickets: {total_sales}"