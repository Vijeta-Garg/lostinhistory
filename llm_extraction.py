import spacy
# from graph_engine import GraphEngine

def extract_nouns(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    name_tokens = set()
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            for token in ent:
                name_tokens.add(token.text)
    
    words = []
    for token in doc:
        if token.pos_ == "PROPN" and token.text not in words and token.text not in name_tokens:
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


print(extract_nouns("The discovery of nuclear fission in 1938 fundamentally transformed both physics and world history. Otto Hahn, working at the Kaiser Wilhelm Institute in Berlin, bombarded uranium atoms with neutrons and observed that the uranium nucleus had split into lighter elements — barium among them. This was a stunning result that defied existing models of nuclear physics, which had assumed that bombarding heavy nuclei with neutrons would produce only slightly lighter elements. Hahn published his radiochemical findings, and the theoretical explanation soon followed: the uranium nucleus, when struck by a neutron, could divide into two roughly equal fragments, releasing an enormous amount of energy predicted by Einstein's mass-energy equivalence. For this discovery, Otto Hahn was awarded the 1944 Nobel Prize in Chemistry. The implications were immediate and far-reaching — within seven years, nuclear fission had been harnessed for both devastating weaponry and, eventually, civilian energy production."))
print(extract_names("The discovery of nuclear fission in 1938 fundamentally transformed both physics and world history. Otto Hahn, working at the Kaiser Wilhelm Institute in Berlin, bombarded uranium atoms with neutrons and observed that the uranium nucleus had split into lighter elements — barium among them. This was a stunning result that defied existing models of nuclear physics, which had assumed that bombarding heavy nuclei with neutrons would produce only slightly lighter elements. Hahn published his radiochemical findings, and the theoretical explanation soon followed: the uranium nucleus, when struck by a neutron, could divide into two roughly equal fragments, releasing an enormous amount of energy predicted by Einstein's mass-energy equivalence. For this discovery, Otto Hahn was awarded the 1944 Nobel Prize in Chemistry. The implications were immediate and far-reaching — within seven years, nuclear fission had been harnessed for both devastating weaponry and, eventually, civilian energy production."))
