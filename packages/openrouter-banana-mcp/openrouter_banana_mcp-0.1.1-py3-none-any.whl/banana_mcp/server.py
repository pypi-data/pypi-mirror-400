import json
import os
from typing import Any

import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "google/gemini-3-pro-image-preview"
REQUEST_TIMEOUT_SECS = float(os.getenv("OPENROUTER_TIMEOUT_SECS", "60"))

mcp = FastMCP("Banana MCP")


def _require_api_key() -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set. Provide it via environment or a .env file."
        )
    return api_key


@mcp.tool()
def generate_image(prompt: str) -> dict[str, Any]:
    """Generate an image from a text prompt via OpenRouter."""
    api_key = _require_api_key()
    payload = {
        "model": DEFAULT_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "modalities": ["image", "text"],
    }

    response = requests.post(
        url=OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
        timeout=REQUEST_TIMEOUT_SECS,
    )
    response.raise_for_status()
    result = response.json()

    images: list[str] = []
    message_text: str | None = None
    if result.get("choices"):
        message = result["choices"][0].get("message", {})
        message_text = message.get("content")
        for image in message.get("images", []) or []:
            image_url = image.get("image_url", {}).get("url")
            if image_url:
                images.append(image_url)

    if not images:
        error_message = result.get("error", {}).get("message")
        if error_message:
            raise RuntimeError(f"OpenRouter error: {error_message}")
        raise RuntimeError("No images returned from OpenRouter.")

    return {"model": DEFAULT_MODEL, "images": images, "text": message_text}


def main() -> None:
    mcp.run()
