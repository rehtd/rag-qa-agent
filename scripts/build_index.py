"""Build or rebuild the ChromaDB index from data/faq.txt."""
import shutil
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from src.config import COLLECTION_NAME, DATA_DIR, EMBED_MODEL, INDEX_DIR, MODELS_CACHE
from src.data_loader import load_faqs


def get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        cache_folder=str(MODELS_CACHE),
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def build_index(reset: bool = False) -> int:
    entries = load_faqs(DATA_DIR)
    ids, docs, metas = [], [], []
    for e in entries:
        for lang, q in (("zh", e.q_zh), ("en", e.q_en)):
            ids.append(f"{e.id}__{lang}")
            docs.append(q)
            metas.append({"entry_id": e.id, "lang": lang, "topic": e.topic, "source": e.source})
    if reset:
        shutil.rmtree(INDEX_DIR, ignore_errors=True)
    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(INDEX_DIR),
        embedding_function=get_embeddings(),
    )
    vectorstore.add_texts(texts=docs, ids=ids, metadatas=metas)
    return len(ids)


if __name__ == "__main__":
    print(f"indexed {build_index(reset='--reset' in sys.argv)} items")
