"""
Example: Structured Responses with Pydantic Models

This example demonstrates how to use Pydantic models to get structured,
type-safe responses from agents.
"""

from lyzr import Studio
from pydantic import BaseModel, Field
from typing import Literal, List

# Initialize Studio
studio = Studio(api_key="your-api-key-here")

print("=" * 70)
print("STRUCTURED RESPONSES EXAMPLE")
print("=" * 70)

# Example 1: Simple Enum Response
print("\n1. Simple Enum Response (Pass/Fail)")
print("-" * 70)


class PassFailResult(BaseModel):
    """Test result with Pass or Fail"""

    Response: Literal["Pass", "Fail"] = Field(description="Test result: Pass or Fail")


agent1 = studio.create_agent(
    name="Test Agent",
    provider="openai/gpt-4o",
    response_model=PassFailResult,
    agent_instructions="Evaluate tests and return Pass or Fail randomly as you like.",
    agent_goal="Your goal is to pass the test",
    temperature=0.7,
)

print(f"✓ Agent created: {agent1.name}")
print(f"  Response format: {agent1.response_format['type']}")

# Run and get typed response
result: PassFailResult = agent1.run("Run the test")
print(f"✓ Result: {result.Response}")
print(f"  Type: {type(result).__name__}")


# Example 2: Complex Structured Response
print("\n2. Complex Structured Response (Task List)")
print("-" * 70)


class Task(BaseModel):
    """Single task"""

    title: str = Field(description="Task title")
    priority: Literal["high", "medium", "low"] = Field(description="Task priority")
    estimated_hours: int = Field(ge=1, le=100, description="Estimated hours to complete")


class TaskList(BaseModel):
    """List of tasks with metadata"""

    tasks: List[Task] = Field(description="List of tasks to complete")
    total_hours: int = Field(description="Total estimated hours")
    project_name: str = Field(description="Name of the project")


agent2 = studio.create_agent(
    name="Task Planner",
    provider="openai/gpt-4o",
    response_model=TaskList,
    agent_instructions=(
        "Break down projects into specific tasks. Return a structured list "
        "with task titles, priorities (high/medium/low), and estimated hours."
    ),
    temperature=0.7,
)

print(f"✓ Agent created: {agent2.name}")

# Run and get typed response
task_list: TaskList = agent2.run("Plan a website redesign project")
print(f"✓ Project: {task_list.project_name}")
print(f"  Total hours: {task_list.total_hours}")
print(f"  Tasks:")
for i, task in enumerate(task_list.tasks, 1):
    print(f"    {i}. {task.title} - {task.priority.upper()} ({task.estimated_hours}h)")


# Example 3: Streaming with Structured Response
print("\n3. Streaming with Structured Response")
print("-" * 70)


class StoryAnalysis(BaseModel):
    """Analysis of a story"""

    sentiment: Literal["positive", "negative", "neutral"] = Field(description="Overall sentiment")
    key_themes: List[str] = Field(description="Main themes in the story")
    word_count_estimate: int = Field(description="Estimated word count")


agent3 = studio.create_agent(
    name="Story Analyzer",
    provider="openai/gpt-4o",
    response_model=StoryAnalysis,
    agent_instructions=(
        "Analyze stories and return structured analysis with sentiment, "
        "key themes, and word count estimate."
    ),
    temperature=0.5,
)

print(f"✓ Agent created: {agent3.name}")
print("  Streaming response...")

# Stream and collect chunks
print("  Raw stream: ", end="", flush=True)
structured_result = None

for chunk in agent3.run(
    "Analyze this story: A young hero saves the village from darkness.", stream=True
):
    print(chunk.content, end="", flush=True)

    # Final chunk contains structured data
    if chunk.done and hasattr(chunk, "structured_data") and chunk.structured_data:
        structured_result = chunk.structured_data

print()  # New line

if structured_result:
    print(f"\n✓ Parsed Analysis:")
    print(f"  Sentiment: {structured_result.sentiment}")
    print(f"  Themes: {', '.join(structured_result.key_themes)}")
    print(f"  Word Count: {structured_result.word_count_estimate}")


# Example 4: Error Handling
print("\n4. Error Handling for Invalid Responses")
print("-" * 70)

from lyzr.exceptions import InvalidResponseError


class StrictFormat(BaseModel):
    """Very strict format"""

    exact_number: int = Field(ge=1, le=10, description="Must be between 1 and 10")


agent4 = studio.create_agent(
    name="Strict Agent",
    provider="openai/gpt-4o",
    response_model=StrictFormat,
    agent_instructions="Return a number between 1 and 10",
    temperature=0.7,
)

print(f"✓ Agent created: {agent4.name}")

try:
    # This might fail validation if agent returns invalid data
    result: StrictFormat = agent4.run("Give me a random number")
    print(f"✓ Valid result: {result.exact_number}")
except InvalidResponseError as e:
    print(f"✗ Validation failed: {e.message}")
    print(f"  Raw response: {e.response}")
    if e.validation_error:
        print(f"  Validation errors: {e.validation_error.errors()}")


# Example 5: Using structured agent fetched by ID
print("\n5. Fetching Existing Agent with Structured Response")
print("-" * 70)

# Fetch agent and add response_model
fetched = studio.get_agent(agent1.id, response_model=PassFailResult)
print(f"✓ Fetched agent: {fetched.name}")

# Can now use with structured responses
result: PassFailResult = fetched.run("Test again")
print(f"✓ Result: {result.Response}")


# Cleanup
print("\n6. Cleanup")
print("-" * 70)
studio.bulk_delete_agents([agent1.id, agent2.id, agent3.id, agent4.id])
print("✓ All test agents deleted")

print("\n" + "=" * 70)
print("✅ All structured response examples completed!")
print("=" * 70)
