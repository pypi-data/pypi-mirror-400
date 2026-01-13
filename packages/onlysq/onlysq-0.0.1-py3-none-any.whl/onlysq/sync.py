import requests
import json
from typing import List, Dict, Optional, Generator, Any


class Dialog:
    def __init__(self, client: "OnlySq"):
        self._client = client
        self._messages: List[Dict] = []
        if client._system:
            self._messages.append({"role": "system", "content": client._system})

    def ask(self, text: str) -> str:
        if not text:
            raise ValueError("Text is empty")
        self._messages.append({"role": "user", "content": text})
        resp = self._client.conversation(self._messages)
        answer = resp["choices"][0]["message"]["content"]
        self._messages.append({"role": "assistant", "content": answer})
        return answer

    @property
    def history(self) -> List[Dict]:
        return self._messages


class OnlySq:
    def __init__(
        self,
        api_key: str = "openai",
        model: str = "qwen3-235b-a22b",
        timeout: int = 60,
    ):
        self._api_key = api_key
        self._model = model
        self._timeout = timeout
        self._session: Optional[requests.Session] = None
        self._base_url = "https://api.onlysq.ru/ai/openai"
        self._system: Optional[str] = None

    def __enter__(self):
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        })
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            self._session.close()

    def set_system(self, prompt: Optional[str]):
        self._system = prompt

    def ask_raw(
        self,
        text: str,
        reasoning: Optional[str] = None,
        **extra: Any,
    ) -> dict:
        if not text:
            raise ValueError("Text is empty")
        messages: List[Dict] = []
        if self._system:
            messages.append({"role": "system", "content": self._system})
        messages.append({"role": "user", "content": text})
        if reasoning is not None:
            extra.setdefault("reasoning", reasoning)
        return self.conversation(messages, **extra)

    def ask(
        self,
        text: str,
        reasoning: Optional[str] = None,
        **extra: Any,
    ) -> str:
        resp = self.ask_raw(text, reasoning=reasoning, **extra)
        return resp["choices"][0]["message"]["content"]

    def conversation(self, messages: List[Dict], **extra: Any) -> dict:
        if not messages:
            raise ValueError("Messages list is empty")
        payload: Dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            **extra,
        }
        url = f"{self._base_url}/chat/completions"
        resp = self._session.post(
            url,
            json=payload,
            timeout=self._timeout,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"API error {resp.status_code}: {resp.text}")
        return resp.json()

    def stream(
        self,
        messages: List[Dict],
        **extra: Any,
    ) -> Generator[Dict, None, None]:
        if not messages:
            raise ValueError("Messages list is empty")
        payload: Dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "stream": True,
            **extra,
        }
        url = f"{self._base_url}/chat/completions"
        with self._session.post(
            url,
            json=payload,
            timeout=self._timeout,
            stream=True,
        ) as resp:
            if resp.status_code != 200:
                raise RuntimeError(f"API error {resp.status_code}: {resp.text}")
            for line in resp.iter_lines():
                if not line:
                    continue
                text = line.decode("utf-8").strip()
                if not text.startswith("data:"):
                    continue
                data = text[len("data:") :].strip()
                if data == "[DONE]":
                    break
                try:
                    yield json.loads(data)
                except json.JSONDecodeError:
                    continue

    def stream_dialog(
        self,
        text: str,
        reasoning: Optional[str] = None,
        **extra: Any,
    ) -> Generator[Dict[str, Optional[str]], None, None]:
        """Stream reasoning (thinking) and content chunks for a single-user message."""
        if not text:
            raise ValueError("Text is empty")

        messages: List[Dict] = []
        if self._system:
            messages.append({"role": "system", "content": self._system})
        messages.append({"role": "user", "content": text})

        if reasoning is not None:
            extra.setdefault("reasoning", reasoning)

        for chunk in self.stream(messages, **extra):
            choice = chunk.get("choices", [{}])[0]
            delta = choice.get("delta", {})
            yield {
                "thinking": delta.get("reasoning_content"),
                "content": delta.get("content"),
            }

    def dialog(self) -> Dialog:
        return Dialog(self)
