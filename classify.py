from groq import Groq

GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

categories = [
    "Billing Issues",
    "Technical Support",
    "Account Management",
    "Feature Requests & Feedback",
    "Pre-Sales Inquiries",
    "Order & Shipping",
    "Legal & Compliance",
    "General Inquiries"
]

def classify_text(text):
    prompt = f"""
You are a strict classifier.

Your task is to classify the following customer support message into one or more of these **exact** categories:

{', '.join(categories)}

Message:
"{text}"

Respond ONLY with a comma-separated list of one or more categories from the list above. Do NOT invent new categories. Do not explain. Do not include any other text.
"""

    response = client.chat.completions.create(
        model="meta-llama/llama-4-maverick-17b-128e-instruct",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=50
    )

    output = response.choices[0].message.content.strip()
    return [cat.strip() for cat in output.split(",") if cat.strip() in categories]
