import spacy
from spacy.lang.en.examples import sentences 
def extract_nouns(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    words = []
    for token in doc:
        if token.pos_ == "PROPN":
            words.append(token.text)
    return words
            


