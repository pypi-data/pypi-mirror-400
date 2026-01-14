import json

from agentops.metrics.evaluations import Evaluation
from agentops.metrics.metrics import LangfuseMetric


class ConversationQualityScore(Evaluation):
    def __init__(self, llm_client=None):
        super().__init__(llm_client)

    def evaluate(
        self,
        messages,
        ground_truth=None,
        extracted_context=None,
        metadata=None,
    ):
        # add the custom logics here
        history = "\n".join([msg.role + ": " + msg.content for msg in messages])
        prompt = (
            "What's the quality of the conversation {} \n give me a score of 1 if everything looks right or 0 otherwise. "
            'output in {{"conversation_quality_score": 0}}'.format(history)
        )
        output = self.llm_client.query(prompt)
        try:
            score = json.loads(output)["conversation_quality_score"]
        except:
            score = 0

        extracted_context["metric"].update(
            {
                self.__class__.__name__: {
                    "conversation_quality_score": LangfuseMetric(
                        eval_name="conversation_quality_score",
                        value=score,
                        metadata=metadata,
                        data_type="float",
                    )
                }
            }
        )
