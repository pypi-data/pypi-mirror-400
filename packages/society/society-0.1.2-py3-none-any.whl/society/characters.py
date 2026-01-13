"""
Use web search to build personas of real or fictional people
"""

import typing as T
import uuid

from pydantic import BaseModel, Field
from pydantic_ai import Agent, WebSearchTool

from society.datatypes import CharacterOutput


async def generate_character(
    prompt: str,
    model: str | None = None,
) -> CharacterOutput:
    """
    Prompt to character
    """
    instructions = """
You are given a prompt that describes a person (real or fictional).

Your task is to deep research all information you can find about the person and build a
detailed profile of them. Search many web links and dig for information.

This profile should include as much detail as possible that conveys
their demographic, personality, writing and conversation style, decision making, interests,
and anything else you can find.

This will be context for an LLM that then simulates that person, so the more direct quotes
and transcripts of the person's writing/talking you can find and include, the better.
The context can be LONG and include many pages of content.

Rules:
 - write in first person from their POV
 - write in their style, using their voice and tone
 - write in their native language / dialect

IMPORTANT: Spend a lot of time researching, do a lot of web search and gather citations.
The more context and detail, the better. This is a deep research task.
""".strip()

    class CharacterGenModelOutput(BaseModel):
        name: T.Annotated[
            str, "Your name. Do not add parenthetical extras"
        ]

        emoji: T.Annotated[
            str,
            "a single emoji uniquely representing you",
            Field(..., min_length=1, max_length=1),
        ]

        birth_year: T.Annotated[
            int | None, "Your birth year"
        ]

        gender: T.Literal["male", "female", "unknown", "other"]
        occupation: str
        location: str
        bio: T.Annotated[str, "Background on your life and character"]
        personality: T.Annotated[
            str, "How you behave and think"
        ]
        context: T.Annotated[
            str,
            """
            Dump any and all other context about the person here.

            This can be extremely verbose, multiple pages of info.
            Anytime you have examples of their writing (website, blog, social posts, interview, etc)
            or descriptions of their activities, or any other relevant info, dump it here.

            Include all direct quotes you find, up to multiple pages of content.

            Do NOT be worried about making it too long.
            """,
        ]

        confidence: T.Annotated[
            int,
            """
        Confidence in the accuracy of the information, 0-100.

        100 means you are extremely confident with multiple cross-referenced sources
        50 means you have some info but not confident in it 
        0 means you have no accurate info
        """,
        ]

    if model is None:
        model = "google-gla:gemini-3-flash-preview"

    agent: Agent[None, CharacterGenModelOutput] = Agent(
        model=model,
        output_type=CharacterGenModelOutput,
        builtin_tools=[WebSearchTool(search_context_size="high")],
        instructions=instructions,
        retries=3,
        name="character-generate",
    )

    result = await agent.run(prompt)
    return CharacterOutput(
        uuid=uuid.uuid4(),
        **result.output.model_dump(),
    )


class SplitGroupPromptOutput(BaseModel):
    num_people: T.Annotated[int, "Number of people to generate"]
    prompts: T.Annotated[list[str], "A prompt to generate each specific person"]
    malformed_prompt: T.Annotated[
        bool, "Whether the prompt is really unclear or malforned and should be rejected"
    ]


async def split_group_prompt(
    prompt: str,
    model: str | None = None,
) -> SplitGroupPromptOutput:
    """
    Take a prompt that generates N people and split it into N prompts for each person
    """
    instructions = """
You are given a prompt that describes one or more people (real or fictional).

This prompt will be used downstream to generate a profile for each person implied
by this prompt.

Your task is to decide how many people this prompt should generate, and then generate the
prompt for each individual person.

CRITICAL RULES:
1. Each output prompt MUST identify a SPECIFIC, UNIQUE person by name
2. If the input is vague like "six famous directors" or "three scientists", you MUST use
   web search to identify specific real people and output their actual names
3. NEVER output generic prompts like "a famous director" - always output specific names
4. Each person must be different - no duplicates
5. Don't just output their name unless they are very famous, add context from the original prompt

Examples:
- Input: "the cast of Friends" -> Output: ["Jennifer Aniston of Friends", ...]
- Input: "three famous physicists" -> Output: ["Albert Einstein (scientist)", "Richard Feynman (physicist)", ...]
- Input: "Elon Musk" -> Output: ["Elon Musk (ceo of tesla)"]

If the prompt is referring to one specific person, simply output the same prompt as-is.
""".strip()

    if model is None:
        model = "google-gla:gemini-3-flash-preview"

    agent: Agent[None, SplitGroupPromptOutput] = Agent(
        model=model,
        output_type=SplitGroupPromptOutput,
        builtin_tools=[WebSearchTool(search_context_size="high")],
        instructions=instructions,
        name="character-split-group-prompt",
    )

    result = await agent.run(prompt)
    assert result.output.num_people == len(result.output.prompts)
    return result.output
