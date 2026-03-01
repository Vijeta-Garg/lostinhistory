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
            


from graph_engine import GraphEngine

engine = GraphEngine("knowledge_graph.json")

# test it
text = "Watson and Crick discovered DNA. Rosalind Franklin took Photo 51. Nettie Stevens discovered sex chromosomes."
names = extract_nouns(text)
print("Names found:", names)

results = engine.analyze(names)
print(results)