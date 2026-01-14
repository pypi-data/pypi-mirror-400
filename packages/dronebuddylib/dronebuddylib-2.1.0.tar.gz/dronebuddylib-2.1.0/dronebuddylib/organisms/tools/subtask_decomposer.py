def decompose_subtasks(state):
    tasks = state["high_level_tasks"]
    subtasks = []

    for task in tasks:
        if task == "Make a sandwich":
            subtasks.extend([
                {"action": "go_to_kitchen"},
                {"action": "find_bread"},
                {"action": "add_fillings"},
                {"action": "assemble_sandwich"}
            ])
        elif task == "Send update to sister":
            subtasks.extend([
                {"action": "compose_message", "content": "I made a sandwich"},
                {"action": "send_message", "to": "sister"}
            ])

    state["subtasks"] = subtasks
    state["conversation"].append("I'm ready to do these actions.")
    return state
