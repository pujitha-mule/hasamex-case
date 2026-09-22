"""
Retrieval index for the Hasamex case study.

Pipeline: transcript turns → per-expert FAISS index using Ollama embeddings.

Each index wraps a LangChain FAISS vector store and exposes a small
`similarity_search` interface so callers (extractor, qa, themes) do not
need to know which vector backend is in use.
"""

from langchain.schema import Document
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS


EMBED_MODEL = "nomic-embed-text"
OLLAMA_BASE = "http://localhost:11434"


def _embeddings():
    """Local embedding model served by Ollama. No API key required."""
    return OllamaEmbeddings(
        model=EMBED_MODEL,
        base_url=OLLAMA_BASE,
    )


def _to_doc(chunk):
    """Convert a parser chunk into a LangChain Document with metadata."""
    return Document(
        page_content=chunk["text"],
        metadata={
            "expert": chunk["expert"],
            "market": chunk["market"],
            "timestamp": chunk["timestamp"],
            "speaker": chunk["speaker"],
            "call_id": chunk.get("call_id", ""),
            "flag": chunk.get("flag", ""),
        },
    )


class LocalIndex:
    """
    Thin wrapper around a FAISS vector store.

    Exposes `similarity_search(query, k)` — the same interface used
    elsewhere in the app — so swapping backends later is a one-file change.
    """

    def __init__(self, documents):
        self.documents = documents
        self.vectorstore = FAISS.from_documents(documents, _embeddings())

    def similarity_search(self, query, k=4):
        return self.vectorstore.similarity_search(query, k=k)


def build_index(chunks):
    """Cross-expert index over all non-interviewer turns."""
    docs = [
        _to_doc(c)
        for c in chunks
        if c["speaker"] != "Interviewer"
    ]
    return LocalIndex(docs)


def build_expert_index(chunks_by_expert):
    """One FAISS index per expert, over their non-interviewer turns."""
    indexes = {}

    for expert, chunks in chunks_by_expert.items():
        docs = [
            _to_doc(c)
            for c in chunks
            if c["speaker"] != "Interviewer"
        ]

        if docs:
            indexes[expert] = LocalIndex(docs)

    return indexes