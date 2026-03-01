# from detoxify import Detoxify
# from transformers import pipeline
# classifier1 = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")
# classifier2 = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
sample_text = "Miss Ada Lovelace, daughter of a poet, has taken an interest in the curious engine of Mr. Babbage. She has produced a series of notes and calculations, which are delightful in their literary flair. Though clever for a lady, it is Mr. Babbage’s practical ingenuity that drives the machine forward, while Miss Lovelace’s efforts remain an elegant amusement."
# results = Detoxify('unbiased').predict([sample_text])
# print(results)
# print(classifier1(sample_text))
# print(classifier2(sample_text))

import requests
def analyze_tone(text):
    response = requests.post('http://127.0.0.1/api/generate', json={
        "model": "llama3",
        "prompt": f"""Analyze how {text} represents the women in event, achievement, or description explained with the following metrics:
            - score: 0-10 (0: very dismissive, 10: very inclusive)
            - tone: one word describing the tone of the description the women involved
            - reason: one sentence summary of your analysis
        Text: {text}
        """,
        "stream":False
       
    })
    return response.json()['response']
print(analyze_tone(sample_text))
    