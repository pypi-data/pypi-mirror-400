from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from tools.ambiguity_resolver import resolve_ambiguity
from tools.high_level_decomposer import decompose_high_level
from tools.subtask_decomposer import decompose_subtasks

from typing import Annotated

from typing_extensions import TypedDict


# Define the graph state schema
def update_state(state, key, value):
    state[key] = value
    return state


def is_ambiguous(state):
    return state["clarified_instruction"] is None


def is_clarified(state):
    return state["clarified_instruction"] is not None


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


builder = StateGraph(State)

# Nodes
builder.add_node("resolve_ambiguity", resolve_ambiguity)

builder.add_conditional_edges("resolve_ambiguity",
                              {
                                  "clarified": is_clarified,
                                  "ambiguous": is_ambiguous
                              })
builder.add_edge("clarified", "decompose_high_level")
builder.add_edge("ambiguous", "resolve_ambiguity")

builder.add_node("decompose_high_level", decompose_high_level)
builder.add_node("decompose_subtasks", decompose_subtasks)
builder.add_node("end", lambda state: state)

# Edges
builder.set_entry_point("resolve_ambiguity")
builder.add_edge("resolve_ambiguity", "decompose_high_level")
builder.add_edge("decompose_high_level", "decompose_subtasks")
builder.add_edge("decompose_subtasks", "end")

graph = builder.compile()
