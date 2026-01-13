"""
FastAPI backend for the Society web UI
"""

import asyncio
import io
import json
import os
import signal
import subprocess
import typing as T
import zipfile
from pathlib import Path

from fastapi import Depends, FastAPI, File, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from society import data
from society.characters import generate_character, split_group_prompt
from society.chat_client import ChatClient
from society.datatypes import CharacterOutput

app = FastAPI()


def use_api_key(x_api_key: T.Annotated[str | None, Header()] = None) -> None:
    """Dependency that sets GOOGLE_API_KEY and SOCIETY_DATA_DIR from request header."""
    if x_api_key:
        os.environ["GOOGLE_API_KEY"] = x_api_key
        os.environ["SOCIETY_DATA_DIR"] = str(data.get_scoped_data_dir(x_api_key))


app.add_middleware(
    T.cast(T.Any, CORSMiddleware),
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/config")
def get_config() -> dict[str, T.Any]:
    """Get server configuration."""
    return {
        "has_api_key": bool(
            os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        ),
    }


# --- Models ---


class RunSummary(BaseModel):
    name: str
    task: str
    people: list[str]


class RunDetail(BaseModel):
    name: str
    task: str
    characters: list[dict[str, T.Any]]
    people: list[dict[str, T.Any]]
    channels: list[dict[str, T.Any]]
    messages: list[dict[str, T.Any]]
    events: list[dict[str, T.Any]]
    final_answer: str | None


class CreateCharacterRequest(BaseModel):
    prompt: str


class SplitPromptsResponse(BaseModel):
    prompts: list[str]


class GenerateCharacterRequest(BaseModel):
    prompt: str


class StartRunRequest(BaseModel):
    characters: list[str]
    mode: str = "task"
    task: str | None = None  # Required for task mode, optional prompt for casual mode
    voting_start: float = 120.0  # Seconds before voting can begin (task mode only)
    duration: float | None = None  # Max duration in seconds (casual mode only)


# --- Routes ---


@app.get("/api/runs", dependencies=[Depends(use_api_key)])
def list_runs() -> list[RunSummary]:
    """List recent runs"""
    runs: list[RunSummary] = []
    for run_path in data.list_runs()[:50]:
        chat = ChatClient(run_path / "chat", user_id=None)
        messages = chat.get_all_messages()
        task = messages[0].text[:100] + "..." if messages else ""
        people = [p.name for p in chat.list_people() if p.role != "ceo"]
        runs.append(RunSummary(name=run_path.name, task=task, people=people))
    return runs


@app.get("/api/runs/{run_name}", dependencies=[Depends(use_api_key)])
def get_run(run_name: str) -> RunDetail:
    """Get run details"""
    run_path = data.get_data_dir() / "runs" / run_name
    if not run_path.exists():
        raise HTTPException(404, "Run not found")

    chat = ChatClient(run_path / "chat", user_id=None)

    # Load characters.json
    characters: list[dict[str, T.Any]] = []
    chars_path = run_path / "characters.json"
    if chars_path.exists():
        characters = json.loads(chars_path.read_text())

    # Load events.jsonl
    events: list[dict[str, T.Any]] = []
    events_path = run_path / "events.jsonl"
    if events_path.exists():
        for line in events_path.read_text().strip().split("\n"):
            if line:
                events.append(json.loads(line))

    # Get final answer from events
    final_answer = None
    for e in events:
        if e.get("kind") == "simulation_end" and e.get("data", {}).get("final_answer"):
            final_answer = e["data"]["final_answer"]

    messages = chat.get_all_messages()
    return RunDetail(
        name=run_name,
        task=messages[0].text if messages else "",
        characters=[
            {
                "uuid": str(c.get("uuid")),
                "name": c.get("name"),
                "emoji": c.get("emoji", "👤"),
                "bio": c.get("bio", ""),
                "occupation": c.get("occupation", ""),
            }
            for c in characters
        ],
        people=[p.model_dump(mode="json") for p in chat.list_people()],
        channels=[c.model_dump(mode="json") for c in chat.list_channels()],
        messages=[m.model_dump(mode="json") for m in messages],
        events=events,
        final_answer=final_answer,
    )


@app.get("/api/runs/{run_name}/status", dependencies=[Depends(use_api_key)])
def get_run_status(run_name: str) -> dict[str, T.Any]:
    """Get detailed status of a run for debugging"""
    run_path = data.get_data_dir() / "runs" / run_name
    if not run_path.exists():
        raise HTTPException(404, "Run not found")

    # Check if process is still running
    pid_file = run_path / "pid"
    is_running = False
    pid = None
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            os.kill(pid, 0)  # Check if process exists
            is_running = True
        except (ProcessLookupError, ValueError):
            is_running = False

    # Parse events to get per-agent status
    events: list[dict[str, T.Any]] = []
    events_path = run_path / "events.jsonl"
    if events_path.exists():
        for line in events_path.read_text().strip().split("\n"):
            if line:
                events.append(json.loads(line))

    # Group events by agent
    agent_status: dict[str, dict[str, T.Any]] = {}
    for e in events:
        name = e.get("person_name", "unknown")
        if name == "system":
            continue
        if name not in agent_status:
            agent_status[name] = {
                "event_count": 0,
                "last_event_time": 0,
                "last_event_kind": None,
                "errors": [],
            }
        agent_status[name]["event_count"] += 1
        agent_status[name]["last_event_time"] = e.get("time_s", 0)
        agent_status[name]["last_event_kind"] = e.get("kind")
        if e.get("kind") == "agent_error":
            agent_status[name]["errors"].append(e.get("data", {}))

    # Get last few lines of debug log
    debug_log = run_path / "debug.log"
    recent_logs: list[str] = []
    if debug_log.exists():
        lines = debug_log.read_text().split("\n")
        recent_logs = lines[-50:]  # Last 50 lines

    return {
        "run_name": run_name,
        "is_running": is_running,
        "pid": pid,
        "total_events": len(events),
        "agent_status": agent_status,
        "recent_logs": recent_logs,
    }


@app.get("/api/characters", dependencies=[Depends(use_api_key)])
def list_characters() -> list[CharacterOutput]:
    """List available characters"""
    return [
        CharacterOutput.model_validate_json(path.read_text())
        for path in data.list_characters()
    ]


@app.get("/api/characters/{char_id}", dependencies=[Depends(use_api_key)])
def get_character(char_id: str) -> CharacterOutput:
    """Get a character by UUID"""
    for path in data.list_characters():
        char = CharacterOutput.model_validate_json(path.read_text())
        if str(char.uuid) == char_id:
            return char
    raise HTTPException(404, "Character not found")


@app.post("/api/characters", dependencies=[Depends(use_api_key)])
async def create_character(req: CreateCharacterRequest) -> list[CharacterOutput]:
    """Create one or more characters via AI research (legacy endpoint)"""
    if not req.prompt.strip():
        raise HTTPException(400, "prompt required")

    # Split prompt into individual character prompts
    split = await split_group_prompt(req.prompt)
    if split.malformed_prompt:
        raise HTTPException(400, "Could not understand prompt")

    # Generate all characters concurrently
    chars = await asyncio.gather(*[generate_character(p) for p in split.prompts])

    # Save all characters
    for char in chars:
        data.write_character(char, overwrite=True)

    return list(chars)


@app.post("/api/characters/split", dependencies=[Depends(use_api_key)])
async def split_character_prompts(req: CreateCharacterRequest) -> SplitPromptsResponse:
    """Split a group prompt into individual character prompts"""
    if not req.prompt.strip():
        raise HTTPException(400, "prompt required")

    split = await split_group_prompt(req.prompt)
    if split.malformed_prompt:
        raise HTTPException(400, "Could not understand prompt")

    return SplitPromptsResponse(prompts=split.prompts)


@app.post("/api/characters/generate", dependencies=[Depends(use_api_key)])
async def generate_single_character(req: GenerateCharacterRequest) -> CharacterOutput:
    """Generate a single character from a prompt"""
    if not req.prompt.strip():
        raise HTTPException(400, "prompt required")

    char = await generate_character(req.prompt)
    data.write_character(char, overwrite=True)

    return char


@app.delete("/api/characters/{char_id}", dependencies=[Depends(use_api_key)])
def delete_character(char_id: str) -> dict[str, str]:
    """Delete a character by UUID"""
    for path in data.list_characters():
        if not path.exists():
            continue
        char = CharacterOutput.model_validate_json(path.read_text())
        if str(char.uuid) == char_id:
            path.unlink(missing_ok=True)
            return {"status": "deleted"}
    raise HTTPException(404, "Character not found")


@app.post("/api/runs/start", dependencies=[Depends(use_api_key)])
def start_run(req: StartRunRequest) -> dict[str, T.Any]:
    """Start a new simulation run"""
    if not req.characters:
        raise HTTPException(400, "characters required")
    if req.mode == "task" and not req.task:
        raise HTTPException(400, "task required for task mode")

    # Create run dir
    run_dir = data.create_run_dir()

    # Build CLI args
    args = ["society", "run"]
    for name in req.characters:
        args.extend(["-c", name])
    args.extend(["-m", req.mode])
    if req.task:
        args.extend(["-t", req.task])
    args.extend(["-v", str(req.voting_start)])
    if req.duration is not None:
        args.extend(["-d", str(req.duration)])
    args.extend(["--run-dir", str(run_dir)])

    # Spawn subprocess (inherits env with API key if set by dependency)
    proc = subprocess.Popen(args, start_new_session=True, env=os.environ.copy())
    (run_dir / "pid").write_text(str(proc.pid))

    return {"status": "started", "runName": run_dir.name}


class ContinueRunRequest(BaseModel):
    message: str
    duration: float = 60.0  # seconds


@app.post("/api/runs/{run_name}/continue", dependencies=[Depends(use_api_key)])
def continue_run(run_name: str, req: ContinueRunRequest) -> dict[str, str]:
    """Continue a simulation with a new message"""
    run_path = data.get_data_dir() / "runs" / run_name
    if not run_path.exists():
        raise HTTPException(404, "Run not found")

    if not req.message.strip():
        raise HTTPException(400, "message required")

    # Build CLI args for continue command
    args = [
        "society",
        "continue",
        "--run-dir",
        str(run_path),
        "--message",
        req.message,
        "--duration",
        str(req.duration),
    ]

    # Spawn subprocess (inherits env with API key if set by dependency)
    proc = subprocess.Popen(args, start_new_session=True, env=os.environ.copy())
    (run_path / "pid").write_text(str(proc.pid))

    return {"status": "started"}


@app.post("/api/runs/{run_name}/stop", dependencies=[Depends(use_api_key)])
def stop_run(run_name: str) -> dict[str, str]:
    """Stop a running simulation"""
    run_path = data.get_data_dir() / "runs" / run_name
    if not run_path.exists():
        raise HTTPException(404, "Run not found")

    pid_file = run_path / "pid"
    if not pid_file.exists():
        raise HTTPException(400, "No PID file found - run may not be active")

    try:
        pid = int(pid_file.read_text().strip())
        # Kill the process group to ensure all child processes are killed
        os.killpg(os.getpgid(pid), signal.SIGTERM)
        pid_file.unlink(missing_ok=True)
        return {"status": "stopped"}
    except ProcessLookupError:
        pid_file.unlink(missing_ok=True)
        return {"status": "already_stopped"}
    except Exception as e:
        raise HTTPException(500, f"Failed to stop run: {e}")


@app.get("/api/runs/{run_name}/export", dependencies=[Depends(use_api_key)])
def export_run(run_name: str) -> StreamingResponse:
    """Export a run as a zip file with metadata and transcripts"""
    run_path = data.get_data_dir() / "runs" / run_name
    if not run_path.exists():
        raise HTTPException(404, "Run not found")

    chat = ChatClient(run_path / "chat", user_id=None)
    messages = chat.get_all_messages()
    channels = chat.list_channels()
    people = chat.list_people()

    # Get final answer from events
    final_answer = None
    events_path = run_path / "events.jsonl"
    if events_path.exists():
        for line in events_path.read_text().strip().split("\n"):
            if line:
                e = json.loads(line)
                if e.get("kind") == "simulation_end" and e.get("data", {}).get(
                    "final_answer"
                ):
                    final_answer = e["data"]["final_answer"]

    # Build metadata
    task = messages[0].text if messages else ""
    participants = [p.name for p in people if p.role != "ceo"]
    metadata = {
        "run_name": run_name,
        "task": task,
        "participants": participants,
        "final_answer": final_answer,
        "total_messages": len(messages),
        "channels": [c.name for c in channels],
    }

    # Create zip in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add metadata
        zf.writestr("metadata.json", json.dumps(metadata, indent=2))

        # Add transcript for each channel
        for channel in channels:
            transcript = chat.format_channel(channel.name)
            zf.writestr(f"transcripts/{channel.name}.txt", transcript)

    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{run_name}.zip"'},
    )


# Serve frontend static files (after building)
frontend_dist = Path(__file__).parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")
