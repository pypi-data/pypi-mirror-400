"""Simple prompt optimization for runtime prompt tuning."""

import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from agentops.prompt.template_render import (
    MutationPromptRenderer,
    OpenLoopOptimizationPromptRenderer,
)
from agentops.service_provider.openai_provider import OpenAIProvider

ROOT_DIR = os.path.dirname(__file__)


def build_prompt(current_prompt, trajectories, feedback):
    trajectories_and_feedback = ""
    for i in range(len(trajectories)):
        trajectories_and_feedback += f"<trajectory {i}>\n{trajectories[i]}\n</trajectory {i}>\n<feedback {i}>\n{feedback[i]}\n</feedback {i}>\n-----\n"
    open_loop_optimization_prompt_template = OpenLoopOptimizationPromptRenderer(
        os.path.join(
            ROOT_DIR,
            "prompt",
            "open_loop_optimization_prompt.jinja2",
        )
    )
    open_loop_optimization_prompt = (
        open_loop_optimization_prompt_template.render(
            current_prompt=current_prompt,
            trajectories_and_feedback=trajectories_and_feedback,
        )
    )
    if isinstance(open_loop_optimization_prompt, list):
        open_loop_optimization_prompt = open_loop_optimization_prompt[0][
            "content"
        ]
    return open_loop_optimization_prompt


class Optimizer(ABC):
    """Base class for prompt optimization strategies."""

    @abstractmethod
    def optimize(
        self, current_prompt: str, trajectories: List[str], metrics: List[Dict]
    ) -> str:
        """
        Optimize prompt given trajectories and metrics.

        Args:
            current_prompt: Current prompt template
            trajectories: List of complete trajectory strings
            metrics: List of metric dictionaries with 'journey_success' key

        Returns:
            Optimized prompt string
        """
        pass


# open-loop optimization
# TODO: add text-grad and gepa optimization
class PromptOptimizer(Optimizer):
    """Prompt optimizer."""

    def __init__(
        self, llm_client=None, num_examples: int = 1, num_iterations: int = 1
    ):
        """
        Initialize PromptOptimizer.

        Args:
            llm_client: LLM client for optimization (defaults to OpenAIProvider)
            num_examples: Number of successful examples to use for optimization
            num_iterations: Number of iterations to run
        """
        self.llm_client = (
            llm_client if llm_client is not None else OpenAIProvider()
        )
        self.num_examples = num_examples
        self.num_iterations = num_iterations

    def optimize(
        self,
        current_prompt: str,
        trajectories: List[str],
        metrics: List[str],
    ) -> str:
        """
        TauBench-style bootstrap optimization.

        Args:
            current_prompt: Current prompt template
            trajectories: List of complete trajectory strings
            metrics: List of metric

        Returns:
            Optimized prompt
        """
        # Bootstrap: find high-quality examples
        demos = trajectories[: self.num_examples]
        feedback = metrics[: self.num_examples]
        # Create optimized prompt with demonstrations
        optimization_prompt = build_prompt(current_prompt, demos, feedback)
        response = self.llm_client.chat(
            messages=[{"role": "user", "content": optimization_prompt}],
            max_tokens=4096,
        )
        response = response.choices[0].message.content.strip()
        if "```" in response:
            response = response.split("```")[1].replace("```", "")
        return response

    def iterative_optimize(
        self,
        current_prompt: str,
        trajectories: List[str],
        metrics: List[str],
    ) -> str:
        """
        Iterative prompt optimization.

        Args:
            current_prompt: Current prompt template
            trajectories: List of complete trajectory strings
            metrics: List of metric

        Returns:
            Optimized prompt
        """
        new_prompts = []
        tokens = [2048 * i for i in range(1, self.num_iterations + 1)]
        for iteration in range(self.num_iterations):
            demos = trajectories[: self.num_examples]
            feedback = metrics[: self.num_examples]
            # Create optimized prompt with demonstrations
            optimization_prompt = build_prompt(current_prompt, demos, feedback)
            response = self.llm_client.chat(
                messages=[{"role": "user", "content": optimization_prompt}],
                max_tokens=tokens[iteration],
            )
            response = response.choices[0].message.content.strip()
            if "```" in response:
                response = response.split("```")[1].replace("```", "")
            new_prompts.append(response)
            current_prompt = response

        return new_prompts


class EvolutionaryOptimizer(Optimizer):
    """Evolutionary prompt optimization."""

    def __init__(
        self, llm_client=None, num_candidates: int = 1, num_iterations: int = 1
    ):
        """
        Initialize EvolutionaryOptimizer.

        Args:
            llm_client: LLM client for optimization (defaults to OpenAIProvider)
            num_candidates: Number of prompt variations to generate
            num_iterations: Number of iterations to run
        """
        self.llm_client = (
            llm_client if llm_client is not None else OpenAIProvider()
        )
        self.num_candidates = num_candidates
        self.num_iterations = num_iterations

    def optimize(
        self,
        current_prompt: str,
        trajectories: List[str],
        metrics: Optional[List[str]] = None,
    ) -> str:
        """
        Evolution for Prompt Adaptation (simplified).

        Args:
            current_prompt: Current prompt template
            trajectories: List of complete trajectory strings
            metrics: List of metric strings

        Returns:
            Optimized prompt
        """
        best_prompt = current_prompt

        for iteration in range(self.num_iterations):
            # Generate mutations
            mutations = self._generate_mutations(
                best_prompt, trajectories, metrics
            )

            # Evaluate and select best
            candidates = [best_prompt] + mutations
            # run environment simulation
            scores = [self._evaluate(p, metrics) for p in candidates]
            print(f"Scores: {scores}")

            best_idx = scores.index(max(scores))
            import random

            best_idx = random.choice([i for i, _ in enumerate(candidates)])
            best_prompt = candidates[best_idx]
            print(f"Best score: {scores[best_idx]}")

        return best_prompt

    def _generate_mutations(
        self, prompt: str, trajectories: List[str], metrics: List[Dict]
    ) -> List[str]:
        """Generate prompt variations using LLM."""
        failures = [
            t
            for t, m in zip(trajectories, metrics)
            if not m.get("journey_success", 1.0)
        ]
        successes = [
            t
            for t, m in zip(trajectories, metrics)
            if m.get("journey_success", 1.0)
        ]
        mutation_prompt_template = MutationPromptRenderer(
            os.path.join(ROOT_DIR, "prompt", "mutation_prompt.jinja2")
        )
        mutation_prompt = mutation_prompt_template.render(
            prompt=prompt,
            failures=failures,
            successes=successes,
            num_candidates=self.num_candidates,
        )

        response = self.llm_client.chat(
            messages=[{"role": "user", "content": mutation_prompt}],
            max_tokens=1500,
        )
        variants = [
            v.strip() for v in response.split("---VARIANT---") if v.strip()
        ]
        return variants[: self.num_candidates]

    def _evaluate(
        self, prompt: str, metrics: List[Dict]
    ) -> (
        float
    ):  # TODO: Implement a better evaluation function leveraging the environment.
        """Evaluate prompt quality (simplified)."""
        # Simple: count success mentions or use actual success rate
        score = sum(m.get("journey_success", 1.0) for m in metrics) / len(
            metrics
        )
        return score
