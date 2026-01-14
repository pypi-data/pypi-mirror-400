"""Utility & helper functions."""

import os

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from pydantic import SecretStr


def get_message_text(msg: BaseMessage) -> str:
    """Get the text content of a message."""
    content = msg.content
    if isinstance(content, str):
        return content
    elif isinstance(content, dict):
        return content.get("text", "")
    else:
        txts = [c if isinstance(c, str) else (c.get("text") or "") for c in content]
        return "".join(txts).strip()


def load_chat_model(
    fully_specified_name: str | None = None,
    **kwargs,
) -> BaseChatModel:
    """Load a chat model from a fully specified name.

    Args:
        fully_specified_name: String in the format 'provider/model', or just model name.
            If None or empty, will use environment variables.
        **kwargs: Optional configuration parameters:
            - base_url (str): Base URL for the API endpoint.
            - api_key (str): API key for authentication.
            - temperature (float): Temperature for model generation (0.0 to 1.0).
            For backward compatibility, all kwargs are optional.
    """
    # Get values from kwargs or fall back to environment variables
    final_base_url = kwargs.get("base_url") or os.getenv("OPENAI_BASE_URL")
    final_api_key = kwargs.get("api_key") or os.getenv("OPENAI_API_KEY")
    final_temperature = kwargs.get("temperature", 0.0)

    # Use OpenAI-compatible client when:
    # 1. No name provided, or
    # 2. Name has no "/" and final_base_url is set, or
    # 3. Provider is "compatible_openai"
    use_compatible = (
        not fully_specified_name
        or ("/" not in fully_specified_name and final_base_url)
        or (
            fully_specified_name
            and fully_specified_name.startswith("compatible_openai/")
        )
    )

    if use_compatible:
        model = fully_specified_name
        if fully_specified_name and "/" in fully_specified_name:
            model = fully_specified_name.split("/", maxsplit=1)[1]
        model = model or os.getenv("OPENAI_MODEL_NAME")

        return ChatOpenAI(
            api_key=SecretStr(final_api_key) if final_api_key else None,
            base_url=final_base_url,
            model=model,
            streaming=True,
            temperature=final_temperature,
            timeout=120,
        )

    provider, model = fully_specified_name.split("/", maxsplit=1)
    return init_chat_model(model, model_provider=provider)
