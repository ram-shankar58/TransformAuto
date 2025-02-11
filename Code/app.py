from flask import Flask, request, jsonify, send_file
import os
import subprocess
import requests
from handlers import process_task
import urllib.request
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

DATA_DIR = os.getenv("DATA_ROOT", os.path.join(os.getcwd(), "data"))
os.makedirs(DATA_DIR, exist_ok=True)  # Ensure the data directory exists
DATAGEN_PATH = os.path.join(DATA_DIR, "datagen.py")
DATAGEN_URL = "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py"

USER_EMAIL = os.getenv("USER_EMAIL", "23f1002296@ds.study.iitm.ac.in")  # Set user email from env

# Ensure `uv` is installed
def ensure_uv_installed():
    try:
        subprocess.run(["uv", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print("Installing uv...")
        subprocess.run(["pip", "install", "uv"], check=True)

def setup_data():
    """Download and run datagen.py while forcing a new data directory."""
    datagen_path = os.path.join(DATA_DIR, "datagen.py")

    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)

    # If datagen.py is missing, download it
    if not os.path.exists(datagen_path):
        urllib.request.urlretrieve(DATAGEN_URL, datagen_path)
        print(f"Downloaded datagen.py to {datagen_path}")

    # ✅ Run datagen.py with a forced data root
    try:
        env = os.environ.copy()
        env["DATA_ROOT"] = DATA_DIR  # Override any internal settings

        subprocess.run(
            ["python", datagen_path, USER_EMAIL, "--root", DATA_DIR],
            check=True,
            cwd=DATA_DIR,  # Ensure it runs in the correct directory
            env=env  # Pass modified environment
        )
        print("Data generation completed successfully.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error running datagen.py: {e.stderr}")

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