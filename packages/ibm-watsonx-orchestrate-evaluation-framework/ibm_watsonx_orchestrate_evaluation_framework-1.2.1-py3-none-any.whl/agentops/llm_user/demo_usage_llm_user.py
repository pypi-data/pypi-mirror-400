import os
import uuid

from openai import OpenAI

from agentops.llm_user.llm_user_v2 import LLMUserV2
from agentops.service_provider.portkey_provider import PortkeyProvider
from agentops.type import ContentType, Message

user_story = "Your user id is mia_li_3668. You want to fly from New York to Seattle on May 20 (one way). You do not want to fly before 11am est. You want to fly in economy. You prefer direct flights but one stopover also fine. If there are multiple options, you prefer the one with the lowest price. You have 3 baggages. You do not want insurance. You want to use your two certificates to pay. If only one certificate can be used, you prefer using the larger one, and pay the rest with your 7447 card. You are reactive to the agent and will not say anything that is not asked. Your birthday is in your user profile so you do not prefer to provide it."

portkey_client = PortkeyProvider(
    vendor="@openai",
    model_id="gpt-4o-mini",
    api_key=os.environ.get("PORTKEY_API_KEY"),
)

user_response_style = [
    "reactive to the agent and will not say anything that is not asked",
    "replies only in very short sentences and few words",
]

user_agent = LLMUserV2(
    llm_client=portkey_client,
    user_prompt_path="../prompt/universal_user_template.jinja2",
)

agent = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def get_agent_response(messages: list[dict]) -> str:

    response = agent.chat.completions.create(
        model="gpt-4o-mini", messages=messages
    )
    return response.choices[0].message.content


starting_user_input = Message(
    role="user", content="I want to fly.", type=ContentType.text
)


agent_system_prompt = Message(
    role="system",
    content="You are a helpful assistant. Keep your responses short and concise.",
    type=ContentType.text,
)

session_id = str(uuid.uuid4())
max_turns = 30
conversation_history = []
for i in range(max_turns):

    if len(conversation_history) == 0:
        conversation_history.append(agent_system_prompt)
        conversation_history.append(
            Message(
                role="assistant",
                content="Hi! How can I help you today?",
                type=ContentType.text,
            )
        )

        user_response = user_agent.generate_user_input(
            user_story=user_story,
            conversation_history=conversation_history,
            user_response_style=user_response_style,
            starting_user_input=starting_user_input,
        )
    else:
        user_response = user_agent.generate_user_input(
            user_story=user_story,
            conversation_history=conversation_history,
            user_response_style=user_response_style,
            starting_user_input=None,
        )

    conversation_history.append(user_response)
    print(f"User: {user_response.content}")

    if "END" in user_response.content:
        break

    # Get agent response
    agent_response_content = get_agent_response(
        [msg.model_dump() for msg in conversation_history]
    )
    # agent_response_content = get_langflow_agent_response(conversation_history, session_id)
    # agent_response_content = asyncio.run(get_langgraph_agent_response(conversation_history, session_id))
    print(f"Agent: {agent_response_content}")

    agent_response = Message(
        role="assistant", content=agent_response_content, type=ContentType.text
    )
    conversation_history.append(agent_response)


print(conversation_history)
