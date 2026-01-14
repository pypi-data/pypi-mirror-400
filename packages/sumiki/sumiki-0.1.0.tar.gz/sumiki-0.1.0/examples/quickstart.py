"""
Quickstart example for Lyzr Agent SDK

This example shows the basic usage of creating, managing, and running agents.
"""

from lyzr import Studio

# Initialize Studio with your API key
studio = Studio(api_key="your-api-key-here")
# Or use environment variable: export LYZR_API_KEY="your-api-key"
# studio = Studio()

print("=" * 60)
print("LYZR AGENT SDK - QUICKSTART EXAMPLE")
print("=" * 60)

# Example 1: Create a simple agent
print("\n1. Creating agent...")
agent = studio.create_agent(
    name="Customer Support Bot",
    provider="openai/gpt-4o-mini",  # Format: provider/model
    description="A helpful customer support assistant",
    agent_role="You are a friendly customer support agent",
    agent_goal="Help customers with their questions efficiently",
    agent_instructions="Help customers with their questions efficiently",
    temperature=0.7,
)

print(f"✓ Agent created: {agent.name}")
print(f"  ID: {agent.id}")
print(f"  Model: {agent.provider_id}/{agent.model}")
print(f"  Temperature: {agent.temperature}")

# Example 2: Run the agent (non-streaming)
print("\n2. Running agent (non-streaming)...")
response = agent.run("What are your business hours?")
print(f"✓ Agent response: {response.response}")
print(f"  Session ID: {response.session_id}")

# Example 3: Run with explicit session
print("\n3. Running with explicit session...")
session_id = "my_session_123"
response = agent.run("Do you offer refunds?", session_id=session_id)
print(f"✓ Agent response: {response.response}")
print(f"  Session ID: {response.session_id}")

# Example 4: Streaming response
print("\n4. Running agent (streaming)...")
print("Agent response (streamed): ", end="", flush=True)
for chunk in agent.run("Tell me a short joke", stream=True):
    print(chunk.content, end="", flush=True)
print()  # New line

# Example 5: List all agents
print("\n5. Listing all agents...")
agents = studio.list_agents()
print(f"✓ Found {len(agents)} agent(s):")
for ag in agents:
    print(f"  - {ag.name} (ID: {ag.id[:16]}...)")

# Example 6: Get a specific agent
print(f"\n6. Fetching agent by ID...")
fetched_agent = studio.get_agent(agent.id)
print(f"✓ Agent fetched: {fetched_agent.name}")
# Fetched agent is also smart!
response = fetched_agent.run("Hello!")
print(f"  Can run immediately: {response.response[:50]}...")

# Example 7: Update agent using agent.update()
print("\n7. Updating agent via agent.update()...")
agent = agent.update(temperature=0.5, description="Updated support bot")
print(f"✓ Agent updated")
print(f"  New temperature: {agent.temperature}")
print(f"  New description: {agent.description}")

# Example 8: Clone an agent
print("\n8. Cloning agent...")
cloned = agent.clone("Customer Support Bot (Clone)")
print(f"✓ Cloned agent created: {cloned.name}")
print(f"  Original ID: {agent.id}")
print(f"  Clone ID: {cloned.id}")

# Example 9: Using the agents module directly
print("\n9. Using agents module directly...")
another_agent = studio.agents.create(
    name="Sales Assistant",
    provider="anthropic/claude-sonnet-4-5",
    temperature=0.8,
)
print(f"✓ Agent created via module: {another_agent.name}")

# Example 10: Delete agent using agent.delete()
print("\n10. Deleting cloned agent via agent.delete()...")
success = cloned.delete()
print(f"✓ Agent deleted: {success}")

# Example 11: Bulk delete
print("\n11. Bulk deleting remaining agents...")
studio.bulk_delete_agents([agent.id, another_agent.id])
print("✓ Agents deleted in bulk")

print("\n" + "=" * 60)
print("✅ All examples completed successfully!")
print("=" * 60)
