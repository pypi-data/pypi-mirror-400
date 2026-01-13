# src/aiel_auth/config.py
from pathlib import Path
AIEL_DIR = Path(".aiel")
STATE_PATH = AIEL_DIR / "state.json"
INDEX_PATH = AIEL_DIR / "index.json"
COMMITS_DIR = AIEL_DIR / "commits"

class Settings():
    AIEL_DIR: Path =  Path(".aiel")
    STATE_PATH: Path = AIEL_DIR / "state.json"
    INDEX_PATH: Path = AIEL_DIR / "index.json"
    COMMITS_DIR: Path = AIEL_DIR / "commits"
    # BASE_URL: str = "http://localhost:8012"
    BASE_URL: str = "https://aiel-data-plane-service-606160957768.us-east1.run.app"

settings = Settings()
