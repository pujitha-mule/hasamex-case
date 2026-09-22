from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class LocalIndex:
    """
    Small local TF-IDF index.
    No API, model download, or OpenAI credits required.
    """

    def __init__(self, documents):
        self.documents = documents

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2)
        )

        texts = [d.page_content for d in documents]

        self.matrix = self.vectorizer.fit_transform(texts)

    def similarity_search(self, query, k=4):
        query_vector = self.vectorizer.transform([query])

        scores = cosine_similarity(
            query_vector,
            self.matrix
        )[0]

        ranked = scores.argsort()[::-1]

        results = []

        for i in ranked[:k]:
            results.append(self.documents[i])

        return results


def _to_doc(c):
    """
    Create a lightweight document object compatible
    with the rest of the application.
    """

    from langchain.schema import Document

    return Document(
        page_content=c["text"],
        metadata={
            "expert": c["expert"],
            "market": c["market"],
            "timestamp": c["timestamp"],
            "speaker": c["speaker"],
            "call_id": c["call_id"],
            "flag": c["flag"],
        },
    )


def build_index(chunks):
    """
    Build one local TF-IDF index.
    """

    docs = [
        _to_doc(c)
        for c in chunks
        if c["speaker"] != "Interviewer"
    ]

    return LocalIndex(docs)


def build_expert_index(chunks_by_expert):
    """
    Build a separate local index for each expert.
    """

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