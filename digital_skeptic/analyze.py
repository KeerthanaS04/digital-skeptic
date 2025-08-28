# digital_skeptic/analyze.py
from typing import List, Optional
from .types import AnalysisResult, Claim, LanguageTone, RedFlag, VerificationQuestion, Entities
from .utils import (
    split_sentences,
    score_sentence_for_claim,
    EMOTIONALLY_CHARGED,
    BIAS_CUES,
    LOADED_TERMS,
    ANONYMITY_TERMS,
)
from .ner import extract_entities

# --- Sentiment analysis helper (VADER, fallback to 0.0) ---
def _sentiment(text: str) -> float:
    try:
        from nltk.sentiment import SentimentIntensityAnalyzer
        import nltk
        try:
            nltk.data.find("sentiment/vader_lexicon.zip")
        except LookupError:
            nltk.download("vader_lexicon")
        sia = SentimentIntensityAnalyzer()
        return sia.polarity_scores(text).get("compound", 0.0)
    except Exception:
        return 0.0


# --- Core Claims ---
def extract_core_claims(text: str, use_llm=False, llm=None) -> List[Claim]:
    if use_llm and llm is not None:
        from .prompts import CLAIMS_PROMPT
        bullets = llm.chat(
            [
                {"role": "system", "content": "You extract factual claims."},
                {"role": "user", "content": CLAIMS_PROMPT + text},
            ]
        )
        lines = [l.strip(" -*\t") for l in bullets.splitlines() if l.strip()]
        return [Claim(text=l) for l in lines[:5]]

    # fallback heuristic
    sents = split_sentences(text)
    ranked = sorted([(score_sentence_for_claim(s), s) for s in sents], reverse=True)
    return [Claim(text=s) for _, s in ranked[:5]]


# --- Tone Analysis ---
def language_tone_analysis(text: str) -> LanguageTone:
    lower = text.lower()
    sentiment = _sentiment(text)
    charged = any(w in lower for w in EMOTIONALLY_CHARGED)
    loaded = any(w in lower for w in LOADED_TERMS)

    if charged or loaded:
        cls = "Uses emotionally charged / persuasive language"
    else:
        cls = "Appears relatively neutral and factual"

    details = []
    if charged:
        details.append("Emotionally charged terms detected")
    if loaded:
        details.append("Loaded/pejorative terms detected")
    details.append(f"Sentiment (VADER compound): {sentiment:+.3f}")

    return LanguageTone(
        classification=cls,
        details="; ".join(details),
        sentiment_score=sentiment,
    )


# --- Red Flags ---
def detect_red_flags(text: str) -> List[RedFlag]:
    lower = text.lower()
    flags: List[RedFlag] = []

    if any(term in lower for term in ANONYMITY_TERMS):
        flags.append(
            RedFlag(
                label="Reliance on anonymous sources",
                explanation="References to anonymous or unnamed sources appear in the text.",
            )
        )
    if any(term in lower for term in BIAS_CUES):
        flags.append(
            RedFlag(
                label="Hedging/uncertainty language",
                explanation="Frequent use of terms like 'reportedly'/'allegedly' suggests claims may be unverified.",
            )
        )
    if any(term in lower for term in LOADED_TERMS):
        flags.append(
            RedFlag(
                label="Loaded terminology",
                explanation="Pejorative or partisan phrases may indicate bias.",
            )
        )
    if "according to" in lower and (
        "study" in lower or "report" in lower
    ) and ("http" not in lower and "www" not in lower):
        flags.append(
            RedFlag(
                label="Cited data without source link",
                explanation="Mentions of studies/reports without a source link.",
            )
        )
    if ("critics" in lower or "supporters" in lower) and not (
        "however" in lower or "on the other hand" in lower
    ):
        flags.append(
            RedFlag(
                label="Lack of balanced viewpoints",
                explanation="Opposing views are referenced but not explored.",
            )
        )

    return flags


# --- Verification Questions ---
def generate_verification_questions(
    text: str, claims: List[Claim], use_llm=False, llm=None
) -> List[VerificationQuestion]:
    if use_llm and llm is not None:
        from .prompts import VERIFICATION_QUESTION_PROMPT
        joined_claims = "\n".join(f"- {c.text}" for c in claims)
        bullets = llm.chat(
            [
                {"role": "system", "content": "You generate verification questions."},
                {
                    "role": "user",
                    "content": VERIFICATION_QUESTION_PROMPT + text + "\n\nClaims:\n" + joined_claims,
                },
            ]
        )
        lines = [l.strip(" -*\t") for l in bullets.splitlines() if l.strip()]
        return [VerificationQuestion(question=l) for l in lines[:4]]

    # fallback heuristic
    qs = []
    for c in claims[:4]:
        qs.append(
            VerificationQuestion(
                question=f"Can I find independent sources (gov data or reputable outlets) that corroborate: '{c.text}'?"
            )
        )
    if not qs:
        qs = [
            VerificationQuestion(
                question="Is there primary data (methodology, dataset, or official statement) backing the key assertions?"
            )
        ]
    return qs


# --- Counter-Argument ---
def simulate_counter_argument(text: str, use_llm=False, llm=None) -> Optional[str]:
    if use_llm and llm is not None:
        from .prompts import COUNTER_ARGUMENT_PROMPT
        return llm.chat(
            [
                {"role": "system", "content": "You are a fair, informed skeptic."},
                {"role": "user", "content": COUNTER_ARGUMENT_PROMPT + text},
            ],
            temperature=0.4,
            max_tokens=400,
        )
    return (
        "From a skeptical perspective, some claims may rely on unverified sources or omit context. "
        "Readers should ask for primary data, consider alternative explanations, and compare coverage across outlets."
    )


# --- Top-level Analyzer ---
def analyze_article(title: str, url: str, text: str, enable_llm: bool = False, llm=None) -> AnalysisResult:
    entities = extract_entities(text)
    claims = extract_core_claims(text, use_llm=enable_llm, llm=llm)
    tone = language_tone_analysis(text)
    red_flags = detect_red_flags(text)
    questions = generate_verification_questions(text, claims, use_llm=enable_llm, llm=llm)
    counter = simulate_counter_argument(text, use_llm=enable_llm, llm=llm)

    return AnalysisResult(
        title=title,
        url=url,
        core_claims=claims,
        tone=tone,
        red_flags=red_flags,
        questions=questions,
        entities=entities,
        counter_argument=counter,
    )
