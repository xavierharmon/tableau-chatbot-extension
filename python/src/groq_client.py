import os
import requests


class GroqClient:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.model   = "llama-3.3-70b-versatile"
        self.url     = "https://api.groq.com/openai/v1/chat/completions"

    def build_system_prompt(self, data_context: str, role_context: str = "") -> str:
        parts = [
            "You are a data analyst assistant embedded in a Tableau dashboard.",
            "You have been given a dataset to analyze.",
            "When showing data, use markdown tables where helpful.",
            "Be specific with numbers — cite actual values from the data.",
            "If asked something the data cannot answer, say so clearly.",
        ]

        if role_context:
            parts += [
                "",
                role_context,
                "",
                "Always tailor your response style, tone, and level of detail to match the role context above.",
            ]

        parts += [
            "",
            "Here is the dataset you are working with:",
            "",
            data_context
        ]

        return "\n".join(parts)

    def chat(self, history: list, data_context: str, role_context: str = "") -> str:
        messages = [
            {"role": "system", "content": self.build_system_prompt(data_context, role_context)},
            *[{"role": m["role"], "content": m["content"]} for m in history]
        ]

        response = requests.post(
            self.url,
            headers={
                "Content-Type":  "application/json",
                "Authorization": f"Bearer {self.api_key}"
            },
            json={
                "model":       self.model,
                "messages":    messages,
                "max_tokens":  1024,
                "temperature": 0.2
            },
            timeout=30
        )

        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]