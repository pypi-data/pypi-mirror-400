import logging
import os
import typing as T

import numpy as np
from openai.types.responses import WebSearchToolParam
from pydantic_ai import Agent
from pydantic_ai.builtin_tools import WebSearchTool
from pydantic_ai.models.anthropic import AnthropicModelSettings
from pydantic_ai.models.google import GoogleModelSettings
from pydantic_ai.models.openai import OpenAIResponsesModelSettings
from pydantic_ai.settings import ModelSettings

from society.deps import Deps

logger = logging.getLogger(__file__)


def create_agent(
    tools: list[T.Callable],
    output_tools: list[T.Callable],
    output_type: type,
    instructions: list[T.Callable],
) -> Agent[Deps]:
    model_name = sample_model_name()
    model_settings = sample_model_settings(model_name)

    # Google models don't support function tools + builtin tools together
    use_builtin_tools = "google" not in model_name and "gemini" not in model_name

    agent = Agent(
        model=model_name,
        model_settings=model_settings,
        deps_type=Deps,
        tools=tools,
        instructions=instructions,
        output_type=output_type,
        retries=5,
        builtin_tools=[WebSearchTool()] if use_builtin_tools else [],
    )

    logger.info(f"[create_agent] Sampled {model_name}")
    return agent


def sample_model_name() -> str:
    model_probs: list[tuple[str, float]] = []

    if "GOOGLE_API_KEY" in os.environ or "GEMINI_API_KEY" in os.environ:
        model_probs.extend(
            [
                ("google-gla:gemini-3-flash-preview", 1.0),
                # ("google-gla:gemini-2.5-pro", 1.0),
                # ("google-gla:gemini-2.5-flash", 1.0),
            ]
        )

    # if "OPENAI_API_KEY" in os.environ:
    #     model_probs.extend(
    #         [
    #             ("openai-responses:gpt-5.1", 1.5),
    #             ("openai-responses:gpt-4.1", 0.0),
    #             ("openai-responses:gpt-4o", 0.0),
    #             ("openai-responses:gpt-5-mini", 0.0),
    #         ]
    #     )

    # if "ANTHROPIC_API_KEY" in os.environ:
    #     model_probs.extend(
    #         [
    #             ("anthropic:claude-haiku-4-5", 1.0),
    #             ("anthropic:claude-sonnet-4-5", 1.0),
    #             ("anthropic:claude-opus-4-5", 0.0),
    #         ]
    #     )

    if len(model_probs) == 0:
        raise ValueError("No API keys found.")

    models, probs = zip(*model_probs)
    model_name = np.random.choice(models, p=np.array(probs) / sum(probs))

    return model_name


def sample_model_settings(model_name: str) -> ModelSettings:
    # Use provider-specific settings based on model name
    assert "gemini" in model_name or "google" in model_name
    settings: ModelSettings = GoogleModelSettings(
        temperature=1.4,
        # top_p=0.98,
    )
    return settings
#     elif "claude" in model_name or "anthropic" in model_name:
#         settings = AnthropicModelSettings()
#     elif (
#         "gpt" in model_name
#         or "openai" in model_name
#         or "o1" in model_name
#         or "o3" in model_name
#     ):
#         settings = OpenAIResponsesModelSettings(
#             # openai_reasoning_effort="low",
#             # openai_text_verbosity="low",
#             # openai_include_web_search_sources=True,
#             openai_builtin_tools=[
#                 WebSearchToolParam(
#                     type="web_search",
#                     # search_context_size="low",
#                 ),
#             ]
#         )
#     else:
#         settings = ModelSettings()

#     # max_temp = 2.0 if "gemini" in model_name else 1.0
#     # settings["temperature"] = np.random.uniform(0.7, max_temp)

#     # top_p

#     return settings
