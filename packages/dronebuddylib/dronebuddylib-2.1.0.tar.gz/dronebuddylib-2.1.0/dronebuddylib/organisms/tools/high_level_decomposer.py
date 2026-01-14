def decompose_high_level(state):
    instruction = state["clarified_instruction"]

    # Dummy logic
    tasks = []
    if "sandwich" in instruction:
        tasks.append("Make a sandwich")
    if "send an update" in instruction:
        tasks.append("Send update to sister")

    state["high_level_tasks"] = tasks
    state["conversation"].append(f"I'll do these: {', '.join(tasks)}. Okay?")
    return state
