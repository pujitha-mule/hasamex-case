import re
from pathlib import Path
from typing import List, Dict


# Matches:
# 00:18
# Dr. Martin: Adoption is growing...
#
# and captures:
# timestamp
# speaker
# transcript text until the next timestamp
TURN_RE = re.compile(
    r"^\s*(\d{2}:\d{2})\s*\n"
    r"\s*([^:\n]+?):\s*(.*?)(?=^\s*\d{2}:\d{2}\s*$|\Z)",
    re.MULTILINE | re.DOTALL,
)


EXPERT_META = {
    "Transcript_1_France.txt": {
        "expert": "Dr. Jean Martin",
        "role": "Head of Urology",
        "market": "France",
        "flag": "🇫🇷",
    },
    "Transcript_2_Germany.txt": {
        "expert": "Anna Keller",
        "role": "Former Hospital Procurement Director",
        "market": "Germany",
        "flag": "🇩🇪",
    },
    "Transcript_3_UK.txt": {
        "expert": "Dr. Emily Carter",
        "role": "Consultant Urologist",
        "market": "United Kingdom",
        "flag": "🇬🇧",
    },
}


def parse_transcript(path: Path) -> List[Dict]:
    text = path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    meta = EXPERT_META[path.name]

    turns = []

    for ts, speaker, content in TURN_RE.findall(text):

        clean = re.sub(r"\s+", " ", content).strip()

        # Remove extraction/UI noise.
        clean = clean.replace("canvas", "").strip()

        if not clean:
            continue

        turns.append({
    "call_id": path.stem,
    "expert": meta["expert"],
    "role": meta["role"],
    "market": meta["market"],
    "flag": meta["flag"],
    "timestamp": ts,
    "speaker": speaker.strip(),
    "text": clean,
})

    return turns


def load_all_transcripts(data_dir: str = "data") -> List[Dict]:
    data_path = Path(data_dir)

    chunks = []

    for fname in EXPERT_META:
        f = data_path / fname

        if f.exists():
            chunks.extend(parse_transcript(f))

    return chunks


def load_interview_guide(data_dir: str = "data") -> List[str]:
    text = (
        Path(data_dir) / "Interview_Guide.txt"
    ).read_text(
        encoding="utf-8"
    )

    questions = re.findall(
        r"^\s*\d+\.\s*(.+?)\s*$",
        text,
        re.M
    )

    return questions