from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class FetchResult:
    url: str
    title: Optional[str]
    text: str
    byline: Optional[str] = None
    published: Optional[str] = None
    meta: Dict[str, str] = field(default_factory=dict)


@dataclass
class Claim:
    text: str
    evidence_hint: Optional[str] = None


@dataclass
class LanguageTone:
    classification: str
    details: str
    sentiment_score: Optional[float] = None


@dataclass
class RedFlag:
    label: str
    explanation: str


@dataclass
class VerificationQuestion:
    question: str


@dataclass
class Entities:
    people: List[str]
    orgs: List[str]
    locations: List[str]


@dataclass
class AnalysisResult:
    title: str
    url: str
    core_claims: List[Claim]
    tone: LanguageTone
    red_flags: List[RedFlag]
    questions: List[VerificationQuestion]
    entities: Entities
    counter_argument: Optional[str] = None