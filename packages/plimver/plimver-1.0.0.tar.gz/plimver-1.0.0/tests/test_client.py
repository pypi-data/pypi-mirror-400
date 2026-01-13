"""
Plimver SDK - Test Suite

Run: pytest tests/test_client.py -v
"""

import pytest
import respx
import httpx
import json

from plimver import (
    Plimver, 
    AsyncPlimver, 
    PlimverError, 
    Message,
    ChatResponse,
    Usage,
    Document
)


class TestPlimver:
    """Test synchronous Plimver client"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = Plimver(
            api_key="pk_test_12345",
            workspace_id="ws_test_abc",
            base_url="https://api.test.com"
        )
    
    def test_init_with_required_options(self):
        """Should create client with required options"""
        assert self.client is not None
        assert self.client.api_key == "pk_test_12345"
        assert self.client.workspace_id == "ws_test_abc"
    
    def test_init_without_api_key_raises(self):
        """Should raise error without api_key"""
        with pytest.raises(ValueError, match="api_key is required"):
            Plimver(api_key="", workspace_id="ws_test")
    
    def test_init_without_workspace_id_raises(self):
        """Should raise error without workspace_id"""
        with pytest.raises(ValueError, match="workspace_id is required"):
            Plimver(api_key="pk_test", workspace_id="")
    
    @respx.mock
    def test_chat_basic(self):
        """Should send basic chat request"""
        respx.post("https://api.test.com/api/v1/workspaces/ws_test_abc/chat").mock(
            return_value=httpx.Response(200, json={
                "choices": [{"message": {"content": "Hello back!"}}],
                "model": "gpt-4o",
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
                "x_metadata": {"provider": "openai", "routing_mode": "auto"}
            })
        )
        
        response = self.client.chat("Hello")
        
        assert response.text == "Hello back!"
        assert response.model == "gpt-4o"
    
    @respx.mock
    def test_chat_with_options(self):
        """Should include options in request"""
        route = respx.post("https://api.test.com/api/v1/workspaces/ws_test_abc/chat").mock(
            return_value=httpx.Response(200, json={
                "choices": [{"message": {"content": "Response"}}],
                "model": "gpt-4o-mini"
            })
        )
        
        self.client.chat(
            "Hello",
            mode="chat_only",
            model="gpt-4o-mini",
            temperature=0.5,
            user_id="user-123"
        )
        
        # Verify the request
        assert route.called
        request = route.calls[0].request
        body = json.loads(request.content)
        
        assert body["mode"] == "chat_only"
        assert body["model"] == "gpt-4o-mini"
        assert body["temperature"] == 0.5
    
    @respx.mock
    def test_chat_api_error(self):
        """Should raise error on API failure"""
        respx.post("https://api.test.com/api/v1/workspaces/ws_test_abc/chat").mock(
            return_value=httpx.Response(401, json={"error": "Invalid API key"})
        )
        
        with pytest.raises(PlimverError):
            self.client.chat("Hello")


class TestPlimverDocuments:
    """Test document operations"""
    
    def setup_method(self):
        self.client = Plimver(
            api_key="pk_test_12345",
            workspace_id="ws_test_abc",
            base_url="https://api.test.com"
        )
    
    @respx.mock
    def test_upload_document(self):
        """Should upload document"""
        respx.post("https://api.test.com/api/v1/workspaces/ws_test_abc/documents").mock(
            return_value=httpx.Response(200, json={
                "id": "doc-123",
                "source": "test.txt",
                "total_chunks": 1
            })
        )
        
        doc = self.client.documents.upload("Test content", source="test.txt")
        
        assert doc.source == "test.txt"
    
    @respx.mock
    def test_list_documents(self):
        """Should list documents"""
        respx.get("https://api.test.com/api/v1/workspaces/ws_test_abc/documents").mock(
            return_value=httpx.Response(200, json={
                "documents": [
                    {"id": "1", "source": "doc1.txt"},
                    {"id": "2", "source": "doc2.txt"}
                ]
            })
        )
        
        docs = self.client.documents.list()
        
        assert len(docs) == 2


class TestPlimverMemory:
    """Test memory operations"""
    
    def setup_method(self):
        self.client = Plimver(
            api_key="pk_test_12345",
            workspace_id="ws_test_abc",
            base_url="https://api.test.com"
        )
    
    @respx.mock
    def test_get_memory(self):
        """Should get memory for user"""
        respx.get(url__startswith="https://api.test.com/api/v1/workspaces/ws_test_abc/memory").mock(
            return_value=httpx.Response(200, json={
                "messages": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi!"}
                ]
            })
        )
        
        messages = self.client.memory.get("user-123")
        
        assert len(messages) == 2
    
    @respx.mock
    def test_clear_memory(self):
        """Should clear memory for user"""
        respx.delete(url__startswith="https://api.test.com/api/v1/workspaces/ws_test_abc/memory").mock(
            return_value=httpx.Response(200, json={"success": True})
        )
        
        # Should not raise
        self.client.memory.clear("user-123")


class TestPlimverError:
    """Test error handling"""
    
    def test_error_contains_details(self):
        """Should contain error details"""
        error = PlimverError("Test error", 401)
        
        assert error.message == "Test error"
        assert error.status == 401
        assert str(error) == "Test error"


class TestPlimverVision:
    """Test vision/multimodal"""
    
    def setup_method(self):
        self.client = Plimver(
            api_key="pk_test_12345",
            workspace_id="ws_test_abc",
            base_url="https://api.test.com"
        )
    
    @respx.mock
    def test_vision(self):
        """Should send vision request with image"""
        route = respx.post("https://api.test.com/api/v1/workspaces/ws_test_abc/chat").mock(
            return_value=httpx.Response(200, json={
                "choices": [{"message": {"content": "A cat sitting on a couch"}}],
                "model": "gpt-4o"
            })
        )
        
        response = self.client.vision("Describe this image", "https://example.com/cat.jpg")
        
        assert response.text == "A cat sitting on a couch"
        
        # Check that multimodal content was sent
        request = route.calls[0].request
        body = json.loads(request.content)
        messages = body.get("messages", [])
        
        assert len(messages) > 0
        user_content = messages[0].get("content")
        assert isinstance(user_content, list)
