import json
import re
from datetime import datetime

def count_weekdays(file_path, weekday):
    """Counts occurrences of a specific weekday in a date file."""
    count = 0
    with open(file_path) as f:
        for line in f:
            try:
                date_obj = datetime.strptime(line.strip(), "%Y-%m-%d")
                if date_obj.strftime("%A") == weekday:
                    count += 1
            except ValueError:
                continue
    return count

def extract_markdown_titles(directory):
    """Extracts H1 titles from Markdown files."""
    index = {}
    for filename in os.listdir(directory):
        if filename.endswith(".md"):
            with open(os.path.join(directory, filename)) as f:
                for line in f:
                    if line.startswith("# "):
                        index[filename] = line[2:].strip()
                        break
    return index
