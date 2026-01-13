"""OpenRouter API client."""

import json
import os
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Final, Literal, Self

import httpx

from orter.types import (
    JSONObject,
    JSONTypeError,
    JSONValue,
    ensure_json_object,
    ensure_json_value,
)

DEFAULT_BASE_URL: Final[str] = "https://openrouter.ai"


class OpenRouterError(RuntimeError):
    """OpenRouter API call failed."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


@dataclass(frozen=True, slots=True)
class OpenRouterConfig:
    api_key: str
    base_url: str = DEFAULT_BASE_URL
    referer: str | None = None
    title: str | None = None
    timeout_s: float = 60.0


def _env(name: str) -> str | None:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return None
    return value


def load_config(
    *,
    api_key: str | None = None,
    base_url: str = DEFAULT_BASE_URL,
    referer: str | None = None,
    title: str | None = None,
    timeout_s: float = 60.0,
) -> OpenRouterConfig:
    key = api_key or _env("OPENROUTER_API_KEY")
    if key is None:
        raise OpenRouterError(
            "OPENROUTER_API_KEY environment variable is empty. Or specify with --api-key."
        )
    return OpenRouterConfig(
        api_key=key,
        base_url=base_url,
        referer=referer,
        title=title,
        timeout_s=timeout_s,
    )


class OpenRouterClient:
    """Minimal wrapper for OpenRouter REST API.

    Documentation (requests/responses/headers): https://openrouter.ai/docs/api/reference/overview
    """

    def __init__(self, config: OpenRouterConfig) -> None:
        self._config = config
        self._client = httpx.Client(
            base_url=config.base_url,
            timeout=httpx.Timeout(config.timeout_s),
            headers=self._build_headers(),
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def _build_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {
            "Authorization": f"Bearer {self._config.api_key}",
            "Content-Type": "application/json",
        }
        # Optional headers specified in documentation
        if self._config.referer:
            headers["HTTP-Referer"] = self._config.referer
        if self._config.title:
            headers["X-Title"] = self._config.title
        return headers

    def _raise_for_status(self, response: httpx.Response) -> None:
        if 200 <= response.status_code < 300:
            return
        try:
            payload = response.json()
        except Exception:
            payload = None
        msg = f"HTTP {response.status_code} {response.reason_phrase}"
        if isinstance(payload, dict) and "error" in payload:
            msg = f"{msg}: {payload['error']}"
        elif payload is not None:
            msg = f"{msg}: {payload}"
        raise OpenRouterError(msg, status_code=response.status_code)

    def _decode_json(self, response: httpx.Response) -> JSONValue:
        raw: object
        try:
            raw = response.json()
        except Exception as e:
            raise OpenRouterError(f"JSON decoding failed: {e}") from e
        try:
            return ensure_json_value(raw)
        except JSONTypeError as e:
            raise OpenRouterError(f"JSON type validation failed: {e}") from e

    def get_json(self, path: str, *, params: dict[str, str] | None = None) -> JSONValue:
        r = self._client.get(path, params=params)
        self._raise_for_status(r)
        return self._decode_json(r)

    def post_json(self, path: str, *, body: JSONObject) -> JSONValue:
        r = self._client.post(path, json=body)
        self._raise_for_status(r)
        return self._decode_json(r)

    def request_json(
        self,
        method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"],
        path: str,
        *,
        params: dict[str, str] | None = None,
        body: JSONObject | None = None,
    ) -> JSONValue:
        r = self._client.request(method, path, params=params, json=body)
        self._raise_for_status(r)
        return self._decode_json(r)

    # ---- Main OpenRouter endpoints (used directly in CLI) ----

    def list_models(self) -> JSONValue:
        return self.get_json("/api/v1/models")

    def list_models_count(self) -> JSONValue:
        return self.get_json("/api/v1/models/count")

    def list_models_user(self) -> JSONValue:
        return self.get_json("/api/v1/models/user")

    def chat_completions(self, *, payload: JSONObject) -> JSONValue:
        return self.post_json("/api/v1/chat/completions", body=payload)

    def get_generation(self, *, generation_id: str) -> JSONValue:
        return self.get_json("/api/v1/generation", params={"id": generation_id})

    # ---- Analytics ----

    def get_user_activity(self, *, date: str | None = None) -> JSONValue:
        params: dict[str, str] | None = None
        if date:
            params = {"date": date}
        return self.get_json("/api/v1/activity", params=params)

    # ---- Credits ----

    def get_credits(self) -> JSONValue:
        return self.get_json("/api/v1/credits")

    def create_coinbase_charge(self, *, payload: JSONObject) -> JSONValue:
        return self.post_json("/api/v1/credits/coinbase", body=payload)

    # ---- Embeddings ----

    def create_embeddings(self, *, payload: JSONObject) -> JSONValue:
        return self.post_json("/api/v1/embeddings", body=payload)

    def list_embeddings_models(self) -> JSONValue:
        return self.get_json("/api/v1/embeddings/models")

    # ---- Endpoints ----

    def list_endpoints(self, *, author: str, slug: str) -> JSONValue:
        return self.get_json(f"/api/v1/models/{author}/{slug}/endpoints")

    def list_endpoints_zdr(self) -> JSONValue:
        return self.get_json("/api/v1/endpoints/zdr")

    # ---- Parameters ----

    def get_parameters(
        self, *, author: str, slug: str, provider: str | None = None
    ) -> JSONValue:
        params: dict[str, str] | None = None
        if provider:
            params = {"provider": provider}
        return self.get_json(f"/api/v1/parameters/{author}/{slug}", params=params)

    # ---- Providers ----

    def list_providers(self) -> JSONValue:
        return self.get_json("/api/v1/providers")

    # ---- API Keys ----

    def list_api_keys(
        self, *, include_disabled: bool | None = None, offset: int | None = None
    ) -> JSONValue:
        params: dict[str, str] | None = None
        if include_disabled is not None:
            params = {"include_disabled": str(include_disabled).lower()}
        if offset is not None:
            if params is None:
                params = {}
            params["offset"] = str(offset)
        return self.get_json("/api/v1/keys", params=params)

    def create_api_key(self, *, payload: JSONObject) -> JSONValue:
        return self.post_json("/api/v1/keys", body=payload)

    def get_api_key(self, *, key_id: str) -> JSONValue:
        return self.get_json(f"/api/v1/keys/{key_id}")

    def update_api_key(self, *, key_id: str, payload: JSONObject) -> JSONValue:
        return self.request_json("PATCH", f"/api/v1/keys/{key_id}", body=payload)

    def delete_api_key(self, *, key_id: str) -> JSONValue:
        return self.request_json("DELETE", f"/api/v1/keys/{key_id}")

    def get_current_api_key(self) -> JSONValue:
        return self.get_json("/api/v1/keys/current")

    # ---- OAuth ----

    def exchange_auth_code_for_api_key(self, *, payload: JSONObject) -> JSONValue:
        return self.post_json("/api/v1/auth/keys", body=payload)

    def create_auth_keys_code(self, *, payload: JSONObject) -> JSONValue:
        return self.post_json("/api/v1/auth/keys/code", body=payload)

    # ---- Completions ----

    def create_completions(self, *, payload: JSONObject) -> JSONValue:
        return self.post_json("/api/v1/completions", body=payload)

    def stream_completions(self, *, payload: JSONObject) -> Iterable[JSONObject]:
        """Yield completion chunks (JSON objects) via SSE streaming."""
        body: JSONObject = dict(payload)
        body["stream"] = True
        with self._client.stream("POST", "/api/v1/completions", json=body) as r:
            self._raise_for_status(r)
            for line in r.iter_lines():
                s = line.strip()
                if s == "" or s.startswith(":"):
                    # Ignore empty lines/comment payloads (see docs)
                    continue
                if not s.startswith("data:"):
                    continue
                data = s.removeprefix("data:").strip()
                if data == "[DONE]":
                    break
                try:
                    parsed = json.loads(data)
                except json.JSONDecodeError:
                    continue
                try:
                    yield ensure_json_object(parsed)
                except JSONTypeError:
                    continue

    # ---- Streaming (SSE) ----

    def stream_chat_completions(self, *, payload: JSONObject) -> Iterable[JSONObject]:
        """Yield chat completion chunks (JSON objects) via SSE streaming."""
        body: JSONObject = dict(payload)
        body["stream"] = True
        with self._client.stream("POST", "/api/v1/chat/completions", json=body) as r:
            self._raise_for_status(r)
            for line in r.iter_lines():
                s = line.strip()
                if s == "" or s.startswith(":"):
                    # Ignore empty lines/comment payloads (see docs)
                    continue
                if not s.startswith("data:"):
                    continue
                data = s.removeprefix("data:").strip()
                if data == "[DONE]":
                    break
                try:
                    parsed = json.loads(data)
                except json.JSONDecodeError:
                    continue
                try:
                    yield ensure_json_object(parsed)
                except JSONTypeError:
                    continue
