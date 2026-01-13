import asyncio
import logging
import typing as T
import uuid

from pydantic_ai import Agent, ModelRetry, RunContext, WebSearchTool

from society.datatypes import Answer, Channel, Message, Vote
from society.deps import Deps

logger = logging.getLogger(__name__)


async def send_message(
    ctx: RunContext[Deps],
    channel: str,
    text: str,
) -> Message:
    """
    Send a message to a channel

    This is your primary way to communicate with the team and share information
    """
    t = ctx.deps.current_time_s()
    try:
        message = ctx.deps.chat_client.send_message(channel, text, t=t)
    except ValueError as e:
        raise ModelRetry(f"Failed to send message: {e}")

    logger.info(f"#{channel}\n{_log_prefix(ctx, t=t)}\n{text}\n")

    return message


async def wait(
    ctx: RunContext[Deps],
) -> None:
    """
    Wait for 10 seconds

    This could make sense if:
     - you are waiting for someone else's reply
     - nothing relevant has happened since you last posted
     - you have no opinion on the current discussion
    """
    time_s = 10.0
    logger.debug(f"{_log_prefix(ctx)}\nWaiting for {time_s}s\n")
    await asyncio.sleep(time_s)


async def propose_answer(
    ctx: RunContext[Deps],
    text: str,
) -> Answer:
    """
    Propose an answer to the task at hand

    It must be a specific answer, not a general statement
    Keep it short, the answer is not meant to give the what, not the how or why

    Proposing an answer automatically votes for it
    """
    if ctx.deps.current_time_s() < ctx.deps.voting_start_s:
        raise ModelRetry(
            f"You cannot propose an answer until {ctx.deps.voting_start_s}s"
        )

    answer = Answer(
        id=uuid.uuid4(),
        person_id=ctx.deps.character_id,
        text=text,
    )
    logger.info(f"{_log_prefix(ctx)}\nProposed answer: {answer.text}\n")

    ctx.deps.shared_state.answers.append(answer)

    # Automatically vote for it
    await vote_on_answer(ctx, answer.id, "yes")

    return answer


async def vote_on_answer(
    ctx: RunContext[Deps],
    answer_id: uuid.UUID,
    vote: T.Literal["yes", "no", "unsure"],
) -> None:
    """
    Vote on an answer to the task at hand

    You can have one vote for every proposed answer, and you can change
    your vote by calling this again
    """
    # Check if this person has already voted on this answer
    existing_vote = next(
        (
            v
            for v in ctx.deps.shared_state.votes
            if v.answer_id == answer_id and v.person_id == ctx.deps.character_id
        ),
        None,
    )
    if existing_vote is not None:
        # Update existing vote
        existing_vote.vote = vote
        vote_obj = existing_vote
    else:
        # Create new vote
        vote_obj = Vote(
            id=uuid.uuid4(),
            answer_id=answer_id,
            person_id=ctx.deps.character_id,
            vote=vote,
        )
        ctx.deps.shared_state.votes.append(vote_obj)

    # Fetch answer object
    answer_obj = next(
        (a for a in ctx.deps.shared_state.answers if a.id == answer_id), None
    )
    if answer_obj is None:
        raise ModelRetry(f"Answer {answer_id} not found")

    # Count votes for this answer
    answer_votes = [v for v in ctx.deps.shared_state.votes if v.answer_id == answer_id]
    vote_counts: dict[str, int] = {}
    for v in answer_votes:
        vote_counts[v.vote] = vote_counts.get(v.vote, 0) + 1
    counts_str = ", ".join(
        f"{count} {vote_type}" for vote_type, count in vote_counts.items()
    )

    logger.info(
        f"{_log_prefix(ctx)}\nVoted {vote} on answer: {answer_obj.text}\nTally: {counts_str}\n"
    )

    # Count the number of non-ceo people
    non_ceo_people = [p for p in ctx.deps.chat_client.list_people() if p.role != "ceo"]

    # If the vote is unanimous, we can finish the job
    if "yes" in vote_counts and vote_counts["yes"] == len(non_ceo_people):
        logger.info(f"**** Unanimous answer: {answer_obj.text}")
        ctx.deps.shared_state.final_answer = answer_obj


def _log_prefix(ctx: RunContext[Deps], t: float | None = None) -> str:
    if t is None:
        t = ctx.deps.current_time_s()
    return f"[{t:.1f}s] {ctx.deps.character.name}"


async def create_channel(
    ctx: RunContext[Deps],
    name: str,
    description: str,
) -> Channel:
    """
    Create a new channel and join it
    """
    try:
        channel = ctx.deps.chat_client.create_channel(
            name=name,
            description=description,
            person_ids=[ctx.deps.character_id],
        )
    except ValueError as e:
        raise ModelRetry(f"Failed to create channel: {e}")

    logger.info(f"{_log_prefix(ctx)}\nCreated channel #{name}: {description}\n")
    return channel


async def join_channel(
    ctx: RunContext[Deps],
    channel: str,
) -> None:
    """
    Join an existing channel to participate in its discussion
    """
    try:
        ctx.deps.chat_client.add_person_to_channel(ctx.deps.character_id, channel)
    except ValueError as e:
        raise ModelRetry(f"Failed to join channel: {e}")

    logger.info(f"{_log_prefix(ctx)}\nJoined #{channel}\n")


async def read_channel(
    ctx: RunContext[Deps],
    channel: str,
) -> str:
    """
    Read messages from a channel you're a member of
    """
    try:
        transcript = ctx.deps.chat_client.format_channel(channel)
    except ValueError as e:
        raise ModelRetry(f"Failed to read channel: {e}")

    logger.debug(f"{_log_prefix(ctx)}\nRead #{channel}\n")
    return transcript


async def leave_channel(
    ctx: RunContext[Deps],
    channel: str,
) -> None:
    """
    Leave a channel you're a member of
    """
    ctx.deps.chat_client.remove_person_from_channel(ctx.deps.character_id, channel)
    logger.info(f"{_log_prefix(ctx)}\nLeft #{channel}\n")


async def web_search(
    ctx: RunContext[Deps],
    query: str,
) -> str:
    """
    Search the web for information

    Use this to look up facts, current events, or any information you need.
    """
    logger.info(f"{_log_prefix(ctx)}\nWeb search: {query}\n")

    agent = Agent(
        model="google-gla:gemini-3-flash-preview",
        output_type=str,
        builtin_tools=[WebSearchTool(search_context_size="medium")],
        instructions="Answer the user's question using web search",
        name="web-search",
    )

    result = await agent.run(query)

    logger.debug(f"{_log_prefix(ctx)}\nWeb search result: {result.output[:200]}...\n")
    return result.output


OUTPUT_TOOLS: list[T.Callable] = []

TOOLS: list[T.Callable] = [
    send_message,
    create_channel,
    join_channel,
    read_channel,
    leave_channel,
    wait,
    web_search,
    propose_answer,
    vote_on_answer,
]
