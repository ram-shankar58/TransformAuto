import os
import json
import sqlite3
import requests
import subprocess
import datetime
import markdown2
import numpy as np
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
AIPROXY_TOKEN = os.getenv("eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIzZjEwMDIyOTZAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.EQkfHBbkPWnkr_vqh2skH55RP6f8ruAZeOBKSIElFk0")

# Initialize OpenAI client
client = OpenAI(api_key=AIPROXY_TOKEN)

# Ensure data directory exists
DATA_DIR = "/data"
os.makedirs(DATA_DIR, exist_ok=True)

app = Flask(__name__)

# Utility function to securely read a file
def read_file(filepath):
    if not filepath.startswith(DATA_DIR):
        return "Access denied", 403
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read(), 200
    except FileNotFoundError:
        return "", 404

# Utility function to execute shell commands
def run_shell_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip()

# Endpoint: Read file contents
@app.route("/read", methods=["GET"])
def read():
    path = request.args.get("path", "")
    content, status = read_file(path)
    return content, status

# Endpoint: Process tasks
@app.route("/run", methods=["POST"])
def run():
    task = request.args.get("task", "").strip().lower()

    try:
        if "install uv" in task and "run datagen.py" in task:
            return install_and_run_uv()
        elif "format" in task and "prettier" in task:
            return format_markdown()
        elif "count" in task and "wednesday" in task:
            return count_wednesdays()
        elif "sort contacts" in task:
            return sort_contacts()
        elif "extract first line" in task and "log files" in task:
            return extract_recent_logs()
        elif "extract h1 headings" in task:
            return extract_markdown_headers()
        elif "extract sender email" in task:
            return extract_sender_email()
        elif "extract credit card number" in task:
            return extract_credit_card()
        elif "find similar comments" in task:
            return find_similar_comments()
        elif "total sales for gold tickets" in task:
            return total_sales_gold()
        else:
            return jsonify({"error": "Task not recognized"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Task A1: Install `uv` and run `datagen.py`
def install_and_run_uv():
    run_shell_command("pip install uv")
    run_shell_command("uv venv .venv")
    url = "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py"
    script_path = os.path.join(DATA_DIR, "datagen.py")
    run_shell_command(f"curl -o {script_path} {url}")
    run_shell_command(f"python {script_path} {os.getenv('USER_EMAIL')}")
    return jsonify({"message": "uv installed and datagen.py executed"}), 200

# Task A2: Format Markdown file with Prettier
def format_markdown():
    file_path = f"{DATA_DIR}/format.md"
    run_shell_command(f"npx prettier@3.4.2 --write {file_path}")
    return jsonify({"message": "Markdown file formatted"}), 200

# Task A3: Count Wednesdays in dates file
def count_wednesdays():
    file_path = f"{DATA_DIR}/dates.txt"
    with open(file_path, "r") as f:
        dates = f.readlines()
    count = sum(1 for date in dates if datetime.datetime.strptime(date.strip(), "%Y-%m-%d").weekday() == 2)
    with open(f"{DATA_DIR}/dates-wednesdays.txt", "w") as f:
        f.write(str(count))
    return jsonify({"message": f"{count} Wednesdays counted"}), 200

# Task A4: Sort contacts by last & first name
def sort_contacts():
    file_path = f"{DATA_DIR}/contacts.json"
    with open(file_path, "r") as f:
        contacts = json.load(f)
    sorted_contacts = sorted(contacts, key=lambda x: (x["last_name"], x["first_name"]))
    with open(f"{DATA_DIR}/contacts-sorted.json", "w") as f:
        json.dump(sorted_contacts, f, indent=4)
    return jsonify({"message": "Contacts sorted"}), 200

# Task A5: Extract first lines of 10 most recent log files
def extract_recent_logs():
    log_dir = f"{DATA_DIR}/logs"
    log_files = sorted(
        [f for f in os.listdir(log_dir) if f.endswith(".log")],
        key=lambda x: os.path.getmtime(os.path.join(log_dir, x)),
        reverse=True,
    )[:10]
    first_lines = []
    for log in log_files:
        with open(os.path.join(log_dir, log), "r") as f:
            first_lines.append(f.readline().strip())
    with open(f"{DATA_DIR}/logs-recent.txt", "w") as f:
        f.write("\n".join(first_lines))
    return jsonify({"message": "Recent log lines extracted"}), 200

# Task A6: Extract H1 headings from Markdown files
def extract_markdown_headers():
    doc_dir = f"{DATA_DIR}/docs"
    index = {}
    for file in os.listdir(doc_dir):
        if file.endswith(".md"):
            with open(os.path.join(doc_dir, file), "r") as f:
                for line in f:
                    if line.startswith("# "):
                        index[file] = line[2:].strip()
                        break
    with open(f"{DATA_DIR}/docs/index.json", "w") as f:
        json.dump(index, f, indent=4)
    return jsonify({"message": "Markdown headers extracted"}), 200

# Task A7: Extract sender email using LLM
def extract_sender_email():
    with open(f"{DATA_DIR}/email.txt", "r") as f:
        email_content = f.read()
    response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": f"Extract the sender's email from:\n{email_content}"}])
    email_address = response["choices"][0]["message"]["content"]
    with open(f"{DATA_DIR}/email-sender.txt", "w") as f:
        f.write(email_address)
    return jsonify({"message": "Email extracted"}), 200

# Task A10: Compute total sales for "Gold" tickets
def total_sales_gold():
    conn = sqlite3.connect(f"{DATA_DIR}/ticket-sales.db")
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(units * price) FROM tickets WHERE type='Gold'")
    total_sales = cursor.fetchone()[0]
    with open(f"{DATA_DIR}/ticket-sales-gold.txt", "w") as f:
        f.write(str(total_sales))
    conn.close()
    return jsonify({"message": "Total sales computed"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
