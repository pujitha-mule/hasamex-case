\arkdown
# Hasamex – European Robotic Surgery Expert Call Analyzer

## What it does
Analyzes 3 expert-call transcripts (France, Germany, UK) to:
1. Answer a 6-question interview guide — **per expert, retrieval-grounded**
2. Extract **verbatim** quotes with timestamps
3. Surface common themes and disagreements across experts
4. Support free-form Q&A across all transcripts, with citations
5. Show token / cost metrics

## Setup
```bash
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
streamlit run app.py
Run the small evaluation:

bash
python run_eval.py
Architecture
text
Transcripts → turn-level parser → per-expert FAISS index
                                        │
              Interview question ───────┤
                                        ▼
                             Top-k retrieved turns (k=4)
                                        │
                                        ▼
                           LLM synthesis → strict JSON
                                        │
                                        ▼
                    Verbatim + timestamp validation
                                        │
                                        ▼
                     Structured output → Streamlit UI
Anti-hallucination strategy
Retrieval-grounded: guide answers only see top-k transcript turns,
not the whole transcript.

Strict JSON schema: quotes, timestamps, speaker are structured fields.

Verbatim quote validation: every returned quote must be a
substring of the retrieved excerpt — otherwise it's dropped.

Timestamp validation: only timestamps from the retrieved turns are allowed.

"Not addressed" / "Not in transcripts" fallbacks.

Q&A citation check: answers without a [Expert, Market, MM:SS] citation
are flagged in the UI.

Temperature 0.

Model choice
gpt-4o-mini — cheap, reliable JSON, strong instruction following.

text-embedding-3-small — cheap, good quality for short turns.

FAISS in-memory — zero infra; swap for managed vector DB at scale.

Evaluation
run_eval.py scores retrieval recall and verbatim quote recall against a
small gold set (eval/gold_quotes.json).

Scaling to 30+ transcripts
FAISS → managed vector DB with metadata filters (market, role, date).

Parallel fan-out of guide extraction per transcript (asyncio / Celery).

Cache per (transcript_id, question).

Hybrid BM25 + dense retrieval for better exact-quote recall.

Expand the gold set to track recall / precision over time.