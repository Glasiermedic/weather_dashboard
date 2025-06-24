from dotenv import load_dotenv
load_dotenv()
import pandas as pd
import subprocess
import logging
import sys
import os
import io
from pathlib import Path
from datetime import datetime

# 🔧 Force UTF-8 encoding for stdout (fixes emoji crash on Windows)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 📁 Set up log directory and file
BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
log_file = LOG_DIR / f"pipeline_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# 🪵 Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Scripts to run in order (relative paths from project root)
scripts = [
    "fetch/fetch_pws_history.py",
    "fetch/weatherjson_to_csv.py",
    "process_weather_data.py",
    "fetch/aggregate_to_daily.py",
    "fetch/aggregate_to_hourly.py"
]

def run_script(script_path):
    try:
        logger.info(f"▶️ Running {script_path}...")
        python_executable = sys.executable
        result = subprocess.run(
            [python_executable, str(script_path)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'  # prevents crash if some bytes still can't decode
        )

        logger.info(result.stdout)
        if result.stderr:
            logger.warning(result.stderr)
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error running {script_path}")
        logger.error(e.stderr)

def run_pipeline():
    logger.info("🚀 Starting weather data pipeline...\n")
    for script in scripts:
        run_script(script)
    logger.info("\n✅ Pipeline complete.")

if __name__ == "__main__":
    run_pipeline()