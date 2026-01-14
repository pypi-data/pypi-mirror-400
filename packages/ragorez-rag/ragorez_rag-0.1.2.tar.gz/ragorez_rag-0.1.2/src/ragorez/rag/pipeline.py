from typing import Dict, Any

from .llm.llm_provider import LLMProvider
from .vector.db import DataBaseProvider


class RAGPipeline:

    def __init__(self,
                 vector_db: DataBaseProvider,
                 llm_provider: LLMProvider,
                 **kwargs):
        """
        prompt_template works with {question} and {context}. Question = initial prompt. Context = result of searching in knowledge database
        """
        self.vector_db = vector_db
        self.llm = llm_provider
        self.system_template = kwargs.get('system_template')
        self.prompt_template = kwargs.get('prompt_template') or "Question: {question}.\nAdditional Context:{context}."

    def query(self,
              question: str,
              n_results: int = 5) -> Dict[str, Any]:
        search_results = self.vector_db.search(question, n_results)
        context = "\n".join(search_results.answers)
        prompt = self.prompt_template.format(context=context, question=question)
        response = self.llm.generate(
            prompt=prompt,
            system_message=self.system_template,
            temperature=0,
            max_tokens=1000
        )
        return {
            "question": question,
            "answer": response,
            "sources": context,
        }
