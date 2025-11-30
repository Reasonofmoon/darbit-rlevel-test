from __future__ import annotations

import json
import os
from typing import Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()

LLM_DEFAULTS = {
    "openai": {"model": "gpt-4o-mini"},
    "anthropic": {"model": "claude-3-5-sonnet-20241022"},
    "gemini": {"model": "gemini-2.5-pro"},
}


class LLMNotConfigured(RuntimeError):
    pass


def _load_client(provider: str):
    provider = provider.lower()
    if provider == "openai":
        try:
            import openai
        except ImportError as exc:
            raise LLMNotConfigured("openai package not installed") from exc

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise LLMNotConfigured("OPENAI_API_KEY not set")
        openai.api_key = api_key
        return openai
    if provider == "anthropic":
        try:
            import anthropic
        except ImportError as exc:
            raise LLMNotConfigured("anthropic package not installed") from exc

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise LLMNotConfigured("ANTHROPIC_API_KEY not set")
        return anthropic.Anthropic(api_key=api_key)
    if provider == "gemini":
        try:
            import google.generativeai as genai
        except ImportError as exc:
            raise LLMNotConfigured("google-generativeai package not installed") from exc

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise LLMNotConfigured("GEMINI_API_KEY not set")
        genai.configure(api_key=api_key)
        return genai
    raise ValueError(f"Unsupported provider: {provider}")


def _system_prompt(level: str, section: str) -> str:
    return (
        "You generate CEFR-aligned English test items.\n"
        f"Level: {level}\n"
        f"Section: {section}\n"
        "Return JSON with list of items, each: {id, text, options:[{label,text}], correct}.\n"
        "Choices must use labels A,B,C,D and correct must be one of them.\n"
        "Keep language concise and level-appropriate."
    )


def _user_prompt(level: str, section: str, count: int, context: Optional[str] = None) -> str:
    prompt = (
        f"Generate {count} CEFR {level} questions for the section '{section}'. "
        "Keep passages short (1-3 sentences) and answers brief. "
        "Return ONLY JSON like {\"items\":[...]}."
    )
    if context:
        prompt += f"\n\nContext/Topic to use:\n{context}"
    return prompt


def llm_generate_questions(
    provider: str, level: str, section: str, count: int, model: Optional[str] = None, context: Optional[str] = None
) -> List[Dict]:
    """
    Generate questions via an LLM provider. Raises LLMNotConfigured if API key missing.
    Returns a list of question dicts matching test_generator expectations.
    """
    provider = provider.lower()
    model = model or LLM_DEFAULTS.get(provider, {}).get("model")
    if not model:
        raise ValueError(f"No default model for provider: {provider}")

    client = _load_client(provider)
    system = _system_prompt(level, section)
    user = _user_prompt(level, section, count, context)

    if provider == "openai":
        resp = client.ChatCompletion.create(model=model, messages=[{"role": "system", "content": system}, {"role": "user", "content": user}])
        content = resp.choices[0].message.content
    elif provider == "anthropic":
        message = client.messages.create(model=model, max_tokens=2048, system=system, messages=[{"role": "user", "content": user}])
        content = message.content[0].text
    elif provider == "gemini":
        # Use system_instruction if supported by the SDK version, otherwise fallback to prompt concatenation
        # For simplicity and robustness with latest models, we try to pass system_instruction
        try:
            model_instance = client.GenerativeModel(model, system_instruction=system)
            message = model_instance.generate_content(user)
        except TypeError:
             # Fallback for older SDKs that might not support system_instruction in init
            model_instance = client.GenerativeModel(model)
            prompt = f"System: {system}\n\nUser: {user}"
            message = model_instance.generate_content(prompt)
            
        content = message.text
    else:
        raise ValueError(f"Unsupported provider: {provider}")

    try:
        parsed = json.loads(content)
        items = parsed.get("items", [])
    except Exception:
        # If the model returned non-JSON, try to extract a JSON block
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1 and end > start:
            parsed = json.loads(content[start : end + 1])
            items = parsed.get("items", [])
        else:
            raise

    normalized: List[Dict] = []
    for idx, item in enumerate(items):
        options = item.get("options", [])
        # Ensure labels and correct exist
        normalized.append(
            {
                "id": item.get("id") or f"{section[0].upper()}{idx + 1}",
                "text": item.get("text", ""),
                "options": [{"label": opt.get("label"), "text": opt.get("text", "")} for opt in options],
                "correct": item.get("correct", "A"),
                "section": section,
            }
        )
    return normalized


__all__ = ["llm_generate_questions", "LLMNotConfigured", "LLM_DEFAULTS"]
