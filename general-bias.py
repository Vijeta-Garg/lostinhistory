from transformers import AutoTokenizer, TFAutoModelForSequenceClassification
from transformers import pipeline
tokenizer = AutoTokenizer.from_pretrained("d4data/bias-detection-model")
model = TFAutoModelForSequenceClassification.from_pretrained("d4data/bias-detection-model")

classifier = pipeline('text-classification', model=model, tokenizer=tokenizer) # cuda = 0,1 based on gpu availability
classifier("The irony, of course, is that the exhibit that invites people to throw trash at vacuuming Ivanka Trump lookalike reflects every stereotype feminists claim to stand against, oversexualizing Ivanka’s body and ignoring her hard work.")
