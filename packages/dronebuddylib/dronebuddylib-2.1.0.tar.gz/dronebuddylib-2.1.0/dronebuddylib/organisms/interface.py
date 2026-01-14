# streamlit_app.py
import streamlit as st
from graph_config import graph

if "state" not in st.session_state:
    st.session_state.state = {
        "user_instruction": None,
        "clarified_instruction": None,
        "high_level_tasks": None,
        "subtasks": None,
        "memory": {
            "device_capabilities": ["speech", "object_recognition", "messaging"],
            "known_contacts": ["sister"]
        },
        "conversation": []
    }

st.title("LangGraph Task Agent")

instruction = st.text_input("Your command:", key="input")

if st.button("Send") and instruction:
    st.session_state.state["user_instruction"] = instruction
    result = graph.invoke(st.session_state.state)
    st.session_state.state = result  # carry forward updated state
    for msg in result["conversation"]:
        st.chat_message("assistant").write(msg)

    if result["clarified_instruction"] and result["subtasks"]:
        st.success("Ready to execute these tasks.")
        st.json(result["subtasks"])
