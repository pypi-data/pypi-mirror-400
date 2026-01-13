"""
Plimver SDK - Async Usage Examples

Run: python examples/async_example.py
"""

import asyncio
import os
from plimver import AsyncPlimver, Message


async def main():
    """Async examples"""
    
    # Initialize async client
    async with AsyncPlimver(
        api_key=os.environ.get("PLIMVER_API_KEY", "pk_live_your_key"),
        workspace_id=os.environ.get("PLIMVER_WORKSPACE_ID", "ws_your_workspace"),
        base_url=os.environ.get("PLIMVER_BASE_URL", "https://api.plimvr.tech")
    ) as client:
        
        # Basic async chat
        print("=== Async Basic Chat ===")
        response = await client.chat("Hello! How are you?")
        print(f"Response: {response.text}")
        
        # Parallel requests
        print("\n=== Parallel Requests ===")
        questions = [
            "What is Python?",
            "What is JavaScript?",
            "What is Rust?",
        ]
        
        # Send all requests in parallel
        tasks = [client.chat(q, mode="chat_only") for q in questions]
        responses = await asyncio.gather(*tasks)
        
        for q, r in zip(questions, responses):
            print(f"Q: {q}")
            print(f"A: {r.text[:100]}...")
            print()
        
        # Async streaming
        print("=== Async Streaming ===")
        print("Streaming: ", end="", flush=True)
        
        async for chunk in client.stream_chat("Tell me a fun fact"):
            if chunk.content:
                print(chunk.content, end="", flush=True)
            if chunk.done:
                print("\n[Done]")
        
        # Async document operations
        print("\n=== Async Document Operations ===")
        
        # Upload multiple documents in parallel
        docs_to_upload = [
            ("Python is a high-level programming language.", "python.txt"),
            ("JavaScript runs in the browser.", "javascript.txt"),
            ("Rust is a systems programming language.", "rust.txt"),
        ]
        
        upload_tasks = [
            client.documents.upload(text, source=src) 
            for text, src in docs_to_upload
        ]
        uploaded = await asyncio.gather(*upload_tasks)
        print(f"Uploaded {len(uploaded)} documents in parallel")
        
        # List documents
        docs = await client.documents.list()
        print(f"Total documents: {len(docs)}")
        
        # Query with RAG
        print("\n=== Async RAG Query ===")
        response = await client.chat(
            "What programming languages are mentioned in my documents?",
            mode="rag_only"
        )
        print(f"RAG Response: {response.text}")
        
        # Cleanup - delete uploaded docs
        delete_tasks = [
            client.documents.delete(src) 
            for _, src in docs_to_upload
        ]
        await asyncio.gather(*delete_tasks)
        print("Cleaned up test documents")
        
        print("\n✅ Async examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
