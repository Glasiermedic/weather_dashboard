import subprocess
import os
import sys

print("🚀 Starting weather data pipeline...\n")

# This ensures your current Python (from .venv) is used
venv_python = sys.executable

# Correct script paths (relative to this file)
scripts = [
    "fetch/fetch_pws_5min_raw.py",
    "fetch/aggregate_to_hourly.py",
    "fetch/aggregate_to_daily.py",
]

for script in scripts:
    script_path = os.path.join(os.path.dirname(__file__), script)
    print(f"\n▶️ Running {os.path.basename(script)}...\n")

    result = subprocess.run(
        [venv_python, script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    try:
        print(result.stdout.decode("utf-8"))
    except UnicodeDecodeError:
        print("⚠️ Could not decode stdout as UTF-8")

    try:
        if result.stderr:
            print(f"⚠️ Errors from {os.path.basename(script)}:\n{result.stderr.decode('utf-8')}")
    except UnicodeDecodeError:
        print(f"⚠️ Errors from {os.path.basename(script)}: Unable to decode stderr")

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(f"⚠️ Errors from {os.path.basename(script)}:\n{result.stderr}")

print("\n✅ Pipeline complete.")
