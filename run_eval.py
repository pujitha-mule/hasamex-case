"""
Gold-set evaluation: measures retrieval recall and verbatim-quote recall
for the guide pipeline. Numbers are computed at runtime — no hardcoded totals.
"""
import json
from pathlib import Path
from dotenv import load_dotenv

from src.parser import load_all_transcripts
from src.indexer import build_expert_index
from src.retriever import retrieve_for_question
from src.extractor import answer_guide_for_expert

load_dotenv()

# Map each gold topic to the real interview-guide question it corresponds to,
# so retrieval is tested against natural questions, not topic identifiers.
TOPIC_QUESTIONS = {
    "adoption_current_state": "How would you describe current adoption of robotic surgery in your market?",
    "capital_budget_barrier": "What are the main barriers to adoption?",
    "cost_barrier": "What are the main barriers to adoption?",
    "training_barrier": "How important are surgeon training and clinical outcomes?",
    "roi_driver": "How important are hospital budgets and ROI in purchasing decisions?",
    "roi_position": "How important are hospital budgets and ROI in purchasing decisions?",
    "tco_focus": "How important are hospital budgets and ROI in purchasing decisions?",
    "clinical_outcomes_position": "How important are surgeon training and clinical outcomes?",
    "training_importance": "How important are surgeon training and clinical outcomes?",
    "adoption_outlook": "What adoption trend do you expect over the next 3-5 years?",
    "growth_expectation": "What adoption trend do you expect over the next 3-5 years?",
    "purchase_timeline": "What is the typical hospital decision-making timeline?",
    "balanced_economics": "How important are hospital budgets and ROI in purchasing decisions?",
}

def main():
    gold = json.loads(Path("eval/gold_quotes.json").read_text())
    chunks = load_all_transcripts("data")

    chunks_by_expert = {}
    for c in chunks:
        chunks_by_expert.setdefault(c["expert"], []).append(c)

    expert_indexes = build_expert_index(chunks_by_expert)

    retrieval_hits = 0
    verbatim_hits = 0
    total = 0

    for expert, topics in gold.items():
        idx = expert_indexes[expert]
        for topic, g in topics.items():
            total += 1
            question = TOPIC_QUESTIONS.get(
                topic, f"{topic} (about robotic surgery)"
            )

            # --- Retrieval recall ---
            docs = retrieve_for_question(idx, question, k=4)
            retrieved_text = " ".join(d.page_content for d in docs)
            if g["quote"] in retrieved_text:
                retrieval_hits += 1
                print(f"[RETRIEVAL HIT]  {expert:18s} | {topic}")
            else:
                print(f"[RETRIEVAL MISS] {expert:18s} | {topic}")

            # --- Verbatim recall (end-to-end through the guide pipeline) ---
            data = answer_guide_for_expert(question, idx)
            all_quotes = " ".join(q["text"] for q in data.get("quotes", []))
            if g["quote"] in all_quotes:
                verbatim_hits += 1
                print(f"[QUOTE HIT]      {expert:18s} | {topic}")
            else:
                print(f"[QUOTE MISS]     {expert:18s} | {topic}")

    print("\n=== Summary ===")
    print(f"Gold items        : {total}")
    print(f"Retrieval recall  : {retrieval_hits}/{total} = {retrieval_hits/total:.1%}")
    print(f"Verbatim recall   : {verbatim_hits}/{total} = {verbatim_hits/total:.1%}")

if __name__ == "__main__":
    main()