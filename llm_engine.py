import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"


# ---------------- FOLLOW-UP QUESTION ----------------

def generate_followup(answer):

    prompt = f"""
You are an interviewer.

Based on the candidate answer below,
generate ONE follow-up interview question.

Answer:
{answer}

Return only the question.
"""

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "phi3",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.5
                }
            },
            timeout=40
        )

        data = response.json()

        question = data.get("response", "").strip()

        return question

    except Exception as e:

        print("FOLLOW UP ERROR:", e)

        return "Can you explain your answer with an example?"


# ---------------- AI EVALUATION ----------------

def evaluate_with_llm(question, answers):

    prompt = f"""
You are a professional interviewer.

Evaluate the candidate answers below.

Answers:
{answers}

Return JSON:

{{
"overall_score": number between 0 and 10,
"strengths": "2 sentences describing strengths",
"weaknesses": "2 sentences describing weaknesses",
"improvements": "2 sentences suggesting improvement"
}}
"""

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "phi3",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 200
                }
            },
            timeout=60
        )

        data = response.json()

        text = data.get("response", "")

        start = text.find("{")
        end = text.rfind("}") + 1

        json_text = text[start:end]

        result = json.loads(json_text)

        return result

    except Exception as e:

        print("AI EVAL ERROR:", e)

        return {
            "overall_score": 6,
            "strengths": "You attempted the questions and showed some understanding.",
            "weaknesses": "Some explanations lacked technical depth.",
            "improvements": "Provide clearer explanations and examples."
        }