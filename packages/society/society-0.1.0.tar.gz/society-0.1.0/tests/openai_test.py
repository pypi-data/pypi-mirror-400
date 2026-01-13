from openai.types.responses import WebSearchToolParam
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModelSettings

model_settings = OpenAIResponsesModelSettings(
    openai_builtin_tools=[
        WebSearchToolParam(
            type="web_search",
        ),
    ]
)
agent = Agent("openai-responses:gpt-5.1", model_settings=model_settings)

result = agent.run_sync(
    "Who is the most likely 2028 US president? Be specific.",
)

print(result.output)
