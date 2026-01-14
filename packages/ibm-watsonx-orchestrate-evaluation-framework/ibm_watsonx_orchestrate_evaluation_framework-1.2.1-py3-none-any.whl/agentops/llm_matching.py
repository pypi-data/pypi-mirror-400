"""
LLM Matching Module with Cosine Similarity Support

This module provides functionality for matching text using:
1. LLM-based matching (using a language model to determine semantic equivalence)
2. Embedding-based matching (using cosine similarity between text embeddings)
"""

import math
from typing import List

from fuzzywuzzy import fuzz

from agentops.prompt.template_render import (
    KeywordMatchingTemplateRenderer,
    SemanticMatchingTemplateRenderer,
)
from agentops.service_provider.watsonx_provider import Provider
from agentops.utils.utils import safe_divide


class LLMMatcher:
    def __init__(
        self,
        llm_client: Provider,
        keyword_template: KeywordMatchingTemplateRenderer,
        semantic_template: SemanticMatchingTemplateRenderer,
        use_llm_for_semantic: bool = True,
        embedding_model_id: str = "sentence-transformers/all-minilm-l6-v2",
        similarity_threshold: float = 0.8,
        enable_fuzzy_matching: bool = False,
    ):
        self.llm_client = llm_client
        self.keyword_template = keyword_template
        self.semantic_template = semantic_template
        self.embedding_model_id = embedding_model_id
        self.use_llm_for_semantic = use_llm_for_semantic
        self.similarity_threshold = similarity_threshold
        self.enable_fuzzy_matching = enable_fuzzy_matching

    def keywords_match(self, response_text: str, keywords: List[str]) -> bool:
        if len(keywords) == 0:
            return True
        # return True if no keywords are provided
        # This allows for skipping keyword check by providing an empty list
        keywords_text = "\n".join(keywords)
        prompt = self.keyword_template.render(
            keywords_text=keywords_text, response_text=response_text
        )
        response = self.llm_client.chat(prompt)
        result = response.choices[0].message.content.strip().lower()
        return result.startswith("true")

    def generate_embeddings(
        self, prediction: str, ground_truth: str
    ) -> List[List[float]]:

        embeddings = self.llm_client.encode([prediction, ground_truth])

        return embeddings

    def compute_cosine_similarity(
        self, vec1: List[float], vec2: List[float]
    ) -> float:
        """Calculate cosine similarity between two vectors using pure Python"""

        # Manual dot product calculation
        dot_product = sum(a * b for a, b in zip(vec1, vec2))

        # Manual magnitude calculations
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))

        return safe_divide(dot_product, (magnitude1 * magnitude2))

    def cosine_similarity_semantic_match(
        self, prediction: str, ground_truth: str
    ) -> bool:
        embeddings = self.generate_embeddings(prediction, ground_truth)
        cosine_similarity = self.compute_cosine_similarity(
            embeddings[0], embeddings[1]
        )

        return cosine_similarity >= self.similarity_threshold

    def llm_semantic_match(
        self, context, prediction: str, ground_truth: str
    ) -> bool:
        """Performs semantic matching for the agent's final response and the expected response using the starting sentence of the conversation as the context

        Args:
            context: The starting sentence of the conversation. TODO can also consider using the LLM user's story
            prediction: the predicted string
            ground_truth: the expected string

        Returns:
            a boolean indicating if the sentences match.
        """

        prompt = self.semantic_template.render(
            context=context, expected_text=ground_truth, actual_text=prediction
        )
        response = self.llm_client.chat(prompt)
        result = response.choices[0].message.content.strip().lower()

        return result.startswith("true")

    def fuzzywuzzy_semantic_match(
        self, prediction: str, ground_truth: str
    ) -> bool:

        similarity_score = fuzz.WRatio(prediction, ground_truth)

        return similarity_score > self.similarity_threshold

    def semantic_match(
        self,
        context: str,
        prediction: str,
        ground_truth: str,
        enable_fuzzy_matching: bool = False,
    ) -> bool:
        ## TODO arjun-gupta1 10/06/2025: revist retry with exponential backoff. Opted for direct fallback to cosine similarity to avoid latency for now.
        try:
            return self.llm_semantic_match(context, prediction, ground_truth)
        except Exception as e:
            print(f"LLM semantic match failed: {e}")

        if enable_fuzzy_matching:
            print("falling back to fuzzy matching")
            # Fallback to cosine similarity if LLM matching is not used or failed
            try:
                return self.cosine_similarity_semantic_match(
                    prediction, ground_truth
                )
            except Exception as e:
                print(
                    f"Cosine similarity failed: {e}. Falling back to fuzzywuzzy."
                )

            # Final fallback to fuzzywuzzy
            return self.fuzzywuzzy_semantic_match(prediction, ground_truth)
