import aiohttp
import json
from typing import List, Dict, Optional, AsyncGenerator, Any


class Dialog:
    def __init__(self, client: "AsyncOnlySq"):
        self._client = client
        self._messages: List[Dict] = []
        if client._system:
            self._messages.append({"role": "system", "content": client._system})

    async def ask(self, text: str) -> str:
        if not text:
            raise ValueError("Text is empty")
        self._messages.append({"role": "user", "content": text})
        resp = await self._client.conversation(self._messages)
        answer = resp["choices"][0]["message"]["content"]
        self._messages.append({"role": "assistant", "content": answer})
        return answer

    @property
    def history(self) -> List[Dict]:
        return self._messages


class AsyncOnlySq:
    def __init__(
        self,
        api_key: str = "openai",
        model: str = "qwen3-235b-a22b",
        timeout: int = 60,
    ):
        self._api_key = api_key
        self._model = model
        self._timeout = timeout
        self._session: Optional[aiohttp.ClientSession] = None
        self._base_url = "https://api.onlysq.ru/ai/openai"
        self._system: Optional[str] = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            timeout=aiohttp.ClientTimeout(total=self._timeout),
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session and not self._session.closed:
            await self._session.close()

    def set_system(self, prompt: Optional[str]):
        self._system = prompt

    async def ask_raw(
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
        return await self.conversation(messages, **extra)

    async def ask(
        self,
        text: str,
        reasoning: Optional[str] = None,
        **extra: Any,
    ) -> str:
        resp = await self.ask_raw(text, reasoning=reasoning, **extra)
        return resp["choices"][0]["message"]["content"]

    async def conversation(self, messages: List[Dict], **extra: Any) -> dict:
        if not messages:
            raise ValueError("Messages list is empty")
        payload: Dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            **extra,
        }
        url = f"{self._base_url}/chat/completions"
        async with self._session.post(url, json=payload) as resp:
            if resp.status != 200:
                raise RuntimeError(
                    f"API error {resp.status}: {await resp.text()}"
                )
            return await resp.json()

    async def stream(
        self,
        messages: List[Dict],
        **extra: Any,
    ) -> AsyncGenerator[Dict, None]:
        if not messages:
            raise ValueError("Messages list is empty")
        payload: Dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "stream": True,
            **extra,
        }
        url = f"{self._base_url}/chat/completions"
        async with self._session.post(url, json=payload) as resp:
            if resp.status != 200:
                raise RuntimeError(
                    f"API error {resp.status}: {await resp.text()}"
                )
            async for line in resp.content:
                text = line.decode("utf-8").strip()
                if not text or not text.startswith("data:"):
                    continue
                data = text[len("data:") :].strip()
                if data == "[DONE]":
                    break
                try:
                    yield json.loads(data)
                except json.JSONDecodeError:
                    continue

    async def stream_dialog(
        self,
        text: str,
        reasoning: Optional[str] = None,
        **extra: Any,
    ) -> AsyncGenerator[Dict[str, Optional[str]], None]:
        """Stream reasoning (thinking) and content chunks for a single-user message."""
        if not text:
            raise ValueError("Text is empty")

        messages: List[Dict] = []
        if self._system:
            messages.append({"role": "system", "content": self._system})
        messages.append({"role": "user", "content": text})

        if reasoning is not None:
            extra.setdefault("reasoning", reasoning)

        async for chunk in self.stream(messages, **extra):
            choice = chunk.get("choices", [{}])[0]
            delta = choice.get("delta", {})
            yield {
                "thinking": delta.get("reasoning_content"),
                "content": delta.get("content"),
            }

    def dialog(self) -> Dialog:
        return Dialog(self)
