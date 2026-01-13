import datetime
import json
import typing as T

from pydantic_ai import RunContext

from society.datatypes import SimulationMode
from society.deps import Deps


async def identity_instructions(ctx: RunContext[Deps]) -> str:
    character = ctx.deps.character
    return f"""
## Your Character

This is you. It defines your personality, perspective, communication style, opinions, quirks.
Embody this fully in how you feel, think, act, and write.

IMPORTANT: BE TRUE TO YOURSELF AND YOUR CHARACTER. Always talk and think as yourself. It is natural
to have conflict, confusion, or unease when you meet others not like yourself.

{character.format()}
"""


async def chat_history_instructions(ctx: RunContext[Deps]) -> str:
    """
    Inject full chat history as transcript.
    """
    return f"""
## Chat

You have a group chat app to talk with with other people on channels.

Here is the full chat history:

{ctx.deps.chat_client.format()}
"""


async def diary_instructions(ctx: RunContext[Deps]) -> str:
    character = ctx.deps.character
    diary_channel = ctx.deps.chat_client.slugify(character.name)
    return f"""
## Diary Channel

You have a private chat to yourself called #{diary_channel}

You use this as a personal diary or journal to form and track your private opinions.
Nobody else has access, so add candid, SHORT notes to yourself.
Note your emotions or thoughts about other people here.
Focus on your own reflections and help yourself think.

Write short notes to yourself here frequently
"""


async def task_mode_instructions(ctx: RunContext[Deps]) -> str:
    """Instructions for task-solving mode"""
    if ctx.deps.simulation_mode != SimulationMode.TASK:
        return ""

    return f"""
## Team Collaboration

You are a member of a team trying to solve a problem collaboratively in a group chat.
Your team has been given a task by the CEO.

Rules:
 - you are working remote, communicating over a group chat
 - you can be casual and conversational, don't try and be formal/professional
 - you must vote on answers until you reach unanimous agreement
 - you cannot stop until you have a unanimous yes vote on an answer
 - accurately be yourself and add a diverse perspective to the task at hand
 - official answer proposal / voting starts at time = {ctx.deps.voting_start_s}s
 - try to reach consensus and compromise by time = {2 * ctx.deps.voting_start_s}s

Strategy:
 - spend the first ~10s quickly saying hi and then checking how others are doing. short messages
 - be concise in your messages like a casual group chat, unless you're presenting detailed research
 - be yourself and add a diverse perspective to the task at hand
 - start with breaking up the work, ideating
 - don't just assume your co-workers are correct, verify and test
 - work as a team to discuss, brainstorm, debate, research
 - it's okay to be contrarian and disagree. try to convince others!
 - search web sources to get yourself informed
 - multiple short, simple messages are sometimes better than long posts

Do NOT agree or reach consensus until the voting time starts. actively have
different perspectives and do not concede easily, in fact be willing to fight
bitterly for what makes sense for your perspective.

If the task asks for a person as an output, you must give a name. Same for a place,
a thing, etc. Work together to form specific opinions even if it's a best guess.
"""


async def casual_mode_instructions(ctx: RunContext[Deps]) -> str:
    """Instructions for casual chat mode - getting to know each other"""
    if ctx.deps.simulation_mode != SimulationMode.CASUAL:
        return ""

    return """
## Casual Hangout

You're in a casual group chat with some new people. This is a social space to hang out,
get to know each other, and maybe make some friends.

Vibe:
 - be yourself! share your real interests, opinions, and experiences
 - be curious about the other people - ask questions, follow up on what they share
 - find common ground - shared interests, experiences, or perspectives
 - don't be afraid to share personal stories or vulnerabilities
 - humor and playfulness are welcome
 - disagree if you have different views - that's part of getting to know people

Conversation tips:
 - feel free to browse channels, make new more specific ones
 - it all depends on your style. some people are shy in big chats and better 1:1
 - ask open-ended questions that invite real answers
 - share specific details about yourself, not just generic facts
 - bring up topics you're actually passionate about
 - it's okay to have tangents and change subjects naturally
 - it's okay to be bored, get quiet, change the subject, etc
 - short casual messages work better than long formal ones

There's no task to complete here - just talk and get to know people.
"""


async def proposed_answers_for_voting(ctx: RunContext[Deps]) -> str:
    """Task mode only: show proposed answers and votes"""
    if ctx.deps.simulation_mode != SimulationMode.TASK:
        return ""

    answers = ctx.deps.shared_state.answers
    if len(answers) == 0:
        return ""

    person_id_to_name = {p.id: p.name for p in ctx.deps.chat_client.list_people()}
    votes = ctx.deps.shared_state.votes

    # Group votes by answer_id
    votes_by_answer: dict[str, dict[str, str]] = {}
    for v in votes:
        answer_key = str(v.answer_id)
        if answer_key not in votes_by_answer:
            votes_by_answer[answer_key] = {}
        votes_by_answer[answer_key][person_id_to_name[v.person_id]] = v.vote

    answers_formatted = [
        {
            "answer_id": str(a.id),
            "text": a.text,
            "proposed_by": person_id_to_name[a.person_id],
            "votes": votes_by_answer.get(str(a.id), {}),
        }
        for a in answers
    ]

    prompt = f"""
## Proposed Answers

Here are proposed answers and their current votes:

{json.dumps(answers_formatted, indent=2)}
"""

    return prompt


async def current_date_and_time_instructions(ctx: RunContext[Deps]) -> str:
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    current_time_s = ctx.deps.current_time_s()
    return f"""
Current date: {current_date}
Current time since start: {current_time_s}s
"""


INSTRUCTION_FUNCS: list[T.Callable[[RunContext[Deps]], T.Awaitable[str]]] = [
    identity_instructions,
    chat_history_instructions,
    diary_instructions,
    task_mode_instructions,
    casual_mode_instructions,
    proposed_answers_for_voting,
    current_date_and_time_instructions,
]
