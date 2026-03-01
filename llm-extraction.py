import spacy
from spacy.lang.en.examples import sentences 
from transformers import pipeline
nlp = spacy.load("en_core_web_sm")
test_sentence = '''Watson & Crick section from a bio textbook. Rosalind Franklin materializes. Nettie Stevens (sex chromosomes) is another nearby node. This one basically demos itself.'''
doc = nlp(test_sentence)
print(doc.text)
words = []
for token in doc:
    print(token.text, token.pos_)
    if token.pos_ == "PROPN":
        words.append(token.text)
    print('Important Nouns')
for word in words:
    print(word)

def extract_nouns(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    words = []
    for token in doc:
        if token.pos_ == "PROPN":
            words.append(token.text)
    return words
            



