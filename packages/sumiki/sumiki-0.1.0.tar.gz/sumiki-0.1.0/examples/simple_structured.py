"""
Simple example of structured responses

Shows the most basic usage of Pydantic models for structured outputs.
"""

from lyzr import Studio
from pydantic import BaseModel, Field
from typing import Literal


# Define your response structure
class MathResult(BaseModel):
    """Structured math result"""

    question: str = Field(description="The original math question")
    answer: int = Field(description="The numerical answer")
    explanation: str = Field(description="Brief explanation of the solution")


# Initialize Studio
studio = Studio(api_key="your-api-key-here")

# Create agent with structured response
agent = studio.create_agent(
    name="Math Tutor",
    provider="openai/gpt-4o",
    response_model=MathResult,  # This is the key!
    agent_instructions="Solve math problems and return structured results",
    temperature=0.3,
)

print(f"Agent created: {agent.name}\n")

# Run agent - get typed Pydantic instance back
result: MathResult = agent.run("What is 15 + 27?")

# Type-safe access
print(f"Question: {result.question}")
print(f"Answer: {result.answer}")
print(f"Explanation: {result.explanation}")

# Cleanup
agent.delete()
print("\nAgent deleted")
