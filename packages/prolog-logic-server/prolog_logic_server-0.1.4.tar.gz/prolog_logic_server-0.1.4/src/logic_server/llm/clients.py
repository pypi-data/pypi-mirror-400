from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

import requests
from requests.exceptions import RequestException, Timeout
from openai import OpenAI, APIError, APIConnectionError, RateLimitError


Message = Dict[str, str]


__all__ = ["Message", "LLM", "OllamaLLM", "OpenAILLM", "LLMError"]


class LLMError(Exception):
    """Exception raised when LLM communication fails."""
    pass


class LLM(ABC):
    @abstractmethod
    def chat(self, messages: List[Message]) -> str:
        """Given a list of messages [{role, content}], return assistant text."""
        raise NotImplementedError


class OllamaLLM(LLM):
    """Adapter for Ollama's HTTP /api/chat endpoint."""

    def __init__(self,
                 model: str = "gpt-oss:20b-cloud",
                 base_url: str = "http://localhost:11434",
                 temperature: Optional[float] = None,
                 timeout: int = 120) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.temperature = temperature
        self.timeout = timeout

    def chat(self, messages: List[Message]) -> str:
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }
        if self.temperature is not None:
            payload["options"] = {"temperature": self.temperature}

        try:
            resp = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = resp.json()
        except Timeout:
            raise LLMError(f"Ollama request timed out after {self.timeout}s")
        except RequestException as e:
            raise LLMError(f"Ollama request failed: {e}")
        except ValueError as e:
            raise LLMError(f"Invalid JSON response from Ollama: {e}")

        # Safely extract content from response
        try:
            return data["message"]["content"]
        except (KeyError, TypeError) as e:
            raise LLMError(f"Unexpected Ollama response format: {e}")


class OpenAILLM(LLM):
    """Adapter for OpenAI's Chat Completions API using the official Python client."""

    def __init__(self,
                 model: str = "gpt-4.1-mini",
                 api_key: Optional[str] = None,
                 base_url: Optional[str] = None,
                 temperature: Optional[float] = None,
                 timeout: int = 120) -> None:
        client_kwargs: Dict[str, Any] = {"timeout": timeout}
        if api_key is not None:
            client_kwargs["api_key"] = api_key
        if base_url is not None:
            client_kwargs["base_url"] = base_url

        self.client = OpenAI(**client_kwargs)
        self.model = model
        self.temperature = temperature

    def chat(self, messages: List[Message]) -> str:
        completion_kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
        }
        if self.temperature is not None:
            completion_kwargs["temperature"] = self.temperature

        try:
            completion = self.client.chat.completions.create(**completion_kwargs)
            return completion.choices[0].message.content or ""
        except RateLimitError as e:
            raise LLMError(f"OpenAI rate limit exceeded: {e}")
        except APIConnectionError as e:
            raise LLMError(f"OpenAI connection error: {e}")
        except APIError as e:
            raise LLMError(f"OpenAI API error: {e}")
        except (IndexError, AttributeError) as e:
            raise LLMError(f"Unexpected OpenAI response format: {e}")
