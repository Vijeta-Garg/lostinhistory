import spacy
from spacy.lang.en.examples import sentences 
from transformers import BertConfig, BertModel
from transformers import pipeline
import torch 
nlp = spacy.load("en_core_web_sm")
doc = nlp(sentences[1])
print(doc.text)
words = []
for token in doc:
    if token.pos_ == "NOUN" or token.pos_ == "PROPN":
        words.append(token.text)
for word in words:
    print(word)
    
# unmasker = pipeline('fill-mask', model='bert-base-uncased')

# unmasker("Artificial Intelligence [MASK] take over the world.")
unmasker = pipeline(
    task = 'fill-mask',
    model = 'google-bert/bert-base-uncased',
    dtype = torch.float16,
    device = 0
)
pipeline("Plants create [MASK] through a process known as photosynthesis.")
# configuration = BertConfig()
# model = BertModel(configuration)
# configuration = model.config