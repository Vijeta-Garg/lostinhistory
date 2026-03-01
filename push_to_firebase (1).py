"""
push_to_firebase.py
-------------------
Runs the full pipeline and pushes results to Firebase
so the frontend can read them.
"""

import json
import urllib.request
from graph_engine import GraphEngine
import spacy

FIREBASE_URL = "https://lostinhistory-default-rtdb.firebaseio.com"

def extract_nouns(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    words = []
    for token in doc:
        if token.pos_ == "PROPN":
            words.append(token.text)
    return words

def push_to_firebase(path, data):
    url = f"{FIREBASE_URL}/{path}.json"
    json_data = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=json_data,
        headers={"Content-Type": "application/json"},
        method="PUT"
    )
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read())

def analyze_and_push(text):
    names = extract_nouns(text)
    engine = GraphEngine("knowledge_graph.json")
    results = engine.analyze(names)

    push_to_firebase("missing_women", results["missing_women"])
    push_to_firebase("gender_ratio", results["gender_ratio"])
    push_to_firebase("graph", results["graph"])
    push_to_firebase("completeness_score", results["completeness_score"])

    line = "-" * 40
    print(line)
    print("LOST IN HISTORY - ANALYSIS")
    print(line)
    print(f"Names extracted:     {', '.join(names)}")
    print(f"Gender ratio:        {results['gender_ratio']['representation_percent']}% women")
    print(f"Completeness score:  {results['completeness_score']}")
    print(f"Missing women found: {len(results['missing_women'])}")
    for w in results["missing_women"]:
        print(f"  {w['name']} (score: {w['omission_score']})")
    print(line)
    print("Pushed to Firebase")
    print(line)

    return results


if __name__ == "__main__":
    test_text = """
    Watson and Crick discovered the double helix structure of DNA.
    Rosalind Franklin took Photo 51. Nettie Stevens discovered sex chromosomes.
    Marie Curie won two Nobel Prizes. Otto Hahn split the atom.
    """
    analyze_and_push(test_text)
