import logging
from copy import copy

from agents import Agent, ModelSettings, Runner
from agents import FunctionTool as AgentsFunctionTool
from agents.exceptions import MaxTurnsExceeded
from agents.usage import Usage as AgentsUsage
from openai.types.shared.reasoning import Reasoning

from sifts.analysis.tools import (
    GET_FUNCTION_BY_ID_TOOL,
    SEARCH_CALLS_TOOL,
    SEARCH_FUNCTION_TOOL,
)
from sifts.analysis.types import (
    FunctionTool,
    TreeExecutionContext,
    Usage,
    VulnerabilityAssessment,
)
from sifts.llm.config_data import MODEL_PARAMETERS

TOOLS: list[FunctionTool] = [
    SEARCH_FUNCTION_TOOL,
    GET_FUNCTION_BY_ID_TOOL,
    # SEARCH_ANNOTATIONS_TOOL,
    SEARCH_CALLS_TOOL,
    # SEARCH_CLASSES_TOOL,
    # SEARCH_FIELDS_TOOL,
    # SEARCH_IDENTIFIERS_TOOL,
    # SEARCH_IMPORTS_TOOL,
    # SEARCH_LITERALS_TOOL,
    # SEARCH_METHODS_TOOL,
    # SEARCH_NAMESPACES_TOOL,
]
TOOLS_BY_NAME: dict[str, FunctionTool] = {tool.name: tool for tool in TOOLS}
LOGGER = logging.getLogger(__name__)
_MAX_CONVERSE_TURNS = 10

AGENT = Agent(
    name="Vulnerability Assessment",
    instructions=MODEL_PARAMETERS["prompts"]["agents"]["vuln_strict"]["system"],
    model="gpt-5-mini",
    output_type=VulnerabilityAssessment,
    model_settings=ModelSettings(
        reasoning=Reasoning(effort="low"),
        parallel_tool_calls=True,
        verbosity="low",
    ),
    tools=[
        AgentsFunctionTool(
            name=tool.name,
            description=tool.description,
            on_invoke_tool=tool.on_invoke_tool,
            params_json_schema=tool.params_json_schema,
            strict_json_schema=False,
        )
        for tool in TOOLS
    ],
)


async def invoke_agent_gpt(
    user_question: str,
    context: TreeExecutionContext,
) -> tuple[VulnerabilityAssessment | None, Usage]:
    runner = Runner()
    context = copy(context)
    context.metadata = context.metadata or {}
    context.metadata["id_obtained"] = []
    try:
        response = await runner.run(AGENT, user_question, context=context, max_turns=20)
    except MaxTurnsExceeded:
        LOGGER.exception("Error running agent: %s", user_question)
        return None, Usage(
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            cost=0,
        )

    return response.final_output_as(VulnerabilityAssessment), Usage(
        prompt_tokens=response.context_wrapper.usage.input_tokens,
        completion_tokens=response.context_wrapper.usage.output_tokens,
        total_tokens=response.context_wrapper.usage.total_tokens,
        cost=costo_gpt5_mini(response.context_wrapper.usage),
    )


def costo_gpt5_mini(usage: AgentsUsage) -> float:
    precio_input = 0.25
    precio_cached_input = 0.025
    precio_output = 2.00

    input_tokens = usage.input_tokens

    cached = usage.input_tokens_details.cached_tokens

    output_tokens = usage.output_tokens

    no_cache = input_tokens - cached
    no_cache = max(no_cache, 0)

    costo_input_no_cache = no_cache * (precio_input / 1_000_000)
    costo_input_cached = cached * (precio_cached_input / 1_000_000)

    costo_output = output_tokens * (precio_output / 1_000_000)

    return costo_input_no_cache + costo_input_cached + costo_output
