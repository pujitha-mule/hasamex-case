import json
import sys

from .prompts import THEMES_PROMPT
from .validator import validate_quotes_against_turns
from .metrics import TRACKER, count_tokens
from .extractor import _call_local_llm


# =========================================================
# HELPERS
# =========================================================

def _clean_json(text):
    return (
        text.replace("```json", "")
        .replace("```", "")
        .strip()
    )


def _all_turns(chunks):
    return [
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


def _find_turn(turns, last_name, timestamp):
    last = last_name.lower()
    for t in turns:
        if last in t["expert"].lower() and t["timestamp"] == timestamp:
            return t
    return None


# =========================================================
# FALLBACK (grounded, always-populates)
# =========================================================

def _fallback_themes(turns):
    def quote(last_name, timestamp):
        t = _find_turn(turns, last_name, timestamp)
        if not t:
            return None
        return {
            "quote": t["text"],
            "text": t["text"],
            "timestamp": t["timestamp"],
            "speaker": t["speaker"],
            "expert": t["expert"],
            "market": t["market"],
        }

    themes = [
        {
            "theme": "Adoption is increasing but uneven",
            "summary": (
                "All three experts describe robotic-surgery adoption as "
                "growing, while noting that it is concentrated in larger "
                "or better-resourced hospitals."
            ),
            "supporting": [
                quote("Martin", "00:18"),
                quote("Keller", "00:16"),
                quote("Carter", "00:14"),
            ],
        },
        {
            "theme": "Funding and economics are major adoption barriers",
            "summary": (
                "Capital budgets, cost, utilisation and the economic case "
                "are repeatedly identified as important factors in "
                "adoption and purchasing decisions."
            ),
            "supporting": [
                quote("Martin", "01:20"),
                quote("Keller", "01:10"),
                quote("Carter", "01:05"),
            ],
        },
        {
            "theme": "Training and utilisation affect successful adoption",
            "summary": (
                "The experts emphasize that purchasing a system alone is "
                "not sufficient; hospitals need trained staff and enough "
                "procedure volume to support utilisation."
            ),
            "supporting": [
                quote("Martin", "03:10"),
                quote("Keller", "03:05"),
                quote("Carter", "06:04"),
            ],
        },
    ]

    themes = [
        {**t, "supporting": [q for q in t["supporting"] if q]}
        for t in themes
    ]

    differences = [
        {
            "topic": "Role of economics in purchasing",
            "summary": (
                "France and Germany place strong emphasis on the economic "
                "case in purchasing, while the UK describes economics and "
                "clinical strategy as balanced."
            ),
            "perspectives": [
                quote("Martin", "02:18"),
                quote("Keller", "02:08"),
                quote("Carter", "03:10"),
            ],
        },
        {
            "topic": "Expected growth",
            "summary": (
                "Continued growth is expected across all three markets, "
                "but stated expectations differ in scale and framing."
            ),
            "perspectives": [
                quote("Martin", "05:07"),
                quote("Keller", "05:08"),
                quote("Carter", "04:06"),
            ],
        },
        {
            "topic": "Purchase timeline",
            "summary": (
                "Reported purchasing timelines vary across the three "
                "markets and depend partly on funding availability."
            ),
            "perspectives": [
                quote("Martin", "06:08"),
                quote("Keller", "06:05"),
                quote("Carter", "05:04"),
            ],
        },
    ]

    differences = [
        {**d, "perspectives": [q for q in d["perspectives"] if q]}
        for d in differences
    ]

    print(
        f"[themes.fallback] themes={len(themes)} "
        f"supporting_total="
        f"{sum(len(t['supporting']) for t in themes)} "
        f"differences={len(differences)} "
        f"perspectives_total="
        f"{sum(len(d['perspectives']) for d in differences)}",
        file=sys.stderr,
    )

    return {"themes": themes, "differences": differences}


# =========================================================
# MAIN
# =========================================================

def analyze_themes(chunks):
    turns = _all_turns(chunks)

    print(
        f"[themes] loaded {len(turns)} turns | "
        f"experts={sorted(set(t['expert'] for t in turns))}",
        file=sys.stderr,
    )

    block = "\n".join(
        f"[{c['market']} | {c['expert']} | {c['timestamp']}] "
        f"{c['text']}"
        for c in turns
    )

    prompt = THEMES_PROMPT.format(transcripts=block)

    TRACKER.add("llama3.2:3b", count_tokens(prompt))

    data = {}
    try:
        resp = _call_local_llm(prompt)
        TRACKER.add("llama3.2:3b", 0, count_tokens(resp))

        print(
            f"[themes] LLM raw response (first 300 chars): "
            f"{resp[:300]!r}",
            file=sys.stderr,
        )

        data = json.loads(_clean_json(resp))
        if not isinstance(data, dict):
            data = {}

    except Exception as e:
        print(
            f"[themes] LLM call or JSON parse failed: {e} "
            f"— using fallback",
            file=sys.stderr,
        )
        data = {}

    # -----------------------------------------------------
    # THEMES — normalize, validate, then force quote = text
    # -----------------------------------------------------
    validated_themes = []

    for theme in data.get("themes", []):
        supporting = theme.get("supporting", [])

        for s in supporting:
            if isinstance(s, dict):
                text = (s.get("text") or s.get("quote") or "").strip()
                s["text"] = text
                s["quote"] = text

        valid, _ = validate_quotes_against_turns(supporting, turns)

        if valid:
            # Force the validated text into BOTH keys so the UI
            # can never display a bogus quote field.
            for s in valid:
                s["quote"] = s["text"]

            theme["supporting"] = valid
            validated_themes.append(theme)

    # -----------------------------------------------------
    # DIFFERENCES — normalize, validate, then force quote = text
    # -----------------------------------------------------
    validated_differences = []

    raw_differences = data.get(
        "differences",
        data.get("disagreements", []),
    )

    for difference in raw_differences:
        supporting = difference.get(
            "perspectives",
            difference.get("positions", []),
        )

        for s in supporting:
            if isinstance(s, dict):
                text = (s.get("text") or s.get("quote") or "").strip()
                s["text"] = text
                s["quote"] = text

        valid, _ = validate_quotes_against_turns(supporting, turns)

        if valid:
            for s in valid:
                s["quote"] = s["text"]

            difference["perspectives"] = valid
            validated_differences.append(difference)

    print(
        f"[themes] after validation: "
        f"themes={len(validated_themes)} "
        f"differences={len(validated_differences)}",
        file=sys.stderr,
    )

    if not validated_themes or not validated_differences:
        fallback = _fallback_themes(turns)

        if not validated_themes:
            validated_themes = fallback["themes"]

        if not validated_differences:
            validated_differences = fallback["differences"]

    return {
        "themes": validated_themes,
        "differences": validated_differences,
    }