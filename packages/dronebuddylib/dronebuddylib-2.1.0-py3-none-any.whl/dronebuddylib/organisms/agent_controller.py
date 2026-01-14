from graph_config import graph

initial_state = {
    "user_instruction": "Make me a sandwich and send an update to my sister",
    "clarified_instruction": None,
    "high_level_tasks": None,
    "subtasks": None,
    "memory": {
        "device_capabilities": ["speech", "object_recognition", "messaging"],
        "known_contacts": ["sister"],
    },
    "conversation": []
}

# Run the graph
result = graph.invoke(initial_state)
print(result)
