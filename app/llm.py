"""llm.py - one small wrapper over LLM providers (Gemini or Groq) for CaneMitra (Day 6, S1).

Use:  from app.llm import generate
      text = generate(system_prompt, user_message)           # provider from LLM_PROVIDER in .env
      text = generate(system_prompt, user_message, provider="groq")

Keys are read from the environment or from the .env file in the repo root.
.env is git-ignored; .env.example shows the names that are needed.
"""
import os
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
TIMEOUT = 30  # seconds


class LLMError(Exception):
    """Raised when the provider is not configured or the call fails."""


def load_env(path: Path = ROOT / ".env") -> None:
    """Read KEY=VALUE lines from .env into os.environ (real environment variables win)."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _key(name: str) -> str:
    load_env()
    value = os.environ.get(name, "")
    if not value or value.startswith("your-"):
        raise LLMError(f"{name} is not set. Copy .env.example to .env and add your key.")
    return value


def _gemini(system_prompt: str, user_message: str, json_mode: bool) -> str:
    model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"role": "user", "parts": [{"text": user_message}]}],
        "generationConfig": {"temperature": 0.2},
    }
    if json_mode:
        body["generationConfig"]["responseMimeType"] = "application/json"
    r = requests.post(url, json=body, headers={"x-goog-api-key": _key("GEMINI_API_KEY")}, timeout=TIMEOUT)
    r.raise_for_status()
    try:
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as e:
        raise LLMError(f"Gemini returned no text: {r.text[:200]}") from e


def _groq(system_prompt: str, user_message: str, json_mode: bool) -> str:
    body = {
        "model": os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile"),
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}],
        "temperature": 0.2,
    }
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        json=body, headers={"Authorization": f"Bearer {_key('GROQ_API_KEY')}"}, timeout=TIMEOUT,
    )
    r.raise_for_status()
    try:
        return r.json()["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        raise LLMError(f"Groq returned no text: {r.text[:200]}") from e


PROVIDERS = {"gemini": _gemini, "groq": _groq}


def _short_reason(e: requests.HTTPError) -> str:
    """Google/Groq put a readable reason in the JSON body; return it (never the key)."""
    try:
        return str(e.response.json()["error"]["message"])[:200]
    except (ValueError, KeyError, TypeError):
        return ""


def generate(system_prompt: str, user_message: str, provider: str | None = None, json_mode: bool = True) -> str:
    """Send one system prompt + one user message to the provider and return the reply text.

    Busy-server answers (HTTP 429 and 503) are retried up to 3 times, waiting 2, 4 and 8 seconds.
    """
    load_env()
    name = (provider or os.environ.get("LLM_PROVIDER", "gemini")).lower()
    if name not in PROVIDERS:
        raise LLMError(f"Unknown provider '{name}'. Use one of: {', '.join(PROVIDERS)}")
    for attempt in range(4):
        try:
            return PROVIDERS[name](system_prompt, user_message, json_mode)
        except requests.Timeout as e:
            raise LLMError(f"{name} timed out after {TIMEOUT}s") from e
        except requests.HTTPError as e:
            status = e.response.status_code
            if status in (429, 503) and attempt < 3:
                time.sleep(2 ** (attempt + 1))
                continue
            raise LLMError(f"{name} returned HTTP {status}: {_short_reason(e)}") from e
        except requests.RequestException as e:
            raise LLMError(f"{name} request failed: {type(e).__name__}") from e