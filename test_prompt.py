from src.parser import load_all_transcripts
from src.indexer import build_expert_index
from src.retriever import retrieve_for_question
from src.prompts import GUIDE_PROMPT

chunks = load_all_transcripts("data")

by_expert = {}

for chunk in chunks:
    by_expert.setdefault(chunk["expert"], []).append(chunk)

indexes = build_expert_index(by_expert)

idx = indexes["Dr. Jean Martin"]

question = "How would you describe current adoption of robotic surgery in your market?"

docs = retrieve_for_question(idx, question, k=4)

excerpt = "\n".join(
    f"[{d.metadata['timestamp']}] {d.page_content}"
    for d in docs
)

prompt = GUIDE_PROMPT.format(
    question=question,
    excerpt=excerpt
)

print("Prompt characters:", len(prompt))
print("Prompt words:", len(prompt.split()))
print()
print("----- EXCERPT -----")
print(excerpt)
print()
print("----- PROMPT -----")
print(prompt)