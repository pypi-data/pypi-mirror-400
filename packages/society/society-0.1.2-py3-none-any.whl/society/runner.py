"""
Primary run loop for a society simulation
"""

import asyncio
import datetime
import json
import logging
import re
import typing as T
import uuid
from pathlib import Path

import numpy as np
from pydantic_ai import Agent, FunctionToolCallEvent, ModelMessage, UsageLimits
from pydantic_ai.exceptions import ModelHTTPError

from society import agent_util, data, instructions, tools
from society.chat_client import ChatClient
from society.datatypes import (
    AgentEvent,
    Channel,
    CharacterOutput,
    Person,
    SharedState,
    SimulationMode,
)
from society.deps import Deps

logging.basicConfig(level=logging.INFO, format="%(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def run(
    characters: list[CharacterOutput],
    mode: SimulationMode = SimulationMode.TASK,
    task: str | None = None,
    run_dir: Path | None = None,
    voting_start_s: float = 120.0,
    duration_s: float | None = None,
) -> Path:
    """
    Run a simulation with characters.

    Args:
        characters: List of characters to participate
        mode: TASK (solve a problem) or CASUAL (hang out and chat)
        task: The task to solve (required for TASK mode, optional prompt for CASUAL)
        run_dir: Output directory for logs and data
        voting_start_s: Minimum time before voting can begin (task mode only)
        duration_s: Max duration in seconds (casual mode only, None = unlimited)

    Returns the directory in which outputs are stored
    """
    if mode == SimulationMode.TASK and not task:
        raise ValueError("task is required for TASK mode")
    if run_dir is None:
        run_dir = data.create_run_dir()
    else:
        run_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Run directory: {run_dir}")

    # Tee DEBUG logs to file in run directory
    file_handler = logging.FileHandler(run_dir / "debug.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
    )
    logging.getLogger().addHandler(file_handler)
    logging.getLogger().setLevel(logging.DEBUG)
    # Keep console at INFO level (only file gets DEBUG)
    for handler in logging.getLogger().handlers:
        if isinstance(handler, logging.StreamHandler) and not isinstance(
            handler, logging.FileHandler
        ):
            handler.setLevel(logging.INFO)
    events_path = run_dir / "events.jsonl"

    # Save characters list
    characters_path = run_dir / "characters.json"
    characters_json = [c.model_dump(mode="json") for c in characters]
    characters_path.write_text(json.dumps(characters_json, indent=2))

    # Initialize chat client
    chat_dir = run_dir / "chat"
    chat_client = ChatClient(chat_dir, user_id=None)

    # Add characters to chat
    for character in characters:
        chat_client.add_person(
            Person(
                id=character.uuid,
                name=character.name,
                bio=character.bio,
                role="member",
            )
        )

    # CEO posts the task (task mode) or Host posts the prompt (casual mode)
    ceo: Person | None = None
    if mode == SimulationMode.TASK:
        ceo = Person(
            id=uuid.uuid4(),
            name="CEO",
            bio="The CEO who assigns tasks to the team",
            role="ceo",
        )
        chat_client.add_person(ceo)
    elif task:
        # Casual mode with optional prompt - create a Host to post it
        ceo = Person(
            id=uuid.uuid4(),
            name="Host",
            bio="The host who sets the topic for discussion",
            role="ceo",
        )
        chat_client.add_person(ceo)

    # Create channels
    channels = _create_default_channels(chat_client.list_people())
    for channel in channels:
        chat_client.create_channel(
            name=channel.name,
            description=channel.description,
            person_ids=channel.person_ids,
        )

    shared_state = SharedState()
    start_timestamp = datetime.datetime.now()

    # Open output files
    events_file = events_path.open("a")

    # Build agents and deps (each agent gets their own ChatClient)
    agents: list[Agent[Deps]] = []
    deps_list: list[Deps] = []
    for character in characters:
        agent = agent_util.create_agent(
            instructions=instructions.INSTRUCTION_FUNCS,
            tools=tools.TOOLS,
            output_tools=tools.OUTPUT_TOOLS,
            output_type=str,
        )
        deps = Deps(
            character=character,
            chat_client=ChatClient(
                chat_dir,
                user_id=character.uuid,
            ),
            start_timestamp=start_timestamp,
            simulation_mode=mode,
            voting_start_s=voting_start_s,
            shared_state=shared_state,
        )
        agents.append(agent)
        deps_list.append(deps)

    # Post CEO task (task mode) or Host prompt (casual mode with prompt)
    if ceo is not None and task is not None:
        starter_client = ChatClient(chat_dir, user_id=ceo.id)
        starter_client.send_message("general", task, t=0.1)

    def emit(event: AgentEvent) -> None:
        events_file.write(event.model_dump_json() + "\n")
        events_file.flush()

    async def run_agent(agent: Agent[Deps], deps: Deps) -> None:
        name = deps.character.name
        logger.info(f"[{name}] Agent starting...")
        await asyncio.sleep(np.random.uniform(0, 15))
        try:
            turn_count = 0
            async for event in stream_agent_events(deps, agent):
                emit(event)
                if event.kind == "agent_run_result":
                    turn_count += 1
                    logger.debug(f"[{name}] Completed turn {turn_count} at t={event.time_s:.1f}s")
            logger.info(f"[{name}] Agent finished normally after {turn_count} turns")
        except Exception as e:
            logger.error(f"[{name}] Agent crashed with error: {e}", exc_info=True)
            emit(AgentEvent(
                kind="agent_error",
                person_name=name,
                time_s=deps.current_time_s(),
                data={"error": str(e), "type": type(e).__name__},
            ))
            raise

    try:
        agents_task = asyncio.gather(*[run_agent(a, d) for a, d in zip(agents, deps_list)])
        if duration_s is not None:
            try:
                await asyncio.wait_for(agents_task, timeout=duration_s)
            except asyncio.TimeoutError:
                logger.info(f"Simulation timed out after {duration_s}s")
        else:
            await agents_task
    finally:
        # Emit final state
        final = deps_list[0].shared_state.final_answer
        emit(
            AgentEvent(
                kind="simulation_end",
                person_name="system",
                time_s=deps_list[0].current_time_s(),
                data={"final_answer": final.text if final else None},
            )
        )
        events_file.close()
        logging.getLogger().removeHandler(file_handler)
        file_handler.close()

    return run_dir


async def continue_run(
    run_dir: Path,
    message: str,
    duration_s: float = 60.0,
) -> None:
    """
    Continue a previous simulation run with a new message.

    Args:
        run_dir: The directory of the previous run
        message: New message to post to #general
        duration_s: How long to run the simulation for (seconds)
    """
    logger.info(f"Continuing run: {run_dir}")

    # Load characters
    characters_path = run_dir / "characters.json"
    if not characters_path.exists():
        raise ValueError(f"No characters.json found in {run_dir}")
    characters_data = json.loads(characters_path.read_text())
    characters = [CharacterOutput.model_validate(c) for c in characters_data]

    # Set up logging
    file_handler = logging.FileHandler(run_dir / "debug.log", mode="a")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
    )
    logging.getLogger().addHandler(file_handler)

    # Get chat client and find the last message time
    chat_dir = run_dir / "chat"
    chat_client = ChatClient(chat_dir, user_id=None)
    all_messages = chat_client.get_all_messages()
    last_time = max((m.t for m in all_messages), default=0.0)

    # Calculate start_timestamp so current_time_s picks up from last_time
    start_timestamp = datetime.datetime.now() - datetime.timedelta(seconds=last_time)

    # Find or create a User person to post the new message
    people = chat_client.list_people()
    user_person = next((p for p in people if p.name == "User"), None)
    if user_person is None:
        user_person = Person(
            id=uuid.uuid4(),
            name="User",
            bio="A human user continuing the conversation",
            role="ceo",
        )
        chat_client.add_person(user_person)
        # Add user to general channel
        general = next((c for c in chat_client.list_channels() if c.name == "general"), None)
        if general:
            chat_client.add_person_to_channel(user_person.id, "general")

    # Post the new message
    user_client = ChatClient(chat_dir, user_id=user_person.id)
    new_time = last_time + 1.0
    user_client.send_message("general", message, t=new_time)
    logger.info(f"[User] Posted message at t={new_time:.1f}s")

    # Determine simulation mode (default to casual for continuations)
    mode = SimulationMode.CASUAL

    # Open events file for appending
    events_path = run_dir / "events.jsonl"
    events_file = events_path.open("a")

    shared_state = SharedState()

    # Build agents and deps
    agents: list[Agent[Deps]] = []
    deps_list: list[Deps] = []
    for character in characters:
        agent = agent_util.create_agent(
            instructions=instructions.INSTRUCTION_FUNCS,
            tools=tools.TOOLS,
            output_tools=tools.OUTPUT_TOOLS,
            output_type=str,
        )
        deps = Deps(
            character=character,
            chat_client=ChatClient(chat_dir, user_id=character.uuid),
            start_timestamp=start_timestamp,
            simulation_mode=mode,
            voting_start_s=999999,  # Disable voting for continuations
            shared_state=shared_state,
        )
        agents.append(agent)
        deps_list.append(deps)

    def emit(event: AgentEvent) -> None:
        events_file.write(event.model_dump_json() + "\n")
        events_file.flush()

    async def run_agent(agent: Agent[Deps], deps: Deps) -> None:
        await asyncio.sleep(np.random.uniform(0, 5))
        async for event in stream_agent_events(deps, agent):
            emit(event)

    # Run agents with timeout
    try:
        await asyncio.wait_for(
            asyncio.gather(*[run_agent(a, d) for a, d in zip(agents, deps_list)]),
            timeout=duration_s,
        )
    except asyncio.TimeoutError:
        logger.info(f"Simulation timed out after {duration_s}s")
    finally:
        emit(
            AgentEvent(
                kind="simulation_continue_end",
                person_name="system",
                time_s=deps_list[0].current_time_s() if deps_list else 0,
                data={"duration_s": duration_s},
            )
        )
        events_file.close()
        logging.getLogger().removeHandler(file_handler)
        file_handler.close()


def _parse_retry_delay(error: ModelHTTPError) -> float | None:
    """Parse retry delay from rate limit error message."""
    body_str = str(error.body) if error.body else ""
    # Try to find "retry in X.XXs" or "retryDelay": "XXs"
    match = re.search(r"retry in (\d+(?:\.\d+)?)", body_str, re.IGNORECASE)
    if match:
        return float(match.group(1))
    match = re.search(r'"retryDelay":\s*"(\d+)s?"', body_str)
    if match:
        return float(match.group(1))
    return None


async def _run_with_retry(
    agent: Agent[Deps],
    turn_prompt: str,
    deps: Deps,
    usage_limits: UsageLimits,
    message_history: list[ModelMessage],
) -> T.AsyncGenerator[T.Any, None]:
    """Run agent with retry logic for rate limits and transient errors."""
    max_retries = 10
    base_delay = 5.0
    name = deps.character.name

    for attempt in range(max_retries):
        try:
            async for event in agent.run_stream_events(
                turn_prompt,
                deps=deps,
                usage_limits=usage_limits,
                message_history=message_history,
            ):
                yield event
            return  # Success, exit retry loop
        except ModelHTTPError as e:
            # Retry on rate limits (429) and server errors (5xx)
            is_retryable = e.status_code == 429 or (500 <= e.status_code < 600)
            if not is_retryable:
                logger.error(f"[{name}] Non-retryable HTTP error {e.status_code}: {e}")
                raise

            # Parse retry delay or use exponential backoff
            delay = _parse_retry_delay(e) if e.status_code == 429 else None
            if delay is None:
                delay = base_delay * (2 ** attempt)

            # Add some jitter
            delay = delay + np.random.uniform(0, 2)

            error_type = "Rate limited" if e.status_code == 429 else f"Server error {e.status_code}"
            logger.warning(
                f"[{name}] {error_type} (attempt {attempt + 1}/{max_retries}), "
                f"waiting {delay:.1f}s before retry..."
            )
            await asyncio.sleep(delay)
        except (ConnectionError, TimeoutError, OSError) as e:
            # Retry on connection errors
            delay = base_delay * (2 ** attempt) + np.random.uniform(0, 2)
            logger.warning(
                f"[{name}] Connection error: {e} (attempt {attempt + 1}/{max_retries}), "
                f"waiting {delay:.1f}s before retry..."
            )
            await asyncio.sleep(delay)

    raise RuntimeError(f"Max retries ({max_retries}) exceeded")


async def stream_agent_events(
    deps: Deps,
    agent: Agent[Deps],
) -> T.AsyncGenerator[AgentEvent, None]:
    """Stream agent events. Yields AgentEvent objects."""
    tool_calls: list[FunctionToolCallEvent] = []
    message_history: list[ModelMessage] = []
    usage_limits = UsageLimits(request_limit=1_000, total_tokens_limit=10_000_000)

    while True:
        if deps.simulation_mode == SimulationMode.TASK:
            turn_prompt = """
Take your next turn:
 - check the chat history above for new messages
 - continue research and reply in the chat
 - follow up on your own previous plans
 - call 'wait' if you need responses from others
 - output 'done'
""".strip()
        else:
            turn_prompt = """
Take your next turn in the chat:
 - check what others have said and respond naturally
 - share something about yourself or ask others questions
 - keep the conversation flowing - be curious and engaged
 - call 'wait' if you don't feel like responding right now
""".strip()

        async for event in _run_with_retry(
            agent, turn_prompt, deps, usage_limits, message_history
        ):
            if deps.shared_state.final_answer is not None:
                logger.info(
                    f"[{deps.character.name}] Unanimous answer detected, ending"
                )
                return

            time_s = deps.current_time_s()

            if event.event_kind == "function_tool_call":
                tool_calls.append(T.cast(FunctionToolCallEvent, event))

            elif event.event_kind == "function_tool_result":
                tool_call_event = next(
                    (tc for tc in tool_calls if tc.tool_call_id == event.tool_call_id),
                    None,
                )
                assert tool_call_event is not None
                tool_return_part = event.result
                if tool_return_part.part_kind == "retry-prompt":
                    continue

                # Serialize result if it's a Pydantic model
                result = tool_return_part.content
                if hasattr(result, "model_dump"):
                    result = result.model_dump(mode="json")
                elif (
                    isinstance(result, list)
                    and result
                    and hasattr(result[0], "model_dump")
                ):
                    result = [r.model_dump(mode="json") for r in result]

                yield AgentEvent(
                    kind="tool_result",
                    person_name=deps.character.name,
                    time_s=time_s,
                    data={
                        "tool_name": tool_call_event.part.tool_name,
                        "args": tool_call_event.part.args_as_dict(),
                        "result": result,
                    },
                )

            elif event.event_kind == "agent_run_result":
                message_history = event.result.all_messages()
                yield AgentEvent(
                    kind="agent_run_result",
                    person_name=deps.character.name,
                    time_s=time_s,
                    data={"output": event.result.output},
                )

            elif event.event_kind == "final_result":
                yield AgentEvent(
                    kind="final_result",
                    person_name=deps.character.name,
                    time_s=time_s,
                    data={"tool_name": event.tool_name},
                )

            elif event.event_kind == "builtin_tool_call":
                yield AgentEvent(
                    kind="builtin_tool_call",
                    person_name=deps.character.name,
                    time_s=time_s,
                    data={
                        "tool_name": event.part.tool_name,
                        "args": event.part.args_as_dict(),
                    },
                )

            elif event.event_kind in (
                "builtin_tool_result",
                "part_delta",
                "part_start",
                "part_end",
            ):
                continue

            else:
                raise NotImplementedError(
                    f"Event kind {event.event_kind} not implemented"
                )


def _create_default_channels(
    people: list[Person],
) -> list[Channel]:
    channels: list[Channel] = []

    channels.append(
        Channel(
            id=uuid.uuid4(),
            name="general",
            description="Group chat channel with everyone",
            person_ids=[person.id for person in people],
        )
    )

    for person in people:
        channels.append(
            Channel(
                id=uuid.uuid4(),
                name=ChatClient.slugify(person.name),
                description=f"Private journal for {person.name} to take notes",
                person_ids=[person.id],
            )
        )

    return channels
