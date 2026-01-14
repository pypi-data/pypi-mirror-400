from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

llm = ChatOpenAI(temperature=0)

template = """
You are an assistant helping a blind user. Your job is to resolve ambiguity in the instruction:
"{instruction}"

Based on the user's memory and device capabilities:
{context}

If any part is unclear, ask a clarifying question. If everything is clear, say "No ambiguity."

Respond with one short sentence.
"""

prompt = PromptTemplate.from_template(template)

def resolve_ambiguity(state):
    instruction = state["user_instruction"]
    context = f"Memory: {state['memory']}"

    input_prompt = prompt.format(instruction=instruction, context=context)
    response = llm.predict(input_prompt)

    if "No ambiguity" in response:
        state["clarified_instruction"] = instruction
    else:
        state["clarified_instruction"] = None
        state["conversation"].append(response)

    return state