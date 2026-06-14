# from dotenv import load_dotenv
# from google import genai
# import os

# load_dotenv()

# client = genai.Client(
#     api_key=os.getenv("GEMINI_API_KEY")
# )

# def ask_ai(disease):

#     prompt = f"""
#     Explain this disease in simple language.

#     Disease: {disease}

#     Give:
#     - What is it?
#     - Main causes
#     - Foods to eat
#     - Foods to avoid
#     - When to see a doctor

#     Keep answer short.
#     """

#     response = client.models.generate_content(
#         model="gemini-2.5-flash",
#         contents=prompt
#     )

#     return response.text


# def ask_followup(disease, question):

#     prompt = f"""
#     Disease: {disease}

#     User Question:
#     {question}

#     Answer in simple language.
#     Give practical advice.
#     """

#     response = client.models.generate_content(
#         model="gemini-2.5-flashs",
#         contents=prompt
#     )

#     return response.text

from dotenv import load_dotenv
import google.generativeai as genai
import os

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL = "gemini-2.5-flash"  # Single source of truth — no more typos


def ask_ai(disease: str) -> str:
    """
    Generate a structured medical overview for a predicted disease.
    """
    prompt = f"""
You are a helpful and empathetic medical assistant.

Explain this disease clearly and concisely for a general audience.

Disease: {disease}

Respond in this exact markdown format:

## 🔍 What is {disease}?
[2-3 sentence explanation]

## 🧬 Main Causes
- [cause 1]
- [cause 2]
- [cause 3]

## 🥗 Foods to Eat
- [food 1]
- [food 2]
- [food 3]

## 🚫 Foods to Avoid
- [food 1]
- [food 2]
- [food 3]

## 🏃 Lifestyle Tips
- [tip 1]
- [tip 2]

## 🚨 When to See a Doctor
[Clear, direct guidance on urgency]

Keep the tone calm, informative, and non-alarmist.
"""
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )
    return response.text


def ask_followup(disease: str, question: str) -> str:
    """
    Answer a follow-up question about a diagnosed disease.
    """
    prompt = f"""
You are a knowledgeable and empathetic AI medical assistant.

The patient has been predicted to have: {disease}

Their question: {question}

Instructions:
- Answer in simple, clear language
- Be practical and actionable
- If the question is outside medical scope, gently redirect
- Keep response under 200 words
- Use bullet points where helpful
- Never replace professional medical advice — remind them if relevant
"""
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )
    return response.text


def get_disease_risk_level(disease: str) -> str:
    """
    Get AI-assessed risk level for a disease.
    Returns: LOW, MEDIUM, or HIGH
    """
    prompt = f"""
Classify the severity/urgency of this disease for a patient who just received a prediction:

Disease: {disease}

Respond with ONLY one word: LOW, MEDIUM, or HIGH

- LOW = manageable at home, not immediately life-threatening
- MEDIUM = requires medical attention within days/weeks
- HIGH = requires urgent or emergency medical attention
"""
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )
    level = response.text.strip().upper()
    if level not in ["LOW", "MEDIUM", "HIGH"]:
        return "MEDIUM"
    return level


def generate_health_report_summary(
    disease: str,
    symptoms: list,
    confidence: float
) -> str:
    """
    Generate a professional health report summary for PDF export.
    """
    symptoms_str = ", ".join(symptoms)
    prompt = f"""
Write a professional medical report summary paragraph (3-4 sentences) for:

Predicted Disease: {disease}
Reported Symptoms: {symptoms_str}
Model Confidence: {confidence:.1f}%

Include:
- Summary of findings
- Importance of professional consultation
- One key next step

Write in formal, third-person medical report style.
Do not use markdown formatting. Plain text only.
"""
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )
    return response.text
