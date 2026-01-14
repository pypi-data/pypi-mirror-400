"""API clients for Poe and Google Deep Research."""

import os
import re
import time
import json
import requests
from dataclasses import dataclass
from typing import Callable, Optional

import openai


@dataclass
class ResearchResult:
    """Result of a research request."""
    success: bool
    content: str = ""
    error: Optional[str] = None
    interaction_id: Optional[str] = None


def run_research(
    model: str,
    api_type: str,
    prompt: str,
    interaction_id: Optional[str] = None,
    timeout: int = 600,
    on_chunk: Optional[Callable[[str], None]] = None,
    on_interaction_id: Optional[Callable[[str], None]] = None,
) -> ResearchResult:
    """Run deep research using the appropriate API.

    Args:
        model: Model name
        api_type: 'poe' or 'google'
        prompt: Research prompt
        interaction_id: For resuming (Poe) or continuing (Google) research
        timeout: Timeout in seconds
        on_chunk: Callback for progress updates
        on_interaction_id: Callback when interaction ID is received

    Returns:
        ResearchResult with success status and content
    """
    if api_type == "google":
        return run_google_research(
            prompt=prompt,
            interaction_id=interaction_id,
            timeout=timeout,
            on_chunk=on_chunk,
            on_interaction_id=on_interaction_id,
        )
    else:
        return run_poe_research(
            model=model,
            prompt=prompt,
            interaction_id=interaction_id,
            timeout=timeout,
            on_chunk=on_chunk,
            on_interaction_id=on_interaction_id,
        )


def run_poe_research(
    model: str,
    prompt: str,
    interaction_id: Optional[str] = None,
    timeout: int = 600,
    on_chunk: Optional[Callable[[str], None]] = None,
    on_interaction_id: Optional[Callable[[str], None]] = None,
) -> ResearchResult:
    """Run research using Poe's OpenAI-compatible API with streaming."""
    api_key = os.environ.get("POE_API_KEY")
    base_url = os.environ.get("POE_BASE_URL", "https://api.poe.com/v1")

    if not api_key:
        return ResearchResult(success=False, error="POE_API_KEY not set")

    client = openai.OpenAI(api_key=api_key, base_url=base_url)

    # Build message with optional interaction_id for resume
    content = prompt
    if interaction_id:
        content = f"[Continuing research with interaction_id: {interaction_id}]\n\n{prompt}"

    collected_content = []
    detected_interaction_id = None

    try:
        stream = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": content}],
            stream=True,
            timeout=timeout,
        )

        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                collected_content.append(text)

                # Try to extract interaction_id from early output
                if not detected_interaction_id:
                    full_text = "".join(collected_content)
                    match = re.search(r"v1_[A-Za-z0-9+/=]+", full_text)
                    if match:
                        detected_interaction_id = match.group(0)
                        if on_interaction_id:
                            on_interaction_id(detected_interaction_id)

                if on_chunk:
                    on_chunk(text)

        full_content = "".join(collected_content)
        return ResearchResult(
            success=True,
            content=full_content,
            interaction_id=detected_interaction_id,
        )

    except Exception as e:
        partial = "".join(collected_content)
        return ResearchResult(
            success=False,
            content=partial,
            error=str(e),
            interaction_id=detected_interaction_id,
        )


def run_google_research(
    prompt: str,
    interaction_id: Optional[str] = None,
    timeout: int = 600,
    on_chunk: Optional[Callable[[str], None]] = None,
    on_interaction_id: Optional[Callable[[str], None]] = None,
) -> ResearchResult:
    """Run research using Google's Interactions REST API with polling.

    This uses the background polling mode which is more stable than streaming.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    base_url = os.environ.get("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com")

    if not api_key:
        return ResearchResult(success=False, error="GEMINI_API_KEY not set")

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }

    # If we have an interaction_id, poll that existing task
    if interaction_id:
        if on_chunk:
            on_chunk(f"[Resuming interaction: {interaction_id}]\n")
        return poll_google_interaction(
            base_url=base_url,
            headers=headers,
            interaction_id=interaction_id,
            timeout=timeout,
            on_chunk=on_chunk,
        )

    # Start a new research task
    start_url = f"{base_url}/v1beta/interactions"
    body = {
        "input": prompt,
        "agent": "deep-research-pro-preview-12-2025",
        "background": True  # Use polling mode, not streaming
    }

    if on_chunk:
        on_chunk("[Starting Google Deep Research...]\n")

    try:
        resp = requests.post(start_url, headers=headers, json=body, timeout=60)

        if resp.status_code != 200:
            return ResearchResult(
                success=False,
                error=f"Failed to start task: {resp.status_code} - {resp.text}"
            )

        data = resp.json()
        new_interaction_id = data.get("id")

        if not new_interaction_id:
            return ResearchResult(
                success=False,
                error=f"No interaction ID in response: {data}"
            )

        if on_chunk:
            on_chunk(f"[Task started. Interaction ID: {new_interaction_id}]\n")

        if on_interaction_id:
            on_interaction_id(new_interaction_id)

        # Poll for completion
        return poll_google_interaction(
            base_url=base_url,
            headers=headers,
            interaction_id=new_interaction_id,
            timeout=timeout,
            on_chunk=on_chunk,
        )

    except requests.exceptions.Timeout:
        return ResearchResult(success=False, error="Timeout starting task")
    except Exception as e:
        return ResearchResult(success=False, error=str(e))


def poll_google_interaction(
    base_url: str,
    headers: dict,
    interaction_id: str,
    timeout: int,
    on_chunk: Optional[Callable[[str], None]] = None,
) -> ResearchResult:
    """Poll a Google Interactions task until completion."""
    poll_url = f"{base_url}/v1beta/interactions/{interaction_id}"
    poll_interval = 10  # seconds
    max_polls = timeout // poll_interval

    start_time = time.time()
    last_status = None

    for i in range(max_polls):
        elapsed = int(time.time() - start_time)

        try:
            resp = requests.get(poll_url, headers=headers, timeout=30)

            if resp.status_code != 200:
                if on_chunk:
                    on_chunk(f"\n[Poll error: {resp.status_code}]\n")
                time.sleep(poll_interval)
                continue

            data = resp.json()
            status = data.get("status", "unknown")

            # Report status changes
            if status != last_status:
                if on_chunk:
                    on_chunk(f"\n[Status: {status} ({elapsed}s elapsed)]\n")
                last_status = status

            if status == "completed":
                # Extract output
                outputs = data.get("outputs", [])
                final_text = ""
                for output in outputs:
                    if output.get("type") == "text" or "text" in output:
                        final_text += output.get("text", "")

                if on_chunk:
                    on_chunk(f"\n[Research completed! {len(final_text)} chars]\n")
                    # Output the actual content
                    on_chunk(final_text)

                return ResearchResult(
                    success=True,
                    content=final_text,
                    interaction_id=interaction_id,
                )

            elif status == "failed":
                error_msg = data.get("error", "Unknown error")
                return ResearchResult(
                    success=False,
                    error=f"Research failed: {error_msg}",
                    interaction_id=interaction_id,
                )

            elif status in ("pending", "running", "in_progress"):
                # Still working, continue polling
                if on_chunk and i % 3 == 0:  # Log every 30 seconds
                    on_chunk(f"[Polling... {elapsed}s elapsed]\n")

        except requests.exceptions.Timeout:
            if on_chunk:
                on_chunk(f"\n[Poll timeout, retrying...]\n")
        except Exception as e:
            if on_chunk:
                on_chunk(f"\n[Poll error: {e}]\n")

        time.sleep(poll_interval)

    # Timeout
    return ResearchResult(
        success=False,
        error=f"Timeout after {timeout}s waiting for completion",
        interaction_id=interaction_id,
    )
