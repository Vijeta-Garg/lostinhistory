from huggingface_hub import InferenceClient

client = InferenceClient(
    model="meta-llama/Llama-3.2-3B-Instruct",
    token="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"
)
def analyze_tone(text):
    response = client.chat_completion(
        messages=[{
            "role": "user",
            "content": f"""Analyze how this text represents the women in the event or achievement described. Describe the following in a cohesive paragraph:
            - score: 0-10 (0: very dismissive, 10: very inclusive), but don't include the score number just rank it
            - tone: one word describing the tone toward women
            - reason: one sentence summary
            no additional text before or after this, just that paragraph
            Text: {text}"""
        }],
        max_tokens=200
    )
    return response.choices[0].message.content
sample_text = "Miss Ada Lovelace, daughter of a poet, has taken an interest in the curious engine of Mr. Babbage. She has produced a series of notes and calculations, which are delightful in their literary flair. Though clever for a lady, it is Mr. Babbage's practical ingenuity that drives the machine forward, while Miss Lovelace's efforts remain an elegant amusement."
print(analyze_tone(sample_text))