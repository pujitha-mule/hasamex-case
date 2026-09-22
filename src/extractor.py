import json
import urllib.request
import urllib.error

from .prompts import GUIDE_PROMPT
from .retriever import retrieve_for_question, format_excerpt
from .validator import validate_quotes_against_turns
from .metrics import TRACKER, count_tokens


OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"


def _strip_json(s: str) -> str:
    """Remove Markdown code fences if the model returns JSON inside them."""
    return (
        s.replace("```json", "")
         .replace("```", "")
         .strip()
    )


def _call_local_llm(prompt: str) -> str:
    """Call the local Ollama model."""

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0,
            "num_predict": 250,
            "num_ctx": 2048,
        },
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
        return result.get("response", "")

    except urllib.error.URLError as e:
        raise RuntimeError(
            "Could not connect to Ollama. "
            "Make sure Ollama is installed and running."
        ) from e

    except Exception as e:
        raise RuntimeError(f"Ollama request failed: {e}") from e


def answer_guide_for_expert(question, expert_index):
    """Answer one interview-guide question for one expert."""

    docs = retrieve_for_question(expert_index, question, k=4)

    turns = [
        {
            "expert": d.metadata["expert"],
            "market": d.metadata["market"],
            "timestamp": d.metadata["timestamp"],
            "speaker": d.metadata["speaker"],
            "text": d.page_content,
        }
        for d in docs
    ]

    excerpt = format_excerpt(docs)

    prompt = GUIDE_PROMPT.format(
        question=question,
        excerpt=excerpt,
    )

    TRACKER.add(OLLAMA_MODEL, count_tokens(prompt))

    resp = _call_local_llm(prompt)

    TRACKER.add(OLLAMA_MODEL, 0, count_tokens(resp))

    try:
        data = json.loads(_strip_json(resp))
    except Exception:
        data = {
            "answer": "Not addressed",
            "quotes": [],
            "confidence": "low",
        }

    if not isinstance(data, dict):
        data = {
            "answer": "Not addressed",
            "quotes": [],
            "confidence": "low",
        }

    if not isinstance(data.get("quotes"), list):
        data["quotes"] = []

    for quote in data.get("quotes", []):
        if isinstance(quote, dict):
            quote.setdefault(
                "expert",
                turns[0]["expert"] if turns else None,
            )

    valid_quotes, rejected_quotes = validate_quotes_against_turns(
        data.get("quotes", []),
        turns,
    )

    data["quotes"] = valid_quotes
    data["rejected_quotes"] = rejected_quotes
    data["retrieved_turns"] = turns

    if data.get("confidence") not in {"high", "medium", "low"}:
        data["confidence"] = "low"

    if not isinstance(data.get("answer"), str) or not data["answer"].strip():
        data["answer"] = "Not addressed"

    return data


def run_full_guide(questions, expert_indexes):
    """Run all interview-guide questions for all experts."""
    results = {}
    for question in questions:
        results[question] = {}
        for expert, idx in expert_indexes.items():
            results[question][expert] = answer_guide_for_expert(question, idx)
    return results