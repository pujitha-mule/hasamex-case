GUIDE_PROMPT = """Answer the interview-guide question for this expert using ONLY the retrieved transcript excerpt below.

Question:
{question}

Retrieved transcript excerpt:
{excerpt}

Return STRICT JSON in exactly this structure:
{{
  "answer": "A concise answer based only on the retrieved excerpt.",
  "quotes": [
    {{
      "text": "A verbatim quote from the excerpt.",
      "timestamp": "MM:SS",
      "speaker": "Speaker name"
    }}
  ],
  "confidence": "high"
}}

Rules:
- Use ONLY information contained in the retrieved excerpt.
- Do not use outside knowledge.
- If the excerpt does not answer the question, set "answer" to "Not addressed" and return an empty quotes list.
- Every quote MUST be copied verbatim from the retrieved excerpt.
- Every timestamp MUST be an exact timestamp appearing in the retrieved excerpt.
- The speaker MUST be the speaker associated with that timestamp.
- Do not invent quotes, timestamps, speakers, facts, or numbers.
- Keep the answer concise.
- Confidence must be one of: "high", "medium", "low".
"""


THEMES_PROMPT = """You are analyzing three expert call transcripts on robotic surgery in Europe (France, Germany, UK).

Task 1 — COMMON THEMES:
Identify 3-5 themes shared across experts.
For each, list supporting verbatim quotes with the expert's name and timestamp.

Task 2 — DIFFERENCES & PERSPECTIVES:
Identify where experts place different emphasis or offer different views.
Do NOT overstate these as direct disagreements — describe them as differences in emphasis, priority, or outlook.
For each, quote each perspective verbatim with expert name and timestamp.

Return STRICT JSON:
{{
  "themes": [
    {{
      "theme": "...",
      "summary": "...",
      "supporting": [
        {{
          "expert": "<full expert name>",
          "timestamp": "MM:SS",
          "quote": "<verbatim>"
        }}
      ]
    }}
  ],
  "differences": [
    {{
      "topic": "...",
      "summary": "<one-line neutral framing>",
      "perspectives": [
        {{
          "expert": "<full expert name>",
          "view": "<short framing>",
          "timestamp": "MM:SS",
          "quote": "<verbatim>"
        }}
      ]
    }}
  ]
}}

Rules:
- "expert" MUST be one of:
  Dr. Jean Martin,
  Anna Keller,
  Dr. Emily Carter.
- "timestamp" MUST be the timestamp of the turn the quote was taken from.
- "quote" MUST be verbatim from that turn.
- Do not invent experts, quotes, timestamps, facts, or numbers.
- Do not use outside knowledge.
- Do not present a difference in emphasis as a direct disagreement unless the transcripts explicitly contradict each other.

Transcripts:
{transcripts}
"""


QA_PROMPT = """Answer questions about three expert call transcripts on robotic surgery in Europe using ONLY the retrieved turns below.

Rules:
- Use ONLY information contained in the retrieved turns.
- Every factual claim must end with a citation in this exact format:
  [Expert, Market, MM:SS]
- Expert and timestamp MUST come from one of the retrieved turns below.
- The Market MUST match the market associated with that expert's retrieved turn.
- If the answer is not present in the retrieved turns, reply exactly:
  "Not in transcripts."
- Do not use outside knowledge.
- Do not invent facts, numbers, quotes, experts, markets, or timestamps.
- Copy quotes verbatim when quoting the transcripts.
- Keep the answer concise.

Question:
{question}

Retrieved turns:
{turns}
"""