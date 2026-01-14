"""Test prompt optimization with mock data."""

from langfuse import Langfuse

from agentops.optimization.lib_prompt_optimization import PromptOptimizer
from agentops.optimization.lib_traces_scores import get_traces_and_scores
from agentops.service_provider.openai_provider import OpenAIProvider


def run_prompt_optimization(
    session_ids,
    score_name,
    prompt_name,
    prompt_label,
    num_examples,
    num_iterations,
):
    """
    Run prompt optimization using Langfuse and PromptOptimizer.

    Args:
        session_ids (list): List of Langfuse session IDs to retrieve traces and scores from. Each session corresponds to set of traces.
        score_name (str): Name of the score/metric to use for feedback (e.g., "Journey Success").
        prompt_name (str): Name of the prompt in Langfuse to optimize.
        prompt_label (str): Label of the prompt version to optimize.
        num_examples (int): Number of trajectories to use for optimization.
        num_iterations (int): Number of optimization iterations (1 for single-step optimization, >1 for iterative).
    """
    langfuse = Langfuse()
    optimizer = PromptOptimizer(
        llm_client=OpenAIProvider(),
        num_examples=num_examples,
        num_iterations=num_iterations,
    )
    current_prompt = langfuse.get_prompt(prompt_name, label=prompt_label).prompt
    results = [
        get_traces_and_scores(session_id, score_names=[score_name])
        for session_id in session_ids
    ]
    trajectory_lst = []
    score_lst = []
    for result in results:
        trajectory_lst.append(result["conversation"])
        scores = [
            e["value"] for e in result["score"] if e["score_name"] == score_name
        ]
        score_lst.append(str(scores[0]))
    if num_iterations == 1:
        optimized_lst = [
            optimizer.optimize(current_prompt, trajectory_lst, score_lst)
        ]
        print(f"{'='*60}")
        print(f"Current prompt: {current_prompt}")
        print(f"Prompt name: {prompt_name}")
        print(f"Prompt label: {prompt_label}")
        print(f"Optimized prompt: {optimized_lst[0]}")
        print(
            f"Prompt length: {len(current_prompt)} -> {len(optimized_lst[0])} chars"
        )
        print(f"{'='*60}")
    else:
        optimized_lst = optimizer.iterative_optimize(
            current_prompt, trajectory_lst, score_lst
        )
        for i, optimized_prompt in enumerate(optimized_lst):
            print(f"{'='*60}")
            print(f"Optimized prompt {i+1}: {optimized_prompt}")
            print(
                f"Prompt length: {len(current_prompt)} -> {len(optimized_prompt)} chars"
            )
            print(f"{'='*60}")

    for optimized in optimized_lst:
        _ = langfuse.create_prompt(
            name=prompt_name,
            prompt=optimized,
            labels=[prompt_label],  # Labels help organize and retrieve prompts
            tags=["langflow", "system"],  # Tags for categorization
            type="text",  # "text" or "chat"
            config={"temperature": 0.7, "max_tokens": 150},  # Optional config
            commit_message="Initial customer greeting prompt",  # Version control message
        )
