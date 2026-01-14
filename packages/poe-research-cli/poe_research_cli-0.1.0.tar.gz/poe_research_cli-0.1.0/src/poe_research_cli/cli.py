"""CLI interface for Poe Research."""

import os
import sys
import click
from pathlib import Path
from datetime import datetime
from uuid import uuid4

from .client import run_research, ResearchResult
from .state import State, load_state, save_state, get_cache_dir


# Model shortcuts - expand to full model names
# Format: shortcut -> (full_model_name, api_type)
MODEL_CONFIGS = {
    "o4-mini": ("o4-mini-deep-research", "poe"),
    "o3": ("o3-deep-research", "poe"),
    "gemini": ("gemini-2.0-flash", "google"),  # Uses Google Interactions API
}


def resolve_model(model: str) -> tuple[str, str]:
    """Resolve model shortcut to (model_name, api_type)."""
    if model in MODEL_CONFIGS:
        return MODEL_CONFIGS[model]
    # Default to Poe API for unknown models
    return (model, "poe")


def generate_task_id() -> str:
    """Generate a unique task ID with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    short_uuid = uuid4().hex[:8]
    return f"{timestamp}_{short_uuid}"


@click.command()
@click.option("--model", "-m", default="o4-mini", help="Model to use (o4-mini, o3, gemini, or full model name)")
@click.option("--prompt", "-p", required=False, help="Research prompt")
@click.option("--resume", "-r", is_flag=True, help="Resume from last incomplete task")
@click.option("--task-id", "-t", help="Specific task ID to resume")
@click.option("--list-tasks", "-l", is_flag=True, help="List all cached tasks")
@click.option("--max-retries", default=3, help="Maximum retry attempts")
@click.option("--timeout", default=600, help="Timeout in seconds per attempt")
def main(model: str, prompt: str | None, resume: bool, task_id: str | None,
         list_tasks: bool, max_retries: int, timeout: int):
    """Poe Deep Research CLI with retry/resume support.

    Examples:

        # Simple research with default model (o4-mini)
        poe-research -p "What are the latest AI developments?"

        # Use specific model
        poe-research -m gemini -p "Research quantum computing trends"

        # Resume last incomplete task
        poe-research --resume

        # Resume specific task
        poe-research -t 2026-01-08_123456_abc12345
    """
    cache_dir = get_cache_dir()

    # List tasks mode (no API key needed)
    if list_tasks:
        list_cached_tasks(cache_dir)
        return

    # Resume mode - load state first, then check API key based on stored api_type
    if resume or task_id:
        state = find_resumable_task(cache_dir, task_id)
        if not state:
            click.echo("[ERROR] No resumable task found", err=True)
            sys.exit(1)
        # Check API key based on stored state's api_type
        if state.api_type == "google":
            if not os.environ.get("GEMINI_API_KEY"):
                click.echo("[ERROR] GEMINI_API_KEY environment variable not set", err=True)
                sys.exit(1)
        else:
            if not os.environ.get("POE_API_KEY"):
                click.echo("[ERROR] POE_API_KEY environment variable not set", err=True)
                sys.exit(1)
        click.echo(f"[RESUME] Task {state.task_id} | Model: {state.model} | API: {state.api_type}")
        click.echo(f"[RESUME] Interaction ID: {state.interaction_id}")
        run_task(state, max_retries, timeout)
        return

    # New task mode - resolve model and check API key
    resolved_model, api_type = resolve_model(model)

    if api_type == "google":
        if not os.environ.get("GEMINI_API_KEY"):
            click.echo("[ERROR] GEMINI_API_KEY environment variable not set", err=True)
            sys.exit(1)
    else:
        if not os.environ.get("POE_API_KEY"):
            click.echo("[ERROR] POE_API_KEY environment variable not set", err=True)
            sys.exit(1)

    # New task mode
    if not prompt:
        click.echo("[ERROR] --prompt is required for new tasks", err=True)
        sys.exit(1)

    new_task_id = generate_task_id()
    task_dir = cache_dir / new_task_id
    task_dir.mkdir(parents=True, exist_ok=True)

    state = State(
        task_id=new_task_id,
        model=resolved_model,
        api_type=api_type,
        prompt=prompt,
        task_dir=str(task_dir),
    )
    save_state(state)

    click.echo(f"[START] Task {new_task_id} | Model: {resolved_model} | API: {api_type}")
    run_task(state, max_retries, timeout)


def list_cached_tasks(cache_dir: Path):
    """List all cached tasks."""
    if not cache_dir.exists():
        click.echo("No cached tasks found.")
        return

    tasks = sorted(cache_dir.iterdir(), reverse=True)
    if not tasks:
        click.echo("No cached tasks found.")
        return

    click.echo(f"Cached tasks in {cache_dir}:\n")
    for task_path in tasks[:20]:  # Show last 20
        state_file = task_path / "state.json"
        if state_file.exists():
            state = load_state(state_file)
            status_icon = {"completed": "[OK]", "failed": "[FAIL]", "in_progress": "[...]"}.get(state.status, "[?]")
            api_info = getattr(state, 'api_type', 'poe')  # backwards compat for old states
            click.echo(f"  {status_icon} {state.task_id} | {state.model} | {api_info} | {state.status}")
        else:
            click.echo(f"  [?] {task_path.name} | (no state file)")


def find_resumable_task(cache_dir: Path, specific_id: str | None = None) -> State | None:
    """Find a task to resume."""
    if not cache_dir.exists():
        return None

    if specific_id:
        task_dir = cache_dir / specific_id
        state_file = task_dir / "state.json"
        if state_file.exists():
            return load_state(state_file)
        return None

    # Find most recent incomplete task
    for task_path in sorted(cache_dir.iterdir(), reverse=True):
        state_file = task_path / "state.json"
        if state_file.exists():
            state = load_state(state_file)
            if state.status == "in_progress" and state.interaction_id:
                return state

    return None


def run_task(state: State, max_retries: int, timeout: int):
    """Execute the research task with retries."""
    import time

    start_time = time.time()

    for attempt in range(1, max_retries + 1):
        state.attempts = attempt
        state.status = "in_progress"
        save_state(state)

        click.echo(f"[ATTEMPT {attempt}/{max_retries}]")

        try:
            result = run_research(
                model=state.model,
                api_type=state.api_type,
                prompt=state.prompt,
                interaction_id=state.interaction_id,
                timeout=timeout,
                on_chunk=lambda chunk: (print(chunk, end="", flush=True)),
                on_interaction_id=lambda iid: update_interaction_id(state, iid),
            )

            if result.success:
                elapsed = time.time() - start_time
                handle_success(state, result, elapsed)
                return
            else:
                click.echo(f"\n[WARN] Attempt {attempt} failed: {result.error}")
                if attempt < max_retries:
                    wait_time = 2 ** attempt * 5
                    click.echo(f"[WAIT] Retrying in {wait_time}s...")
                    time.sleep(wait_time)

        except KeyboardInterrupt:
            click.echo("\n[INTERRUPT] Saving state for resume...")
            state.status = "in_progress"
            save_state(state)
            click.echo(f"[SAVED] Resume with: poe-research --resume -t {state.task_id}")
            sys.exit(130)

        except Exception as e:
            click.echo(f"\n[ERROR] Attempt {attempt} exception: {e}")
            if attempt < max_retries:
                wait_time = 2 ** attempt * 5
                click.echo(f"[WAIT] Retrying in {wait_time}s...")
                time.sleep(wait_time)

    # All retries exhausted
    elapsed = time.time() - start_time
    handle_failure(state, "Max retries exhausted", elapsed)


def update_interaction_id(state: State, interaction_id: str):
    """Update state with new interaction ID."""
    state.interaction_id = interaction_id
    save_state(state)


def handle_success(state: State, result: ResearchResult, elapsed: float):
    """Handle successful research completion."""
    state.status = "completed"
    state.partial_output = result.content
    save_state(state)

    # Write result to file
    result_path = Path(state.task_dir) / "result.md"
    result_path.write_text(result.content)

    # Print summary
    print("\n")
    click.echo("=" * 60)
    click.echo(f"[COMPLETE] {state.model} ({state.api_type}) | {elapsed:.1f}s | {len(result.content):,} chars")
    click.echo(f"Result: {result_path}")
    click.echo("=" * 60)
    click.echo("\n=== PREVIEW (500 chars) ===")
    click.echo(result.content[:500])
    if len(result.content) > 500:
        click.echo("...")
    click.echo("\n=== STATS ===")
    click.echo(f"Task ID: {state.task_id}")
    click.echo(f"Model: {state.model}")
    click.echo(f"API: {state.api_type}")
    click.echo(f"Attempts: {state.attempts}")
    if state.interaction_id:
        click.echo(f"Interaction ID: {state.interaction_id[:50]}...")


def handle_failure(state: State, error: str, elapsed: float):
    """Handle failed research."""
    state.status = "failed"
    state.error = error
    save_state(state)

    click.echo("=" * 60)
    click.echo(f"[FAILED] {state.model} ({state.api_type}) | {elapsed:.1f}s | {error}")
    click.echo(f"Task ID: {state.task_id}")
    if state.interaction_id:
        click.echo(f"Resume with: poe-research --resume -t {state.task_id}")
    if state.partial_output:
        partial_path = Path(state.task_dir) / "partial.md"
        partial_path.write_text(state.partial_output)
        click.echo(f"Partial output saved: {partial_path}")
    click.echo("=" * 60)
    sys.exit(1)


if __name__ == "__main__":
    main()
