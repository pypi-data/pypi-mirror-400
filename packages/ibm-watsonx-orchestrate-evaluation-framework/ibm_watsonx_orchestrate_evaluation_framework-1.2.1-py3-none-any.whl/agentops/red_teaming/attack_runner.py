import dataclasses
import glob
import json
import os
import traceback
from concurrent.futures import ThreadPoolExecutor

import rich
import yaml
from jsonargparse import CLI
from rich.progress import Progress

from agentops.arg_configs import AttackConfig
from agentops.evaluation_controller.evaluation_controller import (
    AttackEvaluationController,
)
from agentops.llm_user.llm_user_v1 import LLMUser
from agentops.prompt.template_render import LlamaUserTemplateRenderer
from agentops.red_teaming.attack_evaluator import (
    AttackEvaluator,
    evaluate_all_attacks,
)
from agentops.resource_map import ResourceMap
from agentops.runtime_adapter.wxo_runtime_adapter import WXORuntimeAdapter
from agentops.service_provider import USE_GATEWAY_MODEL_PROVIDER, get_provider
from agentops.type import AttackData
from agentops.utils import json_dump
from agentops.wxo_client import get_wxo_client


def process_attack(
    task_n, attack_path, config, inference_backend, llm_user, resource_map
):
    attack_filename = os.path.basename(attack_path).replace(".json", "")
    with open(attack_path, "r") as f:
        attack: AttackData = AttackData.model_validate(json.load(f))

    attack_evaluator = AttackEvaluator(config, resource_map, attack_filename)

    evaluation_controller = AttackEvaluationController(
        runtime=inference_backend,
        llm_user=llm_user,
        config=config,
        attack_data=attack,
        attack_evaluator=attack_evaluator,
    )
    rich.print(
        f"[bold magenta]Running attack: {attack_filename}[/bold magenta]"
    )
    history, _, _, _ = evaluation_controller.run(
        task_n,
        attack.story,
        agent_name=attack.agent,
        starting_user_input=attack.starting_sentence,
        attack_instructions=attack.attack_data.attack_instructions,
    )
    result = list()
    for message in history:
        result.append(message.model_dump())

    json_dump(
        os.path.join(
            config.output_dir, "messages", attack_filename + ".messages.json"
        ),
        result,
    )

    # Ensure there's a results dir and write a failure record if none was created
    result_path = os.path.join(
        config.output_dir, "results", attack_filename + ".result.json"
    )
    if not os.path.exists(result_path):
        # attack evaluator should have written a success on early termination; if not, mark as failed
        json_dump(
            result_path,
            {
                "attack_filename": attack_filename,
                "success": False,
                "attack_category": str(attack.attack_data.attack_category),
                "attack_name": getattr(attack.attack_data, "attack_name", ""),
                "attack_type": getattr(attack.attack_data, "attack_type", ""),
            },
        )

    return result


def run_attacks(config: AttackConfig):
    executor = ThreadPoolExecutor(max_workers=config.num_workers)
    wxo_client = get_wxo_client(
        config.auth_config.url,
        config.auth_config.tenant_name,
        config.auth_config.token,
    )
    resource_map = ResourceMap(wxo_client)
    inference_backend = WXORuntimeAdapter(wxo_client=wxo_client)
    provider_kwargs = {}
    if USE_GATEWAY_MODEL_PROVIDER:
        provider_kwargs.update(
            instance_url=wxo_client.service_url,
            token=wxo_client.api_key,
        )
    llm_user = LLMUser(
        wai_client=get_provider(
            model_id=config.llm_user_config.model_id, **provider_kwargs
        ),
        template=LlamaUserTemplateRenderer(
            config.llm_user_config.prompt_config
        ),
        user_response_style=config.llm_user_config.user_response_style,
    )

    print(
        f"Running red teaming attacks with tenant {config.auth_config.tenant_name}"
    )
    for folder in ["messages", "results", "evaluations"]:
        os.makedirs(os.path.join(config.output_dir, folder), exist_ok=True)

    available_res = set()
    if config.skip_available_results:
        available_res = set(
            [
                os.path.basename(f).replace(".result", "")
                for f in glob.glob(
                    os.path.join(config.output_dir, "results", "*.result.json")
                )
            ]
        )

    results_list = []
    attack_paths = []
    for path in config.attack_paths:
        if os.path.isdir(path):
            path = os.path.join(path, "*.json")
        attack_paths.extend(sorted(glob.glob(path)))

    futures = []
    task_n = 0

    for attack_path in attack_paths:
        if not attack_path.endswith(".json") or attack_path.endswith(
            "agent.json"
        ):
            continue

        if config.skip_available_results:
            if os.path.basename(attack_path) in available_res:
                print(
                    f"Skipping attack {os.path.basename(attack_path)} as results already exist."
                )
                continue

        future = executor.submit(
            process_attack,
            task_n,
            attack_path,
            config,
            inference_backend,
            llm_user,
            resource_map,
        )

        futures.append((attack_path, future))
        task_n += 1

    if futures:
        with Progress() as progress:
            task1 = progress.add_task(
                f"[purple]Running {len(futures)} attacks...", total=len(futures)
            )
            for attack_path, future in futures:
                try:
                    results_list.extend(future.result())
                except Exception as e:
                    rich.print(f"Attack {attack_path} fails with {e}")
                    traceback.print_exc()
                finally:
                    progress.update(task1, advance=1)

    attack_results = evaluate_all_attacks(config, resource_map)

    with open(
        os.path.join(config.output_dir, "config.yml"), "w", encoding="utf-8"
    ) as f:
        yaml.safe_dump(dataclasses.asdict(config), f)

    with open(
        os.path.join(config.output_dir, "attacks_results.json"), "w"
    ) as f:
        json.dump(attack_results, f, indent=2)

    print(f"Attack results saved to {config.output_dir}")


if __name__ == "__main__":
    run_attacks(CLI(AttackConfig, as_positional=False))
