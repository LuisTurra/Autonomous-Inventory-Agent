import json
import os

from dotenv import load_dotenv
from groq import Groq

from src.llm.prompts import INVENTORY_ANALYSIS_PROMPT

load_dotenv()


class GroqClient:

    def __init__(self):

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY não encontrada.")

        self.client = Groq(api_key=api_key)

        self.model = "openai/gpt-oss-120b"

    def analyze_inventory(self, product_data):

        data_json = json.dumps(
            product_data, ensure_ascii=False, separators=(",", ":"), default=str
        )

        prompt = INVENTORY_ANALYSIS_PROMPT.format(product_data=data_json)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um analista executivo "
                        "de estoque e demanda. "
                        "Use exclusivamente os dados fornecidos. "
                        "Seja objetivo e não invente informações."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=2600,
        )

        result = response.choices[0].message.content

        finish_reason = response.choices[0].finish_reason

        result = self.clean_report(result)

        if finish_reason == "length":

            result += "\n\n⚠️ **Relatório truncado pelo limite " "de geração da IA.**"

        return result

    @staticmethod
    def clean_report(text):

        import re

        text = re.sub(r"\[svg\]\([^)]*\)", "", text)
        text = re.sub(r"\[[^\]]*\]\(http://localhost:[^)]+\)", "", text)
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()


if __name__ == "__main__":

    client = GroqClient()

    result = client.analyze_inventory(
        {
            "inventory": {
                "products_monitored": 100,
                "total_stock_units": 5000,
                "out_of_stock": 2,
                "below_reorder_point": 5,
                "near_reorder_point": 8,
            },
            "risk_summary": {"CRITICAL": 2, "HIGH": 3, "MEDIUM": 5, "LOW": 90},
            "demand": {
                "sales_30d": 1000,
                "sales_previous_30d": 900,
                "change_pct": 11.1,
                "products_with_sales": 40,
            },
        }
    )

    print(result)
