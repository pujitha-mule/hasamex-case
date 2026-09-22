
# Hasamex AI Engineer Case Study

A local AI application for analyzing expert-call transcripts about robotic surgery adoption across France, Germany, and the UK.

The application provides:

- Interview-guide question answering for each expert
- Verbatim quotes with timestamps
- Cross-transcript Q&A
- Common themes
- Differences and perspectives
- Grounded evidence retrieval
- Quote and timestamp validation
- A small gold-set evaluation
- A hallucination/grounding test

---
## Demo & Deployment

- 🎥 **Demo Video:** [Watch the Demo](YOUR_DEMO_VIDEO_LINK)
- 🚀 **Live Application:** [Open the Deployed App](https://hasamex-ai-case.streamlit.app/)
- 💻 **Source Code:** [GitHub Repository](https://github.com/pujitha-mule/hasamex-case)

> The application uses local Ollama models (`llama3.2:3b` and `nomic-embed-text`) for generation and embeddings.
> The deployed version may require the Ollama runtime/models to be available in the deployment environment.

## Why Local AI?

The application uses Ollama for both embeddings and generation.

### Embedding model

`nomic-embed-text`

Used to create semantic vector representations of transcript turns.

### Generation model

`llama3.2:3b`

Used for:

- Interview-guide answers
- Theme synthesis
- Cross-transcript Q&A

Both models run locally through Ollama.

This means the current demo does not require an OpenAI API key or external LLM API credits.

---

## Retrieval

Each transcript turn is converted into a LangChain `Document` containing:

- Expert
- Market
- Timestamp
- Speaker
- Call ID
- Transcript text

The text is embedded using the local Ollama `nomic-embed-text` model and stored in FAISS.

The application maintains:

- A cross-transcript FAISS index for global Q&A.
- A separate FAISS index for each expert for interview-guide extraction.

Questions are converted into embeddings and matched against transcript turns using semantic similarity.

For example:

**Question:**

> What are the main barriers to adoption?

Retrieved evidence can include:

- France → capital budget approval
- Germany → cost and utilisation
- UK → funding and training capacity

This allows semantically related evidence to be retrieved even when the wording of the question differs from the transcript.

---

# Grounding and Hallucination Reduction

The application uses several safeguards to reduce unsupported answers.

## 1. Deterministic transcript parsing

Transcript timestamps and speaker turns are extracted using deterministic parsing rather than asking the LLM to reconstruct the transcript structure.

## 2. Retrieval grounding

For interview-guide questions, the LLM receives retrieved transcript evidence rather than unrestricted access to outside knowledge.

## 3. Structured output

The guide extraction pipeline requests structured JSON containing:

```json
{
  "answer": "...",
  "quotes": [
    {
      "text": "...",
      "timestamp": "MM:SS",
      "speaker": "..."
    }
  ],
  "confidence": "high"
}
````

## 4. Verbatim quote validation

Returned quotes are checked against the retrieved transcript turns.

If a quote cannot be verified, it is rejected instead of being displayed as evidence.

## 5. Timestamp validation

Displayed evidence must correspond to timestamps present in the retrieved source turns.

## 6. Fail-closed Q&A

If a question cannot be supported by the retrieved transcript evidence, the application returns:

> Not in transcripts.

rather than generating an unsupported factual answer.

---

# Example Questions

## Interview Guide

The application answers questions such as:

* How would you describe current adoption of robotic surgery in your market?
* What are the main barriers to adoption?
* How important are hospital budgets and ROI in purchasing decisions?
* How important are surgeon training and clinical outcomes?
* What adoption trend do you expect over the next 3–5 years?
* What is the typical hospital decision-making timeline?

## Cross-Transcript Q&A

Example:

> What are the main barriers to robotic surgery adoption across the three markets?

The answer can connect evidence from:

* France — capital budget approval
* Germany — cost and utilisation
* UK — funding and training capacity

Each source retains its expert, market, and timestamp metadata.

---

# Hallucination Test

Example:

> What percentage of hospitals in France currently use robotic surgery?

The transcripts do not provide this percentage, so the application should return:

> Not in transcripts.

---

# Themes and Differences

The application surfaces cross-market observations such as:

## Common themes

### Adoption is increasing but uneven

All three experts describe growing adoption while noting differences between larger, better-resourced institutions and smaller hospitals.

### Funding and economics are major considerations

Capital budgets, cost, utilisation, ROI, and the economic case appear repeatedly across the interviews.

### Training affects successful adoption

The experts emphasize that purchasing a robotic system alone is not sufficient. Hospitals also need appropriately trained staff and sufficient procedure volume.

## Differences & Perspectives

The application distinguishes differences in emphasis rather than automatically labeling them as direct disagreement.

For example:

* France and Germany place strong emphasis on the economic case during purchasing decisions.
* The UK expert describes economics and clinical strategy as more balanced.

The UI presents the supporting perspectives with their original timestamps.

---

# Project Structure

```text
hasamex-case/
│
├── app.py
├── run_eval.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── Interview_Guide.txt
│   ├── Transcript_1_France.txt
│   ├── Transcript_2_Germany.txt
│   └── Transcript_3_UK.txt
│
├── src/
│   ├── __init__.py
│   ├── parser.py
│   ├── indexer.py
│   ├── retriever.py
│   ├── extractor.py
│   ├── themes.py
│   ├── qa.py
│   ├── validator.py
│   ├── metrics.py
│   └── prompts.py
│
└── eval/
    └── gold_quotes.json
```

---

# Requirements

* Python 3.11+
* Ollama
* Git

The application has been tested on Windows using Python 3.11.

The setup commands below also provide the equivalent environment setup for macOS/Linux.

---

# Installation

## 1. Clone the repository

```bash
git clone https://github.com/pujitha-mule/hasamex-case.git
cd hasamex-case
```

## 2. Create a virtual environment

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

## 3. Install Python dependencies

```bash
python -m pip install -r requirements.txt
```

## 4. Install Ollama models

Install Ollama for your operating system, then run:

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

Verify:

```bash
ollama list
```

You should see:

```text
llama3.2:3b
nomic-embed-text
```

## 5. Start the application

Make sure Ollama is running, then:

```bash
python -m streamlit run app.py
```

Open the local Streamlit URL shown in the terminal, normally:

```text
http://localhost:8501
```

---

# Evaluation

A small gold-set evaluation is included in:

```text
eval/gold_quotes.json
```

The evaluation checks whether:

* Retrieval surfaces the transcript turn containing the expected quote.
* The answer-generation pipeline reproduces the expected quote verbatim.

Run:

```bash
python run_eval.py
```

The script reports:

* Gold items
* Retrieval recall
* Verbatim recall

The gold set is intentionally small and focused on representative interview-guide evidence.

---

# Testing Semantic Retrieval

The FAISS index can also be tested directly.

Example:

```bash
python -c "from src.parser import load_all_transcripts; from src.indexer import build_index; chunks=load_all_transcripts('data'); idx=build_index(chunks); [print(d.metadata['timestamp'], '|', d.metadata['expert'], '|', d.page_content[:120]) for d in idx.similarity_search('capital budget barriers', k=3)]"
```

A successful run should retrieve semantically relevant transcript turns such as the France 01:20 capital-budget discussion.

---

# Scaling to 30+ Transcripts

The current implementation is intentionally lightweight and suitable for a small case-study dataset.

For a larger production system, the architecture could evolve as follows:

### Current

```text
Local transcript files
        ↓
Ollama embeddings
        ↓
FAISS
        ↓
Local LLM
```

### Larger-scale version

```text
Transcript ingestion
        ↓
Chunking + metadata extraction
        ↓
Embedding pipeline
        ↓
Managed vector database
        ↓
Metadata filtering
        ↓
Hybrid retrieval
        ↓
Parallel LLM extraction
        ↓
Validation + evaluation
```

Potential improvements include:

* Managed vector storage
* Metadata filtering by market, expert, date, and call
* Hybrid BM25 + dense retrieval
* Parallel transcript processing
* Caching per transcript/question pair
* Larger evaluation sets
* Automated regression testing
* Word-level timestamp alignment

The current abstraction around `similarity_search()` makes the retrieval backend replaceable without changing the higher-level extraction and Q&A logic.

---

# Design Decisions

## Why deterministic parsing?

Transcript structure contains timestamps and speakers that should not be inferred by an LLM.

A deterministic parser provides predictable source boundaries before retrieval and generation.

## Why semantic retrieval?

Interview questions and transcript language may use different wording.

Semantic embeddings allow related concepts to be retrieved even when exact keywords do not match.

## Why FAISS?

FAISS provides a lightweight local vector-search implementation without requiring a separate database or cloud infrastructure.

This is appropriate for the three-transcript case-study dataset.

## Why Ollama?

The local Ollama setup provides:

* No API key requirement
* No external LLM dependency for the demo
* Local inference
* Reproducible model configuration

## Why validate quotes?

The most important requirement for interview analysis is traceability.

The application therefore treats generated evidence as untrusted until it can be matched against the transcript source.

---

# Known Limitations

* Timestamps are turn-level rather than word-level.
* The current dataset contains only three transcripts.
* The gold evaluation set is intentionally small.
* Theme summaries are LLM-generated and their supporting evidence is subsequently validated against transcript turns.
* Local model performance and response speed depend on the user's hardware.
* FAISS is currently in-memory and is not intended as a production persistence layer.

---

# Demo Flow

A suggested demo sequence:

## 1. Interview Guide

Show one question answered across:

* France
* Germany
* UK

Highlight the verbatim quotes and timestamps.

## 2. Cross-Transcript Q&A

Ask:

> What are the main barriers to robotic surgery adoption across the three markets?

Show the answer and expand the retrieved sources.

## 3. Grounding Test

Ask:

> What percentage of hospitals in France currently use robotic surgery?

Show:

> Not in transcripts.

## 4. Themes & Differences

Show:

* Common adoption/funding themes
* Differences in purchasing emphasis
* Growth outlook differences

## 5. Evaluation

Run:

```bash
python run_eval.py
```

and show the measured retrieval/verbatim results.

---

# Technology Stack

| Component     | Technology                 |
| ------------- | -------------------------- |
| UI            | Streamlit                  |
| Language      | Python 3.11                |
| Parsing       | Python regex               |
| Embeddings    | Ollama nomic-embed-text    |
| Vector Search | FAISS                      |
| LLM           | Ollama llama3.2:3b         |
| Validation    | Python                     |
| Evaluation    | Custom gold-set evaluation |
| Environment   | Local                      |

---

# Author

**Pujitha Mule**

B.Tech Computer Science and Engineering, VIT-AP

Built as part of the Hasamex AI Engineer Case Study.

````

**Copy everything inside the outermost block into `README.md`**. Don't copy the outer ```markdown markers themselves.
````

Parsing	Python regex
Embeddings	Ollama nomic-embed-text
Vector Search	FAISS
LLM	Ollama llama3.2:3b
Validation	Python
Evaluation	Custom gold-set evaluation
Environment	Local
Author

Pujitha Mule

B.Tech Computer Science and Engineering, VIT-AP

Built as part of the Hasamex AI Engineer Case Study.

