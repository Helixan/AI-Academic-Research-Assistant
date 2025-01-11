from src.core.llm import LLM

class SummarizerAgent:
    def __init__(self, llm: LLM):
        self.llm = llm

    def summarize_text(self, text: str) -> str:
        system_prompt = (
            "You are a helpful assistant specialized in academic paper summarization. "
            "Provide a concise summary highlighting key findings, methodology, and conclusions."
        )

        user_prompt = (
            f"Summarize the following text:\n\n{text}\n\n"
            "Respond with a concise paragraph."
        )

        summary = self.llm.chat_completion(system_prompt, user_prompt)
        return summary
