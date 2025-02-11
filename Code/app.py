from flask import Flask, request, jsonify, send_file
import os
import subprocess
import requests
from handlers import process_task

app = Flask(__name__)

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)  # Ensure the data directory exists

USER_EMAIL = os.getenv("USER_EMAIL", "default@example.com")  # Set user email from env

# Ensure `uv` is installed
def ensure_uv_installed():
    try:
        subprocess.run(["uv", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print("Installing uv...")
        subprocess.run(["pip", "install", "uv"], check=True)

# Download and run `datagen.py`
def setup_data():
    datagen_url = "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py"
    datagen_path = os.path.join(DATA_DIR, "datagen.py")

    if not os.path.exists(datagen_path):  # Download only if missing
        print("Downloading datagen.py...")
        response = requests.get(datagen_url)
        with open(datagen_path, "wb") as f:
            f.write(response.content)

    print("Running datagen.py to generate data...")
    subprocess.run(["python", datagen_path, USER_EMAIL], check=True)

# Run setup on startup
ensure_uv_installed()
setup_data()

@app.route('/run', methods=['POST'])
def run_task():
    task_description = request.args.get('task')
    
    if not task_description:
        return jsonify({"error": "Task description is required"}), 400

    try:
        result = process_task(task_description)
        return jsonify({"message": "Task executed successfully", "result": result}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

@app.route('/read', methods=['GET'])
def read_file():
    file_path = request.args.get('path')

    if not file_path or not file_path.startswith(DATA_DIR):
        return jsonify({"error": "Invalid file path"}), 400

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    return send_file(file_path, as_attachment=False)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
