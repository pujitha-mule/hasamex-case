def retrieve_for_question(expert_index, question, k=4):
    """Retrieval-grounded: pull only the top-k relevant turns for this question."""
    docs = expert_index.similarity_search(question, k=k)
    # Restore chronological order for readability
    docs = sorted(docs, key=lambda d: d.metadata["timestamp"])
    return docs

def format_excerpt(docs):
    return "\n".join(
        f"[{d.metadata['timestamp']}] {d.metadata['speaker']}: {d.page_content}"
        for d in docs
    )