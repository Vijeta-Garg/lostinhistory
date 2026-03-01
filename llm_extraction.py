import spacy
from graphengine import GraphEngine
engine = GraphEngine('./knowledge_graph.json')
def extract_nouns(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    words = []
    for token in doc:
        if token.pos_ == "PROPN" and token.text not in words and token.text:
            words.append(token.text)
    return words

def extract_names(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    words = []
    for ent in doc.ents:
        if ent.label_ == 'PERSON' and ent.text not in words:
            words.append(ent.text)
    return words
def extract_women(text):
    nouns = extract_names(text)
    women = engine._resolve_extracted_names(nouns)
    print(women)
    return women

print(extract_nouns("In 1953, James Watson and Francis Crick published their landmark paper in Nature, proposing that DNA takes the form of a double helix. Their model elegantly explained how genetic information could be stored and copied — the two strands of the helix could separate, each serving as a template for a new complementary strand. Watson and Crick's insight built upon earlier work establishing that DNA, not protein, was the carrier of genetic information. Maurice Wilkins, working at King's College London, had been studying DNA fibers using X-ray diffraction techniques, and his crystallographic data provided critical physical evidence for the helical structure. The famous \"Photo 51,\" an X-ray diffraction image of extraordinary clarity, revealed the unmistakable signature of a helix and allowed Watson and Crick to refine the dimensions of their model. For their discovery, Watson, Crick, and Wilkins shared the 1962 Nobel Prize in Physiology or Medicine."))

print(extract_names("In 1953, James Watson and Francis Crick published their landmark paper in Nature, proposing that DNA takes the form of a double helix. Their model elegantly explained how genetic information could be stored and copied — the two strands of the helix could separate, each serving as a template for a new complementary strand. Watson and Crick's insight built upon earlier work establishing that DNA, not protein, was the carrier of genetic information. Maurice Wilkins, working at King's College London, had been studying DNA fibers using X-ray diffraction techniques, and his crystallographic data provided critical physical evidence for the helical structure. The famous \"Photo 51,\" an X-ray diffraction image of extraordinary clarity, revealed the unmistakable signature of a helix and allowed Watson and Crick to refine the dimensions of their model. For their discovery, Watson, Crick, and Wilkins shared the 1962 Nobel Prize in Physiology or Medicine."))

print(extract_women("In 1953, James Watson and Francis Crick published their landmark paper in Nature, proposing that DNA takes the form of a double helix. Their model elegantly explained how genetic information could be stored and copied — the two strands of the helix could separate, each serving as a template for a new complementary strand. Watson and Crick's insight built upon earlier work establishing that DNA, not protein, was the carrier of genetic information. Maurice Wilkins, working at King's College London, had been studying DNA fibers using X-ray diffraction techniques, and his crystallographic data provided critical physical evidence for the helical structure. The famous \"Photo 51,\" an X-ray diffraction image of extraordinary clarity, revealed the unmistakable signature of a helix and allowed Watson and Crick to refine the dimensions of their model. For their discovery, Watson, Crick, and Wilkins shared the 1962 Nobel Prize in Physiology or Medicine."))
print(engine._resolve_name("Rosalind Franklin"))
print(engine.graph.nodes.get("Rosalind Franklin"))
print(list(engine.graph.neighbors("Rosalind Franklin")))    