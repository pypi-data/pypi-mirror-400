from agentops.metrics.evaluations import Evaluation
from agentops.metrics.metrics import EvaluatorData


class DummyMetric(Evaluation):
    def __init__(self, llm_client=None, config=None):
        super().__init__(llm_client, config)

    def do_evaluate(
        self,
        messages,
        extracted_context,
        ground_truth=None,
        metadata=None,
    ):
        return EvaluatorData(
            eval_name="dummy_metric",
            value=True,
            metadata=metadata,
            data_type="BOOLEAN",
        )


if __name__ == "__main__":
    context = {"extractor": {}, "metric": {}}

    metric = DummyMetric()

    import rich

    rich.print(
        metric.evaluate(messages=[], ground_truth=[], extracted_context=context)
    )
