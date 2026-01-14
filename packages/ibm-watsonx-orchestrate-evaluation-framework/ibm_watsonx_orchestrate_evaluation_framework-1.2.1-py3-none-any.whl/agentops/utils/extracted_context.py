from enum import StrEnum
from typing import Any, Mapping


class OperatorTypes(StrEnum):
    extractor = "Extractor"
    evaluator = "Evaluation"


def get_operator_type(operator):
    class_name = operator.__class__.__name__
    base_classes = operator.__class__.__bases__
    for base in base_classes:
        if base.__name__ == OperatorTypes.extractor:
            # might change to just extractor and evaluator
            return "extractor"
        if base.__name__ == OperatorTypes.evaluator:
            return "metric"

    raise TypeError(
        f"`{class_name}` must inherit from either `Evaluation` or `Extractor`"
    )


def update_context(
    operator, results: Any, extracted_context: Mapping[str, Any]
):
    operator_type = get_operator_type(operator)
    class_name = operator.__class__.__name__

    if not isinstance(results, list):
        results = [results]

    extracted_context[operator_type].update({class_name: results})

    return extracted_context
