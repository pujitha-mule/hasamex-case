import tiktoken
from dataclasses import dataclass, field

# Rough price per 1K tokens (USD) – update if pricing changes
PRICE = {
    "gpt-4o-mini": {"in": 0.00015, "out": 0.0006},
    "text-embedding-3-small": {"in": 0.00002, "out": 0.0},
}

@dataclass
class UsageTracker:
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    per_model: dict = field(default_factory=dict)

    def add(self, model: str, in_tok: int, out_tok: int = 0):
        self.calls += 1
        self.input_tokens += in_tok
        self.output_tokens += out_tok
        p = PRICE.get(model, {"in": 0, "out": 0})
        self.cost_usd += (in_tok / 1000) * p["in"] + (out_tok / 1000) * p["out"]
        m = self.per_model.setdefault(model, {"calls": 0, "in": 0, "out": 0})
        m["calls"] += 1
        m["in"] += in_tok
        m["out"] += out_tok

def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    try:
        enc = tiktoken.encoding_for_model(model)
    except KeyError:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text or ""))

TRACKER = UsageTracker()