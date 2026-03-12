import os
import requests


class GroqClient:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.model   = "llama-3.3-70b-versatile"
        self.url     = "https://api.groq.com/openai/v1/chat/completions"

    def build_system_prompt(self, data_context: str) -> str:
        return (
            "You are a data analyst assistant embedded in a Tableau dashboard.\n"
            "You have been given a dataset to analyze. Answer questions clearly and concisely.\n"
            "When showing data, use markdown tables where helpful.\n"
            "Be specific with numbers — cite actual values from the data.\n"
            "If asked something the data cannot answer, say so clearly.\n\n"
            f"Here is the dataset you are working with:\n\n{data_context}"
        )

    def chat(self, history: list, data_context: str) -> str:
        messages = [
            {"role": "system", "content": self.build_system_prompt(data_context)},
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