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
    user_email = "test@example.com"  # TODO: Extract email from task
    subprocess.run(["python3", script_url, user_email], check=True)
    return "Data generated successfully."

def format_file_with_prettier(task):
    """Formats Markdown files using Prettier."""
    filepath = os.path.join(DATA_DIR, "format.md")
    subprocess.run(["npx", "prettier", "--write", filepath], check=True)
    return "Formatted successfully."

def count_specific_weekday(task):
    """Counts occurrences of a specific weekday from a date file."""
    input_file = os.path.join(DATA_DIR, "dates.txt")
    output_file = os.path.join(DATA_DIR, "dates-wednesdays.txt")
    
    count = count_weekdays(input_file, "Wednesday")
    with open(output_file, "w") as f:
        f.write(str(count))
    
    return f"Counted {count} Wednesdays."

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
