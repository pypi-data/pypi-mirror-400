import pkg_resources
from langgraph.prebuilt import create_react_agent
import openai

from langchain.tools import tool


@tool
def resolve_ambiguity_tool(user_input: str, capabilities: str) -> str:
    """
    Resolve ambiguity in a user instruction based on device capabilities.
    Returns a clarified instruction.
    """
    prompt = f"""You are a helpful assistant for a blind user. The user said: "{user_input}".
The device can: {capabilities}. What clarifying questions would you ask? 
Once resolved, provide the clarified instruction in plain English."""

    prompt = load_prompt().replace("{capabilities}", capabilities).replace("{instruction}", user_input)
    return call_llm(prompt)


def load_prompt():
    """
    Load the prompt for resolving ambiguity in task instructions.

    Returns:
        str: The loaded prompt.
    """

    prompt_path = pkg_resources.resource_filename(__name__, "decomposer_ambiguity_prompt.txt")
    with open(prompt_path, "r") as file:
        prompt = file.read()

    return prompt


def resolve_ambiguity(state):
    """
    Resolves ambiguity in the task instruction by providing a clear and concise response.

    Args:
        task_instruction (str): The task instruction that needs to be resolved.

    Returns:
        str: A clear and concise response to the task instruction.
    """

    instruction = state["user_input"]
    capabilities = state["device_capabilities"]
    prompt_path = pkg_resources.resource_filename(__name__, "decomposer_ambiguity_prompt.txt")
    with open(prompt_path, "r") as file:
        prompt = file.read()
    prompt = prompt.replace("{capabilities}", capabilities).replace("{instruction}", instruction)
    response = call_llm(prompt)


def call_llm(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response["choices"][0]["message"]["content"]


def create_decomposing_agent():
    """
    Creates a decomposing agent that can decompose tasks into subtasks.

    Returns:
        DecomposingAgent: An instance of the DecomposingAgent class.
    """

    decompose_agent = create_react_agent(
        model="anthropic:claude-3-7-sonnet-latest",
        tools=[resolve_ambiguity_tool],
        prompt="You are a helpful assistant"
    )
    return decompose_agent


if __name__ == "__main__":
    # Example usage
    agent = create_decomposing_agent()

    # Use the resolve_ambiguity_tool to clarify the user input
    agent.invoke({
        "input": "Can you go see who's at the window?"
    })
