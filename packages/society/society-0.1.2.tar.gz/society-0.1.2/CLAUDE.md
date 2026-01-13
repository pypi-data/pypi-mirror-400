# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Society is a multi-agent simulation framework where AI agents, each playing a "character" (real or fictional person), collaborate in group chats to solve tasks or casually interact. Characters are generated via web search to build detailed profiles, then agents embodying those characters communicate through a chat system with channels.

The goal of this repo is to be very minimal and compact. Think like nanochat from karpathy. It should be performant and built to scale to a large number of characters, but without fluff or boilerplate.

## Commands

```bash
# Setup
uv venv --python=3.12 .venv
source .venv/bin/activate
uv pip install -e .

# Linting
ruff check .
ruff format .
ty check

# CLI
society gen-character "Elon Musk"     # Generate a single character
society gen-characters "the cast of Friends"  # Generate multiple characters
society list-characters               # List all characters
society show-character alice          # Show character details
society run -c alice -c bob -t "What's the capital of France?"  # Task mode
society run -c alice -c bob -m casual  # Casual chat mode
society list-runs                     # List recent simulation runs

# Dev servers (frontend + backend with hot reload)
society dev

# Frontend only (from src/society/web/frontend/)
npm run dev
npm run build
npm run lint
```

## Architecture

**Core simulation flow:**
1. `cli.py` → Entry point, typer CLI with commands for character generation and simulation runs
2. `characters.py` → Uses pydantic-ai agents with WebSearchTool to research and generate character profiles
3. `runner.py` → Main simulation loop that spawns multiple agents concurrently, each playing a character
4. `deps.py` → Pydantic BaseModel holding per-agent dependencies (character, chat client, shared state)
5. `instructions.py` → Dynamic system prompt functions injected into each agent based on mode/state

**Agent tooling:**
- `tools.py` → Agent tools: `send_message`, `create_channel`, `join_channel`, `read_channel`, `leave_channel`, `wait`, `propose_answer`, `vote_on_answer`
- Agents communicate via `ChatClient` which persists messages to JSONL files per channel
- Task mode requires unanimous voting to complete; casual mode has no objective

**Key datatypes (`datatypes.py`):**
- `CharacterOutput` → Generated character profile with name, bio, personality, context
- `SimulationMode` → TASK (solve a problem) or CASUAL (social chat)
- `SharedState` → Mutable state shared across agents for answers/votes
- `Message`, `Channel`, `Person`, `Answer`, `Vote` → Chat and voting primitives

**Web UI:**
- `web/api.py` → FastAPI backend
- `web/frontend/` → React + Vite + TypeScript frontend

## Code Style

- Use `pydantic` `BaseModel` over dataclasses
- Use `import typing as T` not `from typing import ...`
- Use `from pathlib import Path` not `import os`
- Don't block the asyncio event loop with sync code
- Main function/class at top of module, helpers below
- Multi-line function signatures: one arg per line with trailing comma
- Use typer for CLI scripts
- Put imports at the top, not inline
