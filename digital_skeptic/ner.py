from typing import List
from .types import Entities


def load_spacy_model():
    import spacy
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        # Suggest downloading model
        raise RuntimeError("spaCy model 'en_core_web_sm' not found. Run: python -m spacy download en_core_web_sm")




def extract_entities(text: str) -> Entities:
    nlp = load_spacy_model()
    doc = nlp(text)
    people = sorted({ent.text for ent in doc.ents if ent.label_ == "PERSON"})
    orgs = sorted({ent.text for ent in doc.ents if ent.label_ in {"ORG", "NORP"}})
    locs = sorted({ent.text for ent in doc.ents if ent.label_ in {"GPE", "LOC", "FAC"}})
    return Entities(people=people, orgs=orgs, locations=locs)