"""
claude_logger.py — Non-blocking Claude token usage logger.
Drop this file into any AURENIX system that uses the Anthropic API.

Usage:
    from claude_logger import log_claude_usage

    # After an Anthropic API call:
    log_claude_usage(
        model="claude-haiku-4-5-20251001",
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
    )

The agent picks up /data/orbit_metrics.jsonl and includes it in the next heartbeat.
"""
import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path

METRICS_FILE = Path(os.environ.get("ORBIT_METRICS_FILE", "data/orbit_metrics.jsonl"))

HAIKU_MODELS = {"claude-haiku-4-5-20251001", "claude-3-haiku-20240307"}
SONNET_MODELS = {"claude-sonnet-4-6", "claude-3-5-sonnet-20241022", "claude-3-sonnet-20240229"}

_lock = threading.Lock()


def log_claude_usage(model: str, input_tokens: int, output_tokens: int) -> None:
    """
    Append a single usage record to the JSONL metrics file.
    Thread-safe, non-blocking (fire and forget via thread).
    """
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "model_family": "haiku" if model in HAIKU_MODELS else "sonnet" if model in SONNET_MODELS else "other",
    }
    threading.Thread(target=_write, args=(record,), daemon=True).start()


def _write(record: dict) -> None:
    try:
        METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with _lock:
            with open(METRICS_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
    except Exception:
        pass


def read_and_reset() -> dict:
    """
    Read accumulated metrics since last call and reset the file.
    Called by the agent before each heartbeat to collect token usage.
    Returns: {haiku_tokens: int, sonnet_tokens: int}
    """
    haiku = 0
    sonnet = 0
    try:
        if not METRICS_FILE.exists():
            return {"haiku_tokens": 0, "sonnet_tokens": 0}
        with _lock:
            with open(METRICS_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
            # Reset file
            open(METRICS_FILE, "w").close()

        for line in lines:
            try:
                r = json.loads(line)
                if r.get("model_family") == "haiku":
                    haiku += r.get("total_tokens", 0)
                else:
                    sonnet += r.get("total_tokens", 0)
            except Exception:
                pass
    except Exception:
        pass
    return {"haiku_tokens": haiku, "sonnet_tokens": sonnet}
