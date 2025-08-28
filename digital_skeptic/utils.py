import re
from typing import List


_WS = re.compile(r"\s+")


EMOTIONALLY_CHARGED = {
    "disastrous", "shocking", "unprecedented", "catastrophic", "outrageous",
    "scandal", "furious", "slam", "devastating", "corrupt", "incompetent",
}


BIAS_CUES = {
    "reportedly", "allegedly", "some say", "critics say", "sources say",
    "according to insiders", "without evidence", "it is believed",
}


LOADED_TERMS = {
    "regime", "puppet", "fake news", "witch hunt", "hoax", "cover-up",
}


ANONYMITY_TERMS = {"anonymous", "unnamed", "insider", "source close to"}


MODALITY = {"may", "might", "could", "would", "should", "appears", "seems"}


NUMERIC_PATTERN = re.compile(r"\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\b")


SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")




def clean_text(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = _WS.sub(" ", text)
    return text.strip()




def split_sentences(text: str) -> List[str]:
    # Lightweight sentence splitting
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]




def score_sentence_for_claim(s: str) -> float:
    score = 0.0
    if NUMERIC_PATTERN.search(s):
        score += 0.8
    # If sentence contains reporting verbs or modality, treat as claim-like
    for cue in ("said", "stated", "announced", "reported"):
        if cue in s.lower():
            score += 0.5
    if any(w in s.lower() for w in MODALITY):
        score += 0.3
    # Named entities later add weight, but here just length/structure heuristic
    if 60 <= len(s) <= 280:
        score += 0.3
    return score