"""
Basic Knowledge Base Example

Shows how to create and manage knowledge bases (RAG configurations).
"""

from lyzr import Studio

# Initialize Studio
studio = Studio(api_key="your-api-key-here")

print("=" * 70)
print("KNOWLEDGE BASE - BASIC EXAMPLE")
print("=" * 70)

# Example 1: Create a knowledge base
print("\n1. Creating knowledge base...")
kb = studio.create_knowledge_base(
    name="customer_support",  # Must be lowercase with underscores only!
    description="Customer support documentation",
    vector_store="qdrant",  # Typed: qdrant, weaviate, pg_vector, milvus, neptune
    embedding_model="text-embedding-3-large",
    llm_model="gpt-4o",
)

print(f"✓ Knowledge base created: {kb.name}")
print(f"  ID: {kb.id}")
print(f"  Collection: {kb.collection_name}")
print(f"  Vector Store: {kb.vector_store_provider}")
print(f"  Embedding Model: {kb.embedding_model}")

# Example 2: Add documents - Website
print("\n2. Adding website content...")
kb.add_website(url="https://help.openai.com", max_pages=5, max_depth=1)
print("✓ Website content added")

# Example 3: Add documents - Raw text
print("\n3. Adding raw text...")
kb.add_text(text="Business hours: Monday-Friday 9am-5pm EST", source="business_hours.txt")
kb.add_text(
    text="Refund policy: 30-day money-back guarantee on all products", source="refund_policy.txt"
)
print("✓ Text documents added")

# Example 4: Query the knowledge base
print("\n4. Querying knowledge base...")
results = kb.query(query="What are the business hours?", top_k=3, retrieval_type="basic")

print(f"✓ Found {len(results)} results:")
for i, result in enumerate(results, 1):
    print(f"  {i}. Score: {result.score:.3f}")
    print(f"     Source: {result.source}")
    print(f"     Text: {result.text[:100]}...")

# Example 5: List all knowledge bases
print("\n5. Listing all knowledge bases...")
all_kbs = studio.list_knowledge_bases()
print(f"✓ Found {len(all_kbs)} knowledge base(s):")
for kb_item in all_kbs:
    print(f"  - {kb_item.name} (ID: {kb_item.id[:20]}...)")

# Example 6: Get a specific knowledge base
print("\n6. Fetching knowledge base by ID...")
fetched_kb = studio.get_knowledge_base(kb.id)
print(f"✓ Knowledge base fetched: {fetched_kb.name}")

# Example 7: List documents in KB
print("\n7. Listing documents in knowledge base...")
docs = kb.list_documents()
print(f"✓ Found {len(docs)} document(s)")
for doc in docs[:3]:  # Show first 3
    print(f"  - {doc.source} (ID: {doc.id[:20]}...)")

# Example 8: Update knowledge base
print("\n8. Updating knowledge base...")
kb = kb.update(description="Updated customer support documentation")
print(f"✓ Knowledge base updated")
print(f"  New description: {kb.description}")

# Example 9: Using knowledge_bases module directly
print("\n9. Using knowledge_bases module directly...")
another_kb = studio.knowledge_bases.create(
    name="product_docs_v2", description="Product documentation", vector_store="qdrant"
)
print(f"✓ KB created via module: {another_kb.name}")

# Example 10: Cleanup
print("\n10. Cleanup - Deleting knowledge bases...")
kb.delete()
another_kb.delete()
print("✓ Knowledge bases deleted")

print("\n" + "=" * 70)
print("✅ All basic KB examples completed!")
print("=" * 70)
