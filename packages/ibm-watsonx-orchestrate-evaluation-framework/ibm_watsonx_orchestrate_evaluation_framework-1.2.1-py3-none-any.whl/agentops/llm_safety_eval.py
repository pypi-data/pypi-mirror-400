import json
import re

from agentops.metrics.llm_as_judge import AnswerDerailment, AnswerUnsafeTopic
from agentops.prompt.template_render import (
    DerailmentTemplateRenderer,
    UnsafeTopicTemplateRenderer,
)
from agentops.service_provider.watsonx_provider import Provider


class LLMSafetyJudge:
    def __init__(
        self,
        llm_client: Provider,
        answer_derailment: DerailmentTemplateRenderer,
        answer_unsafe_topic: UnsafeTopicTemplateRenderer,
    ):
        self.llm_client = llm_client
        self.answer_derailment_template = answer_derailment
        self.answer_unsafe_topic_template = answer_unsafe_topic

    def judge_derailment_in_answer(
        self, question: str, instructions: str, answer: str
    ) -> AnswerDerailment:
        prompt = self.answer_derailment_template.render(
            question=question, instructions=instructions, answer=answer
        )
        response = self.llm_client.chat(prompt)
        result = response.choices[0].message.content.strip().lower()
        try:
            json_str = re.search(r"\{.*\}", result, re.DOTALL).group(0)
            thejson = json.loads(json_str)
            answer_derailment = AnswerDerailment.model_validate(thejson)
        except Exception:
            answer_derailment = AnswerDerailment(
                in_scope="not sure", statement=answer, reason=result
            )
        return answer_derailment

    def judge_unsafe_topic_in_answer(
        self, question: str, instructions: str, answer: str
    ) -> AnswerUnsafeTopic:
        """
        Use LLM to judge if the answer contains unsafe topics.
        """
        prompt = self.answer_unsafe_topic_template.render(
            question=question, instructions=instructions, answer=answer
        )
        response = self.llm_client.chat(prompt)
        result = response.choices[0].message.content.strip().lower()
        try:
            json_str = re.search(r"\{.*\}", result, re.DOTALL).group(0)
            thejson = json.loads(json_str)
            answer_unsafe = AnswerUnsafeTopic.model_validate(thejson)
        except Exception:
            answer_unsafe = AnswerUnsafeTopic(
                is_safe="not sure", statement=answer, reason=result
            )

        return answer_unsafe


class LLMSafetyJudgeGraniteGuardian:
    def __init__(
        self,
        llm_client: Provider,
        answer_unsafe_topic: UnsafeTopicTemplateRenderer,
    ):
        self.llm_client = llm_client
        self.answer_unsafe_topic_template = answer_unsafe_topic

    def judge_unsafe_topic_in_answer(
        self, question, instructions, answer
    ) -> AnswerUnsafeTopic:
        prompt = self.answer_unsafe_topic_template.render(
            question=question, instructions=instructions, answer=answer
        )
        response = self.llm_client.chat(prompt)
        result = response.choices[0].message.content.strip().lower()
        is_safe = "no" if result == "yes" else "yes"

        return AnswerUnsafeTopic(is_safe=is_safe, statement=answer, reason="")
