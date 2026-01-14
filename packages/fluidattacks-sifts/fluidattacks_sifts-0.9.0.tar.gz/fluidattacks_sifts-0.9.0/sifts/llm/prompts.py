from typing import TypedDict


class AgentPrompt(TypedDict):
    system: str
    instructions: str
    version: str


class AgentPrompts(TypedDict):
    vuln_strict: AgentPrompt
    vuln_loose: AgentPrompt
    lines_clarification: AgentPrompt
    classify: AgentPrompt


class Prompts(TypedDict):
    agents: AgentPrompts
