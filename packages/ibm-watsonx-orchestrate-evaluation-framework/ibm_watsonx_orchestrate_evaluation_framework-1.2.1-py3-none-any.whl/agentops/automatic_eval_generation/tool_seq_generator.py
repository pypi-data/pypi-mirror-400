"""
Generic Tool Sequence Generator
This module generates tool call sequences with arguments from user stories
using an LLM. It works with any OpenAPI specification
and is domain-agnostic.
"""

import json
import os
from typing import Any, Dict, List, Union

import pandas as pd
from dotenv import load_dotenv

from agentops.prompt.template_render import JinjaTemplateRenderer
from agentops.service_provider.provider import Provider

# Load environment variables from .env file
load_dotenv()


def load_prompt(prompt_path: str) -> JinjaTemplateRenderer:
    renderer = JinjaTemplateRenderer(prompt_path)
    return renderer


def _resolve_ref(ref: str, spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Resolve a JSON Schema $ref reference.
    Args:
        ref: The $ref string (e.g., "#/components/schemas/SchemaName")
        spec: The full OpenAPI spec
    Returns:
        The resolved schema object
    """
    # Remove the leading '#/' and split by '/'
    parts = ref.lstrip("#/").split("/")
    # Navigate through the spec to find the referenced schema
    result = spec
    for part in parts:
        result = result.get(part, {})
    return result


def _resolve_schema(
    schema: Dict[str, Any], spec: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Resolve a schema, following $ref if present.
    Args:
        schema: The schema object (may contain $ref)
        spec: The full OpenAPI spec
    Returns:
        The fully resolved schema
    """
    if "$ref" in schema:
        return _resolve_ref(schema["$ref"], spec)
    return schema


def parse_openapi_spec(
    openapi_spec: Union[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Parse an OpenAPI specification and extract tool definitions.
    Args:
        openapi_spec: Either a file path to OpenAPI JSON or a dict containing the spec
    Returns:
        List of tool definitions with name, description, and parameters
    """
    # Load spec if it's a file path
    if isinstance(openapi_spec, str):
        with open(openapi_spec, "r") as f:
            spec = json.load(f)
    else:
        spec = openapi_spec
    tools = []
    # Extract tools from paths
    paths = spec.get("paths", {})
    for path, path_item in paths.items():
        for method, operation in path_item.items():
            if method.lower() not in ["get", "post", "put", "delete", "patch"]:
                continue
            # Get tool name from 'tool_name' parameter default, or operation ID, or generate from path
            tool_name = None
            # First try to get from tool_name parameter
            for param in operation.get("parameters", []):
                if param.get("name") == "tool_name":
                    schema = param.get("schema", {})
                    tool_name = schema.get("default")
                    break
            # Fall back to operationId or generated name
            if not tool_name:
                tool_name = operation.get(
                    "operationId", f"{method}_{path.replace('/', '_')}"
                )
            # Get description
            description = operation.get(
                "description", operation.get("summary", "")
            )
            # Get parameters
            parameters = {}
            param_descriptions = {}
            # Path and query parameters
            for param in operation.get("parameters", []):
                param_name = param.get("name")
                # Skip the tool_name parameter as it's metadata, not a real parameter
                if param_name == "tool_name":
                    continue
                param_schema = param.get("schema", {})
                param_type = param_schema.get("type", "string")
                param_desc = param.get("description", "")
                parameters[param_name] = param_type
                if param_desc:
                    param_descriptions[param_name] = param_desc
            # Request body parameters
            request_body = operation.get("requestBody", {})
            if request_body:
                content = request_body.get("content", {})
                for _content_type, content_schema in content.items():
                    schema = content_schema.get("schema", {})
                    # Resolve $ref if present
                    schema = _resolve_schema(schema, spec)
                    properties = schema.get("properties", {})
                    for prop_name, prop_schema in properties.items():
                        prop_type = prop_schema.get("type", "string")
                        prop_desc = prop_schema.get("description", "")
                        parameters[prop_name] = prop_type
                        if prop_desc:
                            param_descriptions[prop_name] = prop_desc
            tools.append(
                {
                    "name": tool_name,
                    "description": description,
                    "parameters": parameters,
                    "parameter_descriptions": param_descriptions,
                }
            )
    return tools


def format_tools_for_prompt(tools: List[Dict[str, Any]]) -> str:
    """
    Format tool definitions into a string suitable for LLM prompting.
    Args:
        tools: List of tool definitions
    Returns:
        Formatted string describing available tools
    """
    formatted = []
    for tool in tools:
        tool_str = f"Tool: {tool['name']}\n"
        tool_str += f"Description: {tool['description']}\n"
        if tool["parameters"]:
            tool_str += "Parameters:\n"
            for param_name, param_type in tool["parameters"].items():
                param_desc = tool.get("parameter_descriptions", {}).get(
                    param_name, ""
                )
                if param_desc:
                    tool_str += (
                        f"  - {param_name} ({param_type}): {param_desc}\n"
                    )
                else:
                    tool_str += f"  - {param_name} ({param_type})\n"
        formatted.append(tool_str)
    return "\n".join(formatted)


def generate_starting_sentence(user_story: str, provider: Provider) -> str:
    """
    Generate an initial user utterance for a user story.
    Args:
        user_story: The user story/task description
        provider: Provider instance configured with the LLM
    Returns:
        The starting sentence the user would say
    """

    prompt_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "prompt",
        "starting_sentence_generation_prompt_autoeval.jinja2",
    )

    messages = load_prompt(prompt_path).render(user_story=user_story)

    # Call the LLM
    response = provider.chat(messages=messages, params={"temperature": 0.3})
    # Extract the response content
    if isinstance(response, dict) and "choices" in response:
        content = response["choices"][0]["message"]["content"]
    elif hasattr(response, "choices"):
        content = response.choices[0].message.content
    else:
        content = str(response)
    return content.strip()


def generate_sequence_for_story(
    user_story: str, tools: List[Dict[str, Any]], provider: Provider
) -> List[Dict[str, Any]]:
    """
    Generate a tool call sequence for a single user story.
    Args:
        user_story: The user story/task description
        tools: List of available tool definitions
        provider: Provider instance configured with the LLM
    Returns:
        List of tool calls with arguments
    """
    tools_description = format_tools_for_prompt(tools)

    prompt_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "prompt",
        "tool_sequence_generation_prompt_autoeval.jinja2",
    )
    messages = load_prompt(prompt_path).render(
        tools_description=tools_description, user_story=user_story
    )

    # Call the LLM
    response = provider.chat(messages=messages, params={"temperature": 0.3})
    # Extract the response content
    if isinstance(response, dict) and "choices" in response:
        content = response["choices"][0]["message"]["content"]
    elif hasattr(response, "choices"):
        content = response.choices[0].message.content
    else:
        content = str(response)
    # Parse the JSON response
    try:
        # Try to extract JSON from the response
        content = content.strip()
        # Remove markdown code blocks if present
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1]) if len(lines) > 2 else content
            content = content.replace("```json", "").replace("```", "").strip()
        tool_sequence = json.loads(content)
        return tool_sequence
    except json.JSONDecodeError as e:
        print(f"Failed to parse LLM response as JSON: {e}")
        print(f"Response: {content}")
        return []


def generate_eval_data_from_stories(
    user_stories_df: pd.DataFrame,
    openapi_spec: Union[str, Dict[str, Any]],
    tool_seq_client: Provider,
    task_id_column: str = "task_id",
    user_story_column: str = "story",
) -> Dict[str, Dict[str, Any]]:
    """
    Generate evaluation data (starting sentences and tool sequences) from user stories.

    Args:
        user_stories_df: DataFrame containing user stories
        openapi_spec: Path to OpenAPI JSON file or dict containing the spec
        tool_seq_client: Provider instance for generating sequences and starting sentences
        task_id_column: Name of the column containing task IDs (default: 'task_id')
        user_story_column: Name of the column containing user stories (default: 'story')
    Returns:
        Dictionary mapping task_id to dict with:
            - user_story: The original user story
            - starting_sentence: The initial user utterance
            - tool_sequence: List of tool calls with arguments
    """
    # Parse OpenAPI spec to get tool definitions
    tools = parse_openapi_spec(openapi_spec)

    # Generate tool sequences and starting sentences for each user story
    results = {}
    for _idx, row in user_stories_df.iterrows():
        task_id = (
            row[task_id_column]
            if task_id_column in user_stories_df.columns
            else user_stories_df.index[_idx]
        )
        user_story = row[user_story_column]
        print(f"Processing {task_id}...")
        try:
            # Generate starting sentence
            print("  Generating starting sentence...")
            starting_sentence = generate_starting_sentence(
                user_story=user_story, provider=tool_seq_client
            )
            # Generate tool sequence
            print("  Generating tool sequence...")
            tool_sequence = generate_sequence_for_story(
                user_story=user_story, tools=tools, provider=tool_seq_client
            )
            results[task_id] = {
                "user_story": user_story,
                "starting_sentence": starting_sentence,
                "tool_sequence": tool_sequence,
            }
        except Exception as e:
            print(f"Error processing {task_id}: {e}")
            results[task_id] = {
                "user_story": user_story,
                "starting_sentence": "",
                "tool_sequence": [],
            }
    return results
