"""
Command line interface for invoking this package
"""

import asyncio
from pathlib import Path

import typer
from rich.console import Console

from society import characters, data, runner
from society.datatypes import CharacterOutput, SimulationMode

console = Console()

app = typer.Typer(
    name="society",
    help="Can the whole be greater than the parts?",
    no_args_is_help=True,
    add_completion=False,
    add_help_option=True,
    pretty_exceptions_enable=True,
    pretty_exceptions_show_locals=False,
)

# ---------------------------------------------------------
# People
# ---------------------------------------------------------


@app.command()
def gen_character(
    prompt: str,
    model: str | None = None,
) -> None:
    """
    Build a character from a text prompt of a real or fictional person
    """
    with console.status("Generating character"):
        character = asyncio.run(characters.generate_character(prompt, model=model))

    out_path = data.write_character(character)
    if out_path is None:
        raise typer.Abort()

    console.print(
        f"{character.emoji} [bold cyan]{character.name}[/] → [dim]{out_path}[/]"
    )


@app.command()
def gen_characters(
    prompt: str,
    model: str | None = None,
) -> None:
    """
    Build multiple characters from a single text prompt
    """

    async def run_all() -> None:
        with console.status(f"Analyzing prompt: [yellow]{prompt}[/]"):
            result = await characters.split_group_prompt(prompt, model=model)

        if result.malformed_prompt:
            console.print("Prompt is not clear enough")
            raise typer.Abort()

        async def gen(person_prompt: str) -> None:
            with console.status(f"Generating [yellow]{person_prompt}[/]"):
                try:
                    person = await characters.generate_character(
                        person_prompt, model=model
                    )
                except Exception as e:
                    console.print(f"[red]Failed to generate {person_prompt}: {e}[/]")
                    return

                out_path = data.write_character(person)
                if out_path:
                    console.print(
                        f"{person.emoji} [bold cyan]{person.name}[/] → [dim]{out_path}[/]"
                    )
                else:
                    console.print(f"[bold cyan]{person.name}[/] skipped")

        async with asyncio.TaskGroup() as tg:
            for p in result.prompts:
                tg.create_task(gen(p))

    asyncio.run(run_all())


@app.command()
def list_characters(
    limit: int = typer.Option(None, "--limit", "-n", help="Max people to show"),
) -> None:
    """
    List generated characters
    """
    paths = data.list_characters(limit=limit)
    if not paths:
        console.print("No characters found.")
        return

    for i, path in enumerate(paths):
        character = CharacterOutput.model_validate_json(path.read_text())
        console.print(f"[bold cyan]{character.name}[/] → [dim]{path}[/]")


@app.command()
def show_character(
    name: str,
) -> None:
    """
    Show a character
    """
    paths = data.list_characters()
    characters = [
        CharacterOutput.model_validate_json(path.read_text()) for path in paths
    ]
    indices = [i for i, c in enumerate(characters) if name.lower() in c.name.lower()]
    if len(indices) != 1:
        console.print(f"Found {len(indices)} characters matching {name}:")
        for i in indices:
            console.print(f"  [bold cyan]{characters[i].name}[/] → [dim]{paths[i]}[/]")
        return

    index = indices[0]
    character = characters[index]
    path = paths[index]

    console.print()
    console.print(
        f"[bold]{character.emoji}[/] [bold cyan]{character.name}[/] → [dim]{path}[/]"
    )
    console.print()
    console.print(f"  [bold]Birth Year:[/] {character.birth_year}", highlight=False)
    console.print(f"  [bold]Gender:[/] {character.gender}")
    console.print(f"  [bold]Location:[/] {character.location}")
    console.print(f"  [bold]Occupation:[/] {character.occupation}")
    console.print()

    console.print(f"{character.bio}", highlight=False)


# ---------------------------------------------------------
# Runs
# ---------------------------------------------------------


@app.command()
def run(
    character: list[str] = typer.Option(
        ..., "--character", "-c", help="Character name (can be repeated)"
    ),
    task: str | None = typer.Option(
        None, "--task", "-t", help="Task to solve (required for task mode, optional prompt for casual mode)"
    ),
    mode: SimulationMode = typer.Option(
        SimulationMode.TASK, "--mode", "-m", help="Simulation mode: task or casual"
    ),
    voting_start: float = typer.Option(
        120.0, "--voting-start", "-v", help="Seconds before voting can begin (task mode)"
    ),
    duration: float | None = typer.Option(
        None, "--duration", "-d", help="Max duration in seconds (casual mode only)"
    ),
    run_dir: str | None = None,
) -> None:
    """
    Run a simulation

    Examples:
        society run -c alice -c bob -t "What's the capital of France?"
        society run -c alice -c bob -m casual
        society run -c alice -c bob -m casual -t "Let's discuss our favorite movies"
    """
    if mode == SimulationMode.TASK and task is None:
        console.print("[red]--task is required for task mode[/]")
        raise typer.Abort()

    all_characters = [
        CharacterOutput.model_validate_json(path.read_text())
        for path in data.list_characters()
    ]

    character_objs: list[CharacterOutput] = []
    for name in character:
        match = next(
            (c for c in all_characters if name.lower() in c.name.lower()), None
        )
        if match is None:
            console.print(f"[red]Character '{name}' not found.[/]")
            raise typer.Abort()
        character_objs.append(match)

    run_dir_path = Path(run_dir) if run_dir is not None else None

    asyncio.run(
        runner.run(
            characters=character_objs,
            mode=mode,
            task=task,
            run_dir=run_dir_path,
            voting_start_s=voting_start,
            duration_s=duration,
        )
    )


@app.command(name="continue")
def continue_run(
    run_dir: str = typer.Option(..., "--run-dir", help="Run directory to continue"),
    message: str = typer.Option(..., "--message", "-m", help="Message to post to #general"),
    duration: float = typer.Option(60.0, "--duration", "-d", help="How long to run (seconds)"),
) -> None:
    """
    Continue a previous simulation with a new message
    """
    run_dir_path = Path(run_dir)
    if not run_dir_path.exists():
        console.print(f"[red]Run directory not found: {run_dir}[/]")
        raise typer.Abort()

    asyncio.run(
        runner.continue_run(
            run_dir=run_dir_path,
            message=message,
            duration_s=duration,
        )
    )


@app.command()
def list_runs(
    limit: int = typer.Option(10, "--limit", "-n", help="Max runs to show"),
) -> None:
    """
    List recent simulation runs
    """
    run_dir = data.get_data_dir() / "runs"
    if not run_dir.exists():
        typer.echo(f"No runs found in {run_dir}")
        return
    runs = sorted(run_dir.iterdir(), reverse=True)[:limit]
    for run_path in runs:
        typer.echo(f"  {run_path.name}")


@app.command(name="web")
def run_web(
    port: int = typer.Option(8000, "--port", "-p", help="Port to run on"),
    reload: bool = typer.Option(False, "--reload", "-r", help="Auto-reload on changes"),
) -> None:
    """
    Launch the web UI
    """
    import uvicorn

    uvicorn.run(
        "web.api:app",
        host="0.0.0.0",
        port=port,
        reload=reload,
    )


@app.command(name="dev")
def run_dev(
    backend_port: int = typer.Option(8000, "--backend-port", "-b", help="Backend port"),
    frontend_port: int = typer.Option(
        5173, "--frontend-port", "-f", help="Frontend port"
    ),
) -> None:
    """
    Run both frontend and backend in dev/hot-reload mode
    """
    import os
    import sys

    frontend_dir = Path(__file__).parent / "web" / "frontend"
    if not frontend_dir.exists():
        console.print(f"[red]Frontend directory not found: {frontend_dir}[/]")
        raise typer.Abort()

    console.print(f"Starting dev servers...\n")

    backend_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "society.web.api:app",
        "--host",
        "0.0.0.0",
        "--port",
        str(backend_port),
        "--reload",
    ]
    frontend_cmd = ["npm", "run", "dev", "--", "--port", str(frontend_port)]

    console.print(f"[backend] [bold green]{' '.join(backend_cmd)}[/]\n")
    console.print(f"    http://localhost:{backend_port}\n")

    console.print(f"[frontend] [bold green]{' '.join(frontend_cmd)}[/]\n")
    console.print(f"    http://localhost:{frontend_port}\n")

    async def stream_output(
        proc: asyncio.subprocess.Process,
        prefix: str,
        color: str,
    ) -> None:
        """Stream stdout/stderr from a process with a colored prefix"""

        async def read_stream(
            stream: asyncio.StreamReader | None,
            is_stderr: bool = False,
        ) -> None:
            if stream is None:
                return
            while True:
                line = await stream.readline()
                if not line:
                    break
                text = line.decode().rstrip()
                console.print(f"[{color}]{prefix}[/] {text}")

        await asyncio.gather(
            read_stream(proc.stdout),
            read_stream(proc.stderr, is_stderr=True),
        )

    async def run_servers() -> None:
        backend_proc = await asyncio.create_subprocess_exec(
            *backend_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        frontend_env = {**os.environ, "SOCIETY_BACKEND_PORT": str(backend_port)}
        frontend_proc = await asyncio.create_subprocess_exec(
            *frontend_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=frontend_dir,
            env=frontend_env,
        )

        try:
            await asyncio.gather(
                stream_output(backend_proc, "[backend]", "cyan"),
                stream_output(frontend_proc, "[frontend]", "magenta"),
            )
        except asyncio.CancelledError:
            backend_proc.terminate()
            frontend_proc.terminate()
            raise

    try:
        asyncio.run(run_servers())
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down...[/]")


if __name__ == "__main__":
    app()
