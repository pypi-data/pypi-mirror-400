"""
Knowledge Base with Agent Integration

Shows how to use knowledge bases with agents at runtime.
"""

from lyzr import Studio

# Initialize Studio
studio = Studio(api_key="your-api-key-here")

print("=" * 70)
print("KNOWLEDGE BASE + AGENT INTEGRATION")
print("=" * 70)

# Step 1: Create knowledge bases
print("\n1. Creating knowledge bases...")

# KB for product information
products_kb = studio.create_knowledge_base(
    name="products_kb", description="Product information and specifications", vector_store="qdrant"
)

# KB for policies
policies_kb = studio.create_knowledge_base(
    name="policies_kb", description="Company policies and procedures", vector_store="qdrant"
)

print(f"✓ Created: {products_kb.name}")
print(f"✓ Created: {policies_kb.name}")

# Step 2: Add documents to knowledge bases
print("\n2. Adding documents to knowledge bases...")

# Add to products KB
products_kb.add_text(
    text="Product X: High-performance laptop. Price: $1,299. Specs: 16GB RAM, 512GB SSD, Intel i7",
    source="product_x.txt",
)
products_kb.add_text(
    text="Product Y: Budget-friendly tablet. Price: $399. Specs: 4GB RAM, 64GB storage, 10-inch display",
    source="product_y.txt",
)

# Add to policies KB
policies_kb.add_text(
    text="Refund Policy: 30-day money-back guarantee on all products. No questions asked.",
    source="refund_policy.txt",
)
policies_kb.add_text(
    text="Shipping Policy: Free shipping on orders over $50. Standard delivery 3-5 business days.",
    source="shipping_policy.txt",
)

print("✓ Documents added to both KBs")

# Step 3: Create agent (NO KB connection here!)
print("\n3. Creating agent...")
agent = studio.create_agent(
    name="Customer Support Agent",
    provider="openai/gpt-4o-mini",
    agent_instructions="You are a helpful customer support agent. Use the provided knowledge bases to answer questions accurately.",
    temperature=0.3,
)
print(f"✓ Agent created: {agent.name}")

# Step 4: Run agent WITHOUT knowledge base
print("\n4. Running agent WITHOUT knowledge base...")
response_without_kb = agent.run("What products do you offer?")
print(f"✓ Response (no KB): {response_without_kb.response[:100]}...")

# Step 5: Run agent WITH single knowledge base
print("\n5. Running agent WITH knowledge base (products)...")
response_with_kb = agent.run(
    "What products do you offer and what are their prices?",
    knowledge_bases=[products_kb],  # ← KB passed at runtime!
)
print(f"✓ Response (with products KB):")
print(f"  {response_with_kb.response}")

# Step 6: Run agent with MULTIPLE knowledge bases
print("\n6. Running agent with MULTIPLE knowledge bases...")
response_multi_kb = agent.run(
    "What is your refund policy and shipping policy?",
    knowledge_bases=[products_kb, policies_kb],  # Multiple KBs!
)
print(f"✓ Response (with both KBs):")
print(f"  {response_multi_kb.response}")

# Step 7: Custom KB configuration per query
print("\n7. Using custom KB configuration...")
response_custom = agent.run(
    "Tell me about Product X and its refund policy",
    knowledge_bases=[
        products_kb.with_config(top_k=5, score_threshold=0.7),
        policies_kb.with_config(top_k=2, retrieval_type="basic"),
    ],
)
print(f"✓ Response (custom config):")
print(f"  {response_custom.response}")

# Step 8: Query KB directly (without agent)
print("\n8. Querying knowledge base directly...")
query_results = products_kb.query("laptop specs", top_k=2)
print(f"✓ Direct KB query results:")
for result in query_results:
    print(f"  Score: {result.score:.3f} | Source: {result.source}")
    print(f"  Text: {result.text[:80]}...")

# Step 9: Different sessions with same agent and KB
print("\n9. Using different sessions...")
session1 = "customer_alice_001"
session2 = "customer_bob_002"

response1 = agent.run("What is Product X?", session_id=session1, knowledge_bases=[products_kb])
print(f"✓ Session {session1[:15]}...: {response1.response[:60]}...")

response2 = agent.run(
    "What is the shipping policy?", session_id=session2, knowledge_bases=[policies_kb]
)
print(f"✓ Session {session2[:15]}...: {response2.response[:60]}...")

# Step 10: Cleanup
print("\n10. Cleanup...")
agent.delete()
products_kb.delete()
policies_kb.delete()
print("✓ Agent and knowledge bases deleted")

print("\n" + "=" * 70)
print("✅ KB + Agent integration examples completed!")
print("=" * 70)
print("\nKey Takeaway:")
print("  Knowledge bases are passed to agent.run() at RUNTIME,")
print("  not during agent creation. This allows:")
print("  - Dynamic KB selection per query")
print("  - Multiple KBs per query")
print("  - Custom retrieval config per query")
