from .prompts import QA_PROMPT
from .validator import validate_citations_in_evidence
from .metrics import TRACKER, count_tokens
from .extractor import _call_local_llm


FAIL_CLOSED_MESSAGE = (
    "Unable to provide a grounded answer from the retrieved evidence."
)


def ask(index, question, k=6):
    docs = index.similarity_search(question, k=k)

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

    evidence_block = "\n".join(
        f"[{t['expert']} | {t['market']} | {t['timestamp']}] "
        f"{t['speaker']}: {t['text']}"
        for t in turns
    )

    prompt = QA_PROMPT.format(
        question=question,
        turns=evidence_block,
    )

    TRACKER.add("llama3.2:3b", count_tokens(prompt))

    raw = (_call_local_llm(prompt) or "").strip()

    TRACKER.add("llama3.2:3b", 0, count_tokens(raw))

    if raw.lower() in {"not in transcripts.", "not in transcripts"}:
        return _result("Not in transcripts.", grounded=False, turns=turns)

    all_valid, valid_cites = validate_citations_in_evidence(raw, turns)
    if not all_valid:
        return _result(FAIL_CLOSED_MESSAGE, grounded=False, turns=turns)

    return _result(raw, grounded=True, turns=turns, citations=valid_cites)


def _result(answer, grounded, turns, citations=None):
    return {
        "answer": answer,
        "grounded": grounded,
        "citations": citations or [],
        "sources": turns,
    }