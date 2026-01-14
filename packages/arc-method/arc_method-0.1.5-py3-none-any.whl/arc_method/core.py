from groq import Groq
from openai import OpenAI

__all__ = ["ArcMethod", "help"]


class ArcMethod:
    """
    ArcMethod - LLM-based interpretation engine.
    provider: "openai" or "llama"
    """

    def __init__(self, provider: str, api_key: str, model: str = None):
        self.provider = provider.lower()
        self.api_key = api_key

        if self.provider == "openai":
            self.model = model or "gpt-4o"
            self.client = OpenAI(api_key=self.api_key)

        elif self.provider == "llama":
            self.model = model or "llama-3.3-70b-versatile"
            self.client = Groq(api_key=self.api_key)

        else:
            raise ValueError("provider must be 'openai' or 'llama'")

    # -----------------------
    # Internal sync invokers
    # -----------------------

    def _invoke_openai(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content.strip()

    def _invoke_groq(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content.strip()

    # -----------------------
    # Public API (SYNC)
    # -----------------------

    def interact(self, system_prompt: str, user_prompt: str) -> str:
        """
        Arc Method interaction.
        Fully synchronous. Safe in all runtimes.
        """

        if self.provider == "openai":
            return self._invoke_openai(system_prompt, user_prompt)

        elif self.provider == "llama":
            return self._invoke_groq(system_prompt, user_prompt)

        else:
            raise RuntimeError("Invalid provider in interact()")

    @staticmethod
    def print_help():
        print("ArcMethod sync API. Use interact(system, user).")


def help():
    ArcMethod.print_help()
