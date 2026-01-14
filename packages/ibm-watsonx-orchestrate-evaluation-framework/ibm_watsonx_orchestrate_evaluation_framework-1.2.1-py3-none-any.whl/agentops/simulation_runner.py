import json
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Optional

from dotenv import load_dotenv
from openinference.instrumentation import using_session
from opentelemetry.context import attach as attach_otel_context
from opentelemetry.context import get_current as get_otel_context

from agentops.arg_configs import ControllerConfig
from agentops.evaluation_controller.evaluation_controller import (
    EvaluationController,
)
from agentops.llm_user.base_user import BaseUserSimulator
from agentops.runtime_adapter.runtime_adapter import RuntimeAdapter
from agentops.runtime_adapter.wxo_runtime_adapter import WXORuntimeAdapter
from agentops.utils.rich_utils import RichLogger
from agentops.utils.telemetry_platform import TelemetryPlatform

load_dotenv()

logger = RichLogger(__name__)


@dataclass
class ItemResult:
    output: str


class ExperimentResultsWrapper:
    """Mimic Langfuse's experiment item result structure.
    This is a temporary wrapper to be compatible with EvaluationRunner's experiment_results parameter.
    """

    def __init__(self, session_ids: List[str]):
        self.item_results = [ItemResult(output=sid) for sid in session_ids]


class SimulationRunner:
    def __init__(
        self,
        user_agent: BaseUserSimulator,
        agent: RuntimeAdapter,
        config: ControllerConfig,
    ):
        self.evaluation_controller = EvaluationController(
            runtime=agent,
            llm_user=user_agent,
            config=config,
        )
        self.session_id_prefix = f"session-{str(uuid.uuid4())}"
        self.counter = 0

    def run_wrapper(self, session_id=None):
        def run_task_langfuse(*, item, **kwargs):
            input = item.input
            user_story = input.get("story")
            starting_sentence = input.get("starting_sentence")
            agent_name = input.get("agent")

            return run_task(
                input=input,
                user_story=user_story,
                starting_sentence=starting_sentence,
                agent_name=agent_name,
            )

        def run_task_arize(*, dataset_row, **kwargs):
            input = json.loads(dataset_row["input"])
            user_story = input.get("story")
            starting_sentence = input.get("starting_sentence")
            agent_name = input.get("agent")

            return run_task(
                input=input,
                user_story=user_story,
                starting_sentence=starting_sentence,
                agent_name=agent_name,
            )

        def run_task(*, input, user_story, starting_sentence, agent_name):
            """
            Task function for Langfuse experiment
            """

            if session_id:
                logger.warn(
                    f"Ensure that session-id is unique. During evaluation, all traces associated with this session-id will be evaluated."
                )
                new_session_id = session_id + "-" + str(uuid.uuid4())
            else:
                new_session_id = str(uuid.uuid4())

            with using_session(new_session_id):
                _, _, _, new_session_id = self.evaluation_controller.run(
                    self.counter,
                    agent_name=agent_name,
                    story=user_story,
                    starting_user_input=starting_sentence,
                    session_id=(
                        None
                        if isinstance(
                            self.evaluation_controller.runtime,
                            WXORuntimeAdapter,
                        )
                        else new_session_id
                    ),
                )
            self.counter += 1
            return new_session_id

        if TelemetryPlatform().is_langfuse:
            return run_task_langfuse
        elif TelemetryPlatform().is_arize:
            return run_task_arize
        else:
            raise ValueError(
                f"Invalid telemetry platform: {TelemetryPlatform().platform}"
            )

    def run_parallel(
        self,
        dataset_items: List,
        max_workers: int = 5,
        experiment_prefix: Optional[str] = None,
    ) -> List[str]:

        otel_ctx = get_otel_context()

        def run_single_item(index: int, item) -> str:
            """Run a single dataset item in a worker thread."""
            attach_otel_context(otel_ctx)

            if experiment_prefix is not None:
                session_id = f"{experiment_prefix}-{str(uuid.uuid4())}"
            else:
                session_id = str(uuid.uuid4())

            with using_session(session_id):
                input_data = item.input if hasattr(item, "input") else item
                user_story = input_data.get("story")
                starting_sentence = input_data.get("starting_sentence")
                agent_name = input_data.get("agent")

                # in most cases, returned_session_id is the same as session_id
                # but in case of WXO, it is produced by the runtime

                _, _, _, returned_session_id = self.evaluation_controller.run(
                    index,
                    agent_name=agent_name,
                    story=user_story,
                    starting_user_input=starting_sentence,
                    session_id=(
                        None
                        if isinstance(
                            self.evaluation_controller.runtime,
                            WXORuntimeAdapter,
                        )
                        else session_id
                    ),
                )

            logger.info(f"Completed simulation {index}: {session_id}")
            return returned_session_id

        session_ids = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {
                executor.submit(run_single_item, idx, item): idx
                for idx, item in enumerate(dataset_items)
            }

            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                try:
                    session_id = future.result()
                    session_ids.append((idx, session_id))
                except Exception as e:
                    logger.error(f"Simulation {idx} failed: {e}")
                    session_ids.append((idx, None))

        session_ids.sort(key=lambda x: x[0])

        return ExperimentResultsWrapper(
            [session_id for _, session_id in session_ids]
        )
