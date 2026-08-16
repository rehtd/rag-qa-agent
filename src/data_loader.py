"""Parse data/faq.txt into structured entries.

Entry format: blocks separated by lines containing only '---'.
Fields are 'key: value' lines; a multi-line value continues on lines
indented with two spaces.
"""
from dataclasses import dataclass
from pathlib import Path

REQUIRED_FIELDS = ["q_zh", "a_zh", "q_en", "a_en", "source", "date", "topic"]

@dataclass
class FaqEntry:
    id: str
    q_zh: str
    a_zh: str
    q_en: str
    a_en: str
    source: str
    date: str
    topic: str

def split_blocks(text: str) -> list[str]:
    blocks, current = [], []
    for line in text.splitlines():
        if line.strip() == "---":
            if current:
                blocks.append("\n".join(current))
                current = []
        elif line.strip().startswith("#") or not line.strip():
            continue
        else:
            current.append(line)
    if current:
        blocks.append("\n".join(current))
    return blocks

def parse_block(block: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    current_key = None
    for line in block.splitlines():
        if line.startswith("  "):
            if current_key:
                fields[current_key] = (fields.get(current_key, "") + " " + line.strip()).strip()
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            current_key = key.strip()
            fields[current_key] = value.strip()
    return fields

def parse_faq(text: str) -> list[FaqEntry]:
    entries = []
    for block in split_blocks(text):
        fields = parse_block(block)
        missing = [f for f in REQUIRED_FIELDS if f not in fields]
        if missing:
            raise ValueError(f"entry missing fields {missing}: {block[:80]!r}")
        eid = f"faq-{len(entries) + 1:03d}"
        entries.append(FaqEntry(id=eid, **{f: fields[f] for f in REQUIRED_FIELDS}))
    return entries

def load_faqs(data_dir: Path) -> list[FaqEntry]:
    p = data_dir / "faq.txt"
    if not p.exists():
        raise FileNotFoundError(f"missing data file: {p}")
    return parse_faq(p.read_text(encoding="utf-8"))
