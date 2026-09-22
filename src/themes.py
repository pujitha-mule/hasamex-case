import json
from .prompts import THEMES_PROMPT
from .validator import validate_quotes_against_turns
from .metrics import TRACKER, count_tokens
from .extractor import _call_local_llm


def analyze_themes(chunks):
    block = ""

    for c in chunks:
        if c["speaker"] == "Interviewer":
            continue

        block += (
            f"[{c['market']} | {c['expert']} | {c['timestamp']}] "
            f"{c['text']}\n"
        )

    prompt = THEMES_PROMPT.format(transcripts=block)

    TRACKER.add("llama3.2:3b", count_tokens(prompt))

    resp = _call_local_llm(prompt)

    TRACKER.add("llama3.2:3b", 0, count_tokens(resp))

    try:
        cleaned = (
            resp
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )
        data = json.loads(cleaned)

    except Exception:
        data = {
            "themes": [],
            "differences": [],
            "raw": resp,
        }

    if "differences" not in data and "disagreements" in data:
        data["differences"] = data["disagreements"]

    all_turns = [
        {
            "expert": c["expert"],
            "market": c["market"],
            "timestamp": c["timestamp"],
            "speaker": c["speaker"],
            "text": c["text"],
        }
        for c in chunks
        if c["speaker"] != "Interviewer"
    ]

    for t in data.get("themes", []):
        t["supporting"], _ = validate_quotes_against_turns(
            t.get("supporting", []),
            all_turns,
        )

    for d in data.get("differences", []):
        d["perspectives"], _ = validate_quotes_against_turns(
            d.get("perspectives", d.get("positions", [])),
            all_turns,
        )

    return data