"""
Plimver Python SDK

Official SDK for the Plimver AI Platform
Unified LLM, RAG, and Memory API

Example:
    >>> from plimver import Plimver
    >>> 
    >>> client = Plimver(
    ...     api_key="pk_live_...",
    ...     workspace_id="ws_..."
    ... )
    >>> 
    >>> response = client.chat("Hello!")
    >>> print(response.text)
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import (
    Any,
    AsyncGenerator,
    Dict,
    Generator,
    List,
    Literal,
    Optional,
    Union,
)

import httpx

__version__ = "1.0.0"
__all__ = ["Plimver", "AsyncPlimver", "PlimverError", "ChatResponse", "Document"]


# ============================================================
# Types
# ============================================================

RoutingMode = Literal["auto", "chat_only", "rag_only", "chat_and_rag"]
CostPreference = Literal["low", "balanced", "quality"]


@dataclass
class Usage:
    """Token usage statistics"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class Source:
    """RAG source document"""
    source: str
    text: str
    score: float


@dataclass
class ChatResponse:
    """Response from a chat request"""
    text: str
    model: str = "unknown"
    provider: str = "unknown"
    mode: RoutingMode = "auto"
    usage: Usage = field(default_factory=Usage)
    sources: List[Source] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Document:
    """A RAG document"""
    id: str
    source: str
    text: str = ""
    total_chunks: int = 1
    created_at: str = ""


@dataclass
class Message:
    """A chat message"""
    role: Literal["system", "user", "assistant"]
    content: Union[str, List[Dict[str, Any]]]


@dataclass
class StreamChunk:
    """A streaming response chunk"""
    content: Optional[str] = None
    done: bool = False
    usage: Optional[Usage] = None
    error: Optional[str] = None


class PlimverError(Exception):
    """Plimver API error"""
    def __init__(self, message: str, status: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.status = status


# ============================================================
# Sync Client
# ============================================================

class Plimver:
    """
    Plimver SDK Client (Synchronous)
    
    Args:
        api_key: Your Plimver API key (pk_live_... or pk_test_...)
        workspace_id: Workspace ID to use
        base_url: Base URL (default: https://api.plimvr.tech)
        timeout: Request timeout in seconds (default: 30)
        max_retries: Max retries on failure (default: 2)
    
    Example:
        >>> client = Plimver(
        ...     api_key="pk_live_...",
        ...     workspace_id="ws_..."
        ... )
        >>> response = client.chat("Hello!")
        >>> print(response.text)
    """
    
    def __init__(
        self,
        api_key: str,
        workspace_id: str,
        base_url: str = "https://api.plimvr.tech",
        timeout: float = 30.0,
        max_retries: int = 2,
    ):
        if not api_key:
            raise ValueError("api_key is required")
        if not workspace_id:
            raise ValueError("workspace_id is required")
        
        self.api_key = api_key
        self.workspace_id = workspace_id
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        
        self._client = httpx.Client(
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        
        # Sub-clients
        self.documents = DocumentsClient(self)
        self.memory = MemoryClient(self)
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
    
    def close(self):
        """Close the HTTP client"""
        self._client.close()
    
    # ============================================================
    # Core Chat Methods
    # ============================================================
    
    def chat(
        self,
        message: str,
        *,
        mode: RoutingMode = "auto",
        model: str = "auto",
        cost_preference: Optional[CostPreference] = None,
        user_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ChatResponse:
        """
        Send a chat message and get a response.
        
        Args:
            message: The message to send
            mode: Routing mode (auto, chat_only, rag_only, chat_and_rag)
            model: Model to use (default: auto for smart routing)
            cost_preference: Cost preference when using auto routing
            user_id: User ID for conversation isolation
            system_prompt: System prompt override
            temperature: Temperature (0-2)
            metadata: Custom metadata
        
        Returns:
            ChatResponse with text, model, usage, etc.
        
        Example:
            >>> response = client.chat("What is AI?")
            >>> print(response.text)
        """
        messages = [Message(role="user", content=message)]
        return self.chat_with_messages(
            messages,
            mode=mode,
            model=model,
            cost_preference=cost_preference,
            user_id=user_id,
            system_prompt=system_prompt,
            temperature=temperature,
            metadata=metadata,
        )
    
    def chat_with_messages(
        self,
        messages: List[Message],
        *,
        mode: RoutingMode = "auto",
        model: str = "auto",
        cost_preference: Optional[CostPreference] = None,
        user_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ChatResponse:
        """
        Send multiple messages (conversation history).
        
        Example:
            >>> messages = [
            ...     Message(role="user", content="My name is Alice"),
            ...     Message(role="assistant", content="Nice to meet you!"),
            ...     Message(role="user", content="What is my name?"),
            ... ]
            >>> response = client.chat_with_messages(messages)
        """
        # Build messages list
        msg_list = []
        if system_prompt:
            msg_list.append({"role": "system", "content": system_prompt})
        
        for msg in messages:
            msg_list.append({"role": msg.role, "content": msg.content})
        
        # Build request body
        body: Dict[str, Any] = {
            "messages": msg_list,
            "mode": mode,
            "model": model,
            "stream": False,
        }
        
        if user_id:
            body["user_id"] = user_id
        if cost_preference:
            body["cost_preference"] = cost_preference
        if temperature is not None:
            body["temperature"] = temperature
        if metadata:
            body["metadata"] = metadata
        
        response = self._request("POST", "/chat", body)
        
        return ChatResponse(
            text=response.get("choices", [{}])[0].get("message", {}).get("content", "") 
                 or response.get("response", ""),
            model=response.get("model", "unknown"),
            provider=response.get("provider", "unknown"),
            mode=response.get("mode", mode),
            usage=Usage(
                prompt_tokens=response.get("usage", {}).get("prompt_tokens", 0),
                completion_tokens=response.get("usage", {}).get("completion_tokens", 0),
                total_tokens=response.get("usage", {}).get("total_tokens", 0),
            ),
            sources=[
                Source(source=s["source"], text=s["text"], score=s["score"])
                for s in response.get("sources", [])
            ],
            metadata=response.get("metadata", {}),
        )
    
    def stream(
        self,
        message: str,
        *,
        mode: RoutingMode = "auto",
        model: str = "auto",
        user_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> Generator[StreamChunk, None, None]:
        """
        Stream a chat response.
        
        Example:
            >>> for chunk in client.stream("Tell me a story"):
            ...     print(chunk.content or "", end="", flush=True)
        """
        messages = [Message(role="user", content=message)]
        yield from self.stream_with_messages(
            messages,
            mode=mode,
            model=model,
            user_id=user_id,
            system_prompt=system_prompt,
            temperature=temperature,
        )
    
    def stream_with_messages(
        self,
        messages: List[Message],
        *,
        mode: RoutingMode = "auto",
        model: str = "auto",
        user_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> Generator[StreamChunk, None, None]:
        """Stream with full message history"""
        # Build messages list
        msg_list = []
        if system_prompt:
            msg_list.append({"role": "system", "content": system_prompt})
        
        for msg in messages:
            msg_list.append({"role": msg.role, "content": msg.content})
        
        body: Dict[str, Any] = {
            "messages": msg_list,
            "mode": mode,
            "model": model,
            "stream": True,
        }
        
        if user_id:
            body["user_id"] = user_id
        if temperature is not None:
            body["temperature"] = temperature
        
        url = f"{self.base_url}/api/v1/workspaces/{self.workspace_id}/chat"
        
        with self._client.stream("POST", url, json=body) as response:
            if response.status_code != 200:
                raise PlimverError(f"Stream request failed: {response.status_code}", response.status_code)
            
            for line in response.iter_lines():
                if line.startswith("data: "):
                    data = line[6:].strip()
                    if data == "[DONE]":
                        return
                    
                    try:
                        chunk_data = json.loads(data)
                        yield StreamChunk(
                            content=chunk_data.get("content"),
                            done=chunk_data.get("done", False),
                            usage=Usage(
                                prompt_tokens=chunk_data.get("usage", {}).get("prompt_tokens", 0),
                                completion_tokens=chunk_data.get("usage", {}).get("completion_tokens", 0),
                                total_tokens=0,
                            ) if chunk_data.get("usage") else None,
                            error=chunk_data.get("error"),
                        )
                        if chunk_data.get("done"):
                            return
                    except json.JSONDecodeError:
                        pass
    
    # ============================================================
    # Multimodal Methods
    # ============================================================
    
    def vision(
        self,
        text: str,
        image_url: str,
        *,
        mode: RoutingMode = "auto",
        model: str = "auto",
        **kwargs,
    ) -> ChatResponse:
        """
        Send a message with an image.
        
        Example:
            >>> response = client.vision(
            ...     "What is in this image?",
            ...     "https://example.com/photo.jpg"
            ... )
        """
        content = [
            {"type": "text", "text": text},
            {"type": "image_url", "image_url": {"url": image_url}},
        ]
        return self.chat_with_messages(
            [Message(role="user", content=content)],
            mode=mode,
            model=model,
            **kwargs,
        )
    
    def audio(
        self,
        text: str,
        audio_url: str,
        *,
        mode: RoutingMode = "auto",
        model: str = "gemini-1.5-pro",
        **kwargs,
    ) -> ChatResponse:
        """
        Send a message with audio (requires Gemini 1.5 Pro+).
        
        Example:
            >>> response = client.audio(
            ...     "Transcribe this",
            ...     "https://example.com/audio.mp3"
            ... )
        """
        content = [
            {"type": "text", "text": text},
            {"type": "audio_url", "audio_url": {"url": audio_url}},
        ]
        return self.chat_with_messages(
            [Message(role="user", content=content)],
            mode=mode,
            model=model,
            **kwargs,
        )
    
    def video(
        self,
        text: str,
        video_url: str,
        *,
        mode: RoutingMode = "auto",
        model: str = "gemini-1.5-pro",
        **kwargs,
    ) -> ChatResponse:
        """
        Send a message with video (requires Gemini 1.5 Pro+).
        
        Example:
            >>> response = client.video(
            ...     "Summarize this video",
            ...     "https://example.com/video.mp4"
            ... )
        """
        content = [
            {"type": "text", "text": text},
            {"type": "video_url", "video_url": {"url": video_url}},
        ]
        return self.chat_with_messages(
            [Message(role="user", content=content)],
            mode=mode,
            model=model,
            **kwargs,
        )
    
    # ============================================================
    # Utility Methods
    # ============================================================
    
    def get_workspace(self) -> Dict[str, Any]:
        """Get workspace info"""
        return self._request("GET", "")
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List configured LLM models"""
        response = self._request("GET", "/llms")
        return [
            {
                "id": llm["id"],
                "provider": llm["provider"],
                "model": llm["model"],
                "is_default": llm.get("is_default", False),
            }
            for llm in response.get("llms", [])
        ]
    
    def get_formats(self, type: Optional[str] = None) -> Dict[str, Any]:
        """Get supported formats"""
        url = f"{self.base_url}/api/v1/formats"
        if type:
            url += f"?type={type}"
        response = self._client.get(url)
        return response.json()
    
    # ============================================================
    # Internal Methods
    # ============================================================
    
    def _request(self, method: str, path: str, body: Optional[Dict] = None) -> Dict[str, Any]:
        """Make an API request with retries"""
        url = f"{self.base_url}/api/v1/workspaces/{self.workspace_id}{path}"
        
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                if method == "GET":
                    response = self._client.get(url)
                elif method == "POST":
                    response = self._client.post(url, json=body)
                elif method == "PUT":
                    response = self._client.put(url, json=body)
                elif method == "DELETE":
                    response = self._client.delete(url)
                else:
                    raise ValueError(f"Unknown method: {method}")
                
                if response.status_code >= 400:
                    error_data = response.json() if response.text else {}
                    raise PlimverError(
                        error_data.get("error", response.reason_phrase),
                        response.status_code,
                    )
                
                return response.json() if response.text else {}
                
            except PlimverError as e:
                # Don't retry client errors
                if e.status and 400 <= e.status < 500:
                    raise
                last_error = e
            except Exception as e:
                last_error = PlimverError(str(e))
            
            # Wait before retry
            if attempt < self.max_retries:
                time.sleep(2 ** attempt)
        
        raise last_error or PlimverError("Request failed after retries")


# ============================================================
# Sub-Clients
# ============================================================

class DocumentsClient:
    """Documents operations"""
    
    def __init__(self, client: Plimver):
        self._client = client
    
    def upload(
        self,
        text: str,
        source: str,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Document:
        """
        Upload text content as a document.
        
        Example:
            >>> doc = client.documents.upload(
            ...     "Plimver is an AI platform...",
            ...     source="about.txt"
            ... )
        """
        body = {
            "source": source,
            "text": text,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
        }
        if metadata:
            body["metadata"] = metadata
        
        response = self._client._request("POST", "/documents", body)
        return self._map_document(response)
    
    def upload_file(
        self,
        file_path: str,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ) -> Document:
        """
        Upload a file.
        
        Example:
            >>> doc = client.documents.upload_file("document.pdf")
        """
        import os
        
        filename = os.path.basename(file_path)
        
        with open(file_path, "rb") as f:
            files = {"file": (filename, f)}
            data = {
                "chunk_size": str(chunk_size),
                "chunk_overlap": str(chunk_overlap),
            }
            
            url = f"{self._client.base_url}/api/v1/workspaces/{self._client.workspace_id}/documents/upload"
            response = httpx.post(
                url,
                files=files,
                data=data,
                headers={"Authorization": f"Bearer {self._client.api_key}"},
                timeout=self._client.timeout,
            )
            
            if response.status_code >= 400:
                raise PlimverError(response.text, response.status_code)
            
            return self._map_document(response.json())
    
    def list(self) -> List[Document]:
        """List all documents"""
        response = self._client._request("GET", "/documents")
        return [self._map_document(d) for d in response.get("documents", [])]
    
    def delete(self, source: str) -> None:
        """Delete a document by source name"""
        from urllib.parse import quote
        self._client._request("DELETE", f"/documents/{quote(source, safe='')}")
    
    def search(self, query: str, limit: int = 5) -> List[Source]:
        """Search documents (vector similarity)"""
        response = self._client._request("POST", "/documents/search", {"query": query, "limit": limit})
        return [
            Source(source=r["source"], text=r["text"], score=r["score"])
            for r in response.get("results", [])
        ]
    
    def _map_document(self, data: Dict) -> Document:
        return Document(
            id=data.get("id", ""),
            source=data.get("source", ""),
            text=data.get("text", ""),
            total_chunks=data.get("total_chunks", 1),
            created_at=data.get("created_at", ""),
        )


class MemoryClient:
    """Memory/conversation history operations"""
    
    def __init__(self, client: Plimver):
        self._client = client
    
    def get(self, user_id: str, limit: int = 50) -> List[Message]:
        """Get conversation history for a user"""
        from urllib.parse import quote
        response = self._client._request("GET", f"/memory?user_id={quote(user_id, safe='')}&limit={limit}")
        return [
            Message(role=m["role"], content=m["content"])
            for m in response.get("messages", [])
        ]
    
    def clear(self, user_id: str) -> None:
        """Clear conversation history for a user"""
        from urllib.parse import quote
        self._client._request("DELETE", f"/memory?user_id={quote(user_id, safe='')}")
    
    def clear_all(self) -> None:
        """Clear all conversation history"""
        self._client._request("DELETE", "/memory/all")


# ============================================================
# Async Client
# ============================================================

class AsyncPlimver:
    """
    Plimver SDK Client (Asynchronous)
    
    Same API as Plimver but with async/await support.
    
    Example:
        >>> async with AsyncPlimver(api_key="...", workspace_id="...") as client:
        ...     response = await client.chat("Hello!")
        ...     print(response.text)
    """
    
    def __init__(
        self,
        api_key: str,
        workspace_id: str,
        base_url: str = "https://api.plimvr.tech",
        timeout: float = 30.0,
        max_retries: int = 2,
    ):
        if not api_key:
            raise ValueError("api_key is required")
        if not workspace_id:
            raise ValueError("workspace_id is required")
        
        self.api_key = api_key
        self.workspace_id = workspace_id
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        
        self._client = httpx.AsyncClient(
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args):
        await self.close()
    
    async def close(self):
        """Close the HTTP client"""
        await self._client.aclose()
    
    async def chat(
        self,
        message: str,
        *,
        mode: RoutingMode = "auto",
        model: str = "auto",
        **kwargs,
    ) -> ChatResponse:
        """Send a chat message (async)"""
        messages = [Message(role="user", content=message)]
        return await self.chat_with_messages(messages, mode=mode, model=model, **kwargs)
    
    async def chat_with_messages(
        self,
        messages: List[Message],
        *,
        mode: RoutingMode = "auto",
        model: str = "auto",
        cost_preference: Optional[CostPreference] = None,
        user_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ChatResponse:
        """Send multiple messages (async)"""
        msg_list = []
        if system_prompt:
            msg_list.append({"role": "system", "content": system_prompt})
        
        for msg in messages:
            msg_list.append({"role": msg.role, "content": msg.content})
        
        body: Dict[str, Any] = {
            "messages": msg_list,
            "mode": mode,
            "model": model,
            "stream": False,
        }
        
        if user_id:
            body["user_id"] = user_id
        if cost_preference:
            body["cost_preference"] = cost_preference
        if temperature is not None:
            body["temperature"] = temperature
        if metadata:
            body["metadata"] = metadata
        
        response = await self._request("POST", "/chat", body)
        
        return ChatResponse(
            text=response.get("choices", [{}])[0].get("message", {}).get("content", "") 
                 or response.get("response", ""),
            model=response.get("model", "unknown"),
            provider=response.get("provider", "unknown"),
            mode=response.get("mode", mode),
            usage=Usage(
                prompt_tokens=response.get("usage", {}).get("prompt_tokens", 0),
                completion_tokens=response.get("usage", {}).get("completion_tokens", 0),
                total_tokens=response.get("usage", {}).get("total_tokens", 0),
            ),
            sources=[
                Source(source=s["source"], text=s["text"], score=s["score"])
                for s in response.get("sources", [])
            ],
            metadata=response.get("metadata", {}),
        )
    
    async def stream(
        self,
        message: str,
        **kwargs,
    ) -> AsyncGenerator[StreamChunk, None]:
        """Stream a chat response (async)"""
        messages = [Message(role="user", content=message)]
        async for chunk in self.stream_with_messages(messages, **kwargs):
            yield chunk
    
    async def stream_with_messages(
        self,
        messages: List[Message],
        *,
        mode: RoutingMode = "auto",
        model: str = "auto",
        user_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> AsyncGenerator[StreamChunk, None]:
        """Stream with full message history (async)"""
        msg_list = []
        if system_prompt:
            msg_list.append({"role": "system", "content": system_prompt})
        
        for msg in messages:
            msg_list.append({"role": msg.role, "content": msg.content})
        
        body: Dict[str, Any] = {
            "messages": msg_list,
            "mode": mode,
            "model": model,
            "stream": True,
        }
        
        if user_id:
            body["user_id"] = user_id
        if temperature is not None:
            body["temperature"] = temperature
        
        url = f"{self.base_url}/api/v1/workspaces/{self.workspace_id}/chat"
        
        async with self._client.stream("POST", url, json=body) as response:
            if response.status_code != 200:
                raise PlimverError(f"Stream request failed", response.status_code)
            
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:].strip()
                    if data == "[DONE]":
                        return
                    
                    try:
                        chunk_data = json.loads(data)
                        yield StreamChunk(
                            content=chunk_data.get("content"),
                            done=chunk_data.get("done", False),
                            error=chunk_data.get("error"),
                        )
                        if chunk_data.get("done"):
                            return
                    except json.JSONDecodeError:
                        pass
    
    async def vision(self, text: str, image_url: str, **kwargs) -> ChatResponse:
        """Send a message with an image (async)"""
        content = [
            {"type": "text", "text": text},
            {"type": "image_url", "image_url": {"url": image_url}},
        ]
        return await self.chat_with_messages([Message(role="user", content=content)], **kwargs)
    
    async def audio(self, text: str, audio_url: str, **kwargs) -> ChatResponse:
        """Send a message with audio (async)"""
        content = [
            {"type": "text", "text": text},
            {"type": "audio_url", "audio_url": {"url": audio_url}},
        ]
        kwargs.setdefault("model", "gemini-1.5-pro")
        return await self.chat_with_messages([Message(role="user", content=content)], **kwargs)
    
    async def video(self, text: str, video_url: str, **kwargs) -> ChatResponse:
        """Send a message with video (async)"""
        content = [
            {"type": "text", "text": text},
            {"type": "video_url", "video_url": {"url": video_url}},
        ]
        kwargs.setdefault("model", "gemini-1.5-pro")
        return await self.chat_with_messages([Message(role="user", content=content)], **kwargs)
    
    async def _request(self, method: str, path: str, body: Optional[Dict] = None) -> Dict[str, Any]:
        """Make an API request with retries (async)"""
        url = f"{self.base_url}/api/v1/workspaces/{self.workspace_id}{path}"
        
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                if method == "GET":
                    response = await self._client.get(url)
                elif method == "POST":
                    response = await self._client.post(url, json=body)
                elif method == "DELETE":
                    response = await self._client.delete(url)
                else:
                    raise ValueError(f"Unknown method: {method}")
                
                if response.status_code >= 400:
                    error_data = response.json() if response.text else {}
                    raise PlimverError(
                        error_data.get("error", str(response.status_code)),
                        response.status_code,
                    )
                
                return response.json() if response.text else {}
                
            except PlimverError as e:
                if e.status and 400 <= e.status < 500:
                    raise
                last_error = e
            except Exception as e:
                last_error = PlimverError(str(e))
            
            if attempt < self.max_retries:
                await asyncio.sleep(2 ** attempt)
        
        raise last_error or PlimverError("Request failed after retries")


# For async sleep
import asyncio
