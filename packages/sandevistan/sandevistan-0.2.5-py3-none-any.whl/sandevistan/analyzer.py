"""Core crash analysis logic using LangGraph and Google Gemini Flash."""

from pathlib import Path
from typing import TypedDict

from google import genai
from langgraph.graph import StateGraph, END


class AgentState(TypedDict):
    """Agent state for crash analysis."""
    file_paths: list[Path]
    file_contents: dict[str, str]
    analysis: str
    api_key: str
    model: str


def read_ips_files(state: AgentState) -> AgentState:
    """Read specified IPS files."""
    file_paths = state["file_paths"]

    file_contents = {}
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as f:
            file_contents[file_path.name] = f.read()

    state["file_contents"] = file_contents
    return state


def analyze_crashes(state: AgentState) -> AgentState:
    """Analyze crash files using Google Gemini."""
    client = genai.Client(api_key=state["api_key"])

    analysis_results = []

    for filename, content in state["file_contents"].items():
        prompt = f"""Analyze this Apple IPS crash file and explain the crash reason in plain language.

File: {filename}

{content}

Provide a concise explanation covering:
1. What crashed
2. Why it crashed (root cause)
3. Key technical details"""

        response = client.models.generate_content(
            model=state["model"],
            contents=prompt
        )
        analysis_results.append(f"\n{'='*80}\nFile: {filename}\n{'='*80}\n{response.text}\n")

    state["analysis"] = "\n".join(analysis_results)
    return state


def build_agent():
    """Build the crash analyzer agent graph."""
    workflow = StateGraph(AgentState)

    workflow.add_node("read_files", read_ips_files)
    workflow.add_node("analyze", analyze_crashes)

    workflow.set_entry_point("read_files")
    workflow.add_edge("read_files", "analyze")
    workflow.add_edge("analyze", END)

    return workflow.compile()


def analyze_crash_files(file_paths: list[Path], api_key: str, model: str) -> dict:
    """
    Main analysis function to be called by CLI.

    Args:
        file_paths: List of Path objects pointing to .ips files to analyze
        api_key: Google API key for Gemini
        model: Gemini model name

    Returns:
        Dictionary containing analysis results and file count
    """
    agent = build_agent()

    initial_state = {
        "file_paths": file_paths,
        "file_contents": {},
        "analysis": "",
        "api_key": api_key,
        "model": model
    }

    result = agent.invoke(initial_state)
    return result
