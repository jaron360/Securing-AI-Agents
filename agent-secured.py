import json
from strands import Agent, tool
from strands_tools import calculator, current_time
from strands.models import BedrockModel


# Create a Bedrock model with guardrail configuration
bedrock_model = BedrockModel(
    model_id="global.anthropic.claude-sonnet-4-5-20250929-v1:0",
    guardrail_id="a14x0qqbnlnn",         # Your Bedrock guardrail ID
    guardrail_version="1",                    # Guardrail version
    guardrail_trace="enabled",             # Enable trace info for debugging
)

# Define a custom tool as a Python function using the @tool decorator
@tool
def letter_counter(word: str, letter: str) -> int:
    """
    Count occurrences of a specific letter in a word.

    Args:
        word (str): The input word to search in
        letter (str): The specific letter to count

    Returns:
        int: The number of occurrences of the letter in the word
    """
    if not isinstance(word, str) or not isinstance(letter, str):
        return 0

    if len(letter) != 1:
        raise ValueError("The 'letter' parameter must be a single character")

    return word.lower().count(letter.lower())

# Create an agent with tools from the community-driven strands-tools package
# as well as our custom letter_counter tool
agent = Agent(tools=[calculator, current_time, letter_counter], model=bedrock_model)

# Ask the user for input
print("Available tools: calculator, current time, letter counter")
message = input("What would you like to ask?: ")

response = agent(message)

# Handle potential guardrail interventions
if response.stop_reason == "guardrail_intervened":
    print("Content was blocked by guardrails, conversation context overwritten!")

print(f"Conversation: {json.dumps(agent.messages, indent=4)}")
