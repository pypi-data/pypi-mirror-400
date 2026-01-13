"""
Plimver SDK - Basic Usage Examples

Run: python examples/basic.py
"""

import os
from plimver import Plimver, Message

# Initialize client
client = Plimver(
    api_key=os.environ.get("PLIMVER_API_KEY", "pk_live_your_key"),
    workspace_id=os.environ.get("PLIMVER_WORKSPACE_ID", "ws_your_workspace"),
    base_url=os.environ.get("PLIMVER_BASE_URL", "https://api.plimvr.tech")
)


def basic_chat():
    """Simple chat example"""
    print("=== Basic Chat ===")
    
    response = client.chat("What is machine learning?")
    
    print(f"Response: {response.text}")
    print(f"Model: {response.model}")
    print(f"Tokens: {response.usage.total_tokens}")


def chat_with_options():
    """Chat with custom options"""
    print("\n=== Chat with Options ===")
    
    response = client.chat(
        "Explain quantum computing in simple terms",
        mode="chat_only",
        model="gpt-4o-mini",
        temperature=0.7,
        max_tokens=500,
        user_id="demo-user-123"
    )
    
    print(f"Response: {response.text[:200]}...")
    print(f"Provider: {response.provider}")


def conversation_history():
    """Multi-turn conversation"""
    print("\n=== Conversation History ===")
    
    response = client.chat_with_messages([
        Message(role="user", content="My favorite color is blue"),
        Message(role="assistant", content="Nice! Blue is a calming color."),
        Message(role="user", content="What is my favorite color?"),
    ])
    
    print(f"Response: {response.text}")


def streaming_chat():
    """Stream response tokens"""
    print("\n=== Streaming Chat ===")
    
    print("Streaming: ", end="", flush=True)
    
    for chunk in client.stream_chat("Tell me a short joke"):
        if chunk.content:
            print(chunk.content, end="", flush=True)
        if chunk.done:
            print("\n[Done]")


def vision_example():
    """Image analysis"""
    print("\n=== Vision (Image Analysis) ===")
    
    response = client.vision(
        "Describe what you see in this image",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/1200px-Cat03.jpg"
    )
    
    print(f"Description: {response.text[:300]}...")


def rag_mode():
    """RAG with document context"""
    print("\n=== RAG Mode ===")
    
    # Upload a document first
    client.documents.upload(
        "Plimver is an AI platform that provides unified access to 22+ LLM providers.",
        source="about-plimver.txt"
    )
    
    # Query with RAG
    response = client.chat("What is Plimver?", mode="rag_only")
    
    print(f"Response: {response.text}")
    print(f"Sources: {response.sources}")


def document_management():
    """Manage RAG documents"""
    print("\n=== Document Management ===")
    
    # List existing documents
    docs = client.documents.list()
    print(f"Found {len(docs)} documents")
    
    # Upload new document
    doc = client.documents.upload(
        "This is a test document for the Plimver SDK demo.",
        source="demo-doc.txt"
    )
    print(f"Uploaded: {doc.source}")
    
    # Delete document
    client.documents.delete("demo-doc.txt")
    print("Deleted demo document")


def memory_management():
    """Manage conversation memory"""
    print("\n=== Memory Management ===")
    
    # Get memory for a user
    messages = client.memory.list("demo-user-123", limit=10)
    print(f"Found {len(messages)} messages in memory")
    
    # Clear user memory (commented out for safety)
    # client.memory.clear("demo-user-123")
    # print("Cleared user memory")


def check_formats():
    """Check supported formats"""
    print("\n=== Supported Formats ===")
    
    formats = client.formats.all()
    print(f"Image formats: {len(formats.get('image', []))}")
    print(f"Audio formats: {len(formats.get('audio', []))}")
    print(f"Video formats: {len(formats.get('video', []))}")
    print(f"Document formats: {len(formats.get('document', []))}")
    
    # Get formats for specific model
    gpt4o_formats = client.formats.for_model("gpt-4o")
    print(f"\nGPT-4o supports: {gpt4o_formats}")


def main():
    """Run all examples"""
    try:
        basic_chat()
        chat_with_options()
        conversation_history()
        streaming_chat()
        # vision_example()  # Uncomment to test vision
        # rag_mode()        # Uncomment to test RAG
        document_management()
        memory_management()
        check_formats()
        
        print("\n✅ All examples completed!")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
