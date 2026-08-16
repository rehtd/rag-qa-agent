from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
SNAPSHOT_DIR = ROOT / "data_snapshots"
MODELS_CACHE = ROOT / "models_cache"
INDEX_DIR = ROOT / "index"

EMBED_MODEL = "BAAI/bge-m3"
COLLECTION_NAME = "faq_pairs"
TOP_K = 3
ANSWER_MAX_CHARS = 300

DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"
