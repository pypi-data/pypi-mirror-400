import json

from agentops.evaluation_package import EvaluationPackage
from agentops.otel_support.otel_message_conversion import (
    convert_otel_to_message,
)
from agentops.type import EvaluationData, Message

with open(
    "//otel_support/collie_example.json",
    "r",
) as f:
    data = json.load(f)

tc_name = "collie_trial"


history = convert_otel_to_message(data["calls"][-1]["messages"])
for message in history:
    print(f"{message.role}: {message.content}")


with open(
    "//otel_support/data_simple.json",
    "r",
) as f:
    gt = json.load(f)

tc_name = "collie_trial"

gt = EvaluationData.model_validate(gt)


evaluation_package = EvaluationPackage(
    test_case_name=tc_name,
    messages=history,
    ground_truth=gt,
    conversational_search_data=None,
    resource_map=None,
)

(
    keyword_semantic_matches,
    knowledge_base_metrics,
    messages_with_reason,
    metrics,
) = evaluation_package.generate_summary()


print(metrics)
