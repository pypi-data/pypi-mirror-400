from pydantic_ai import Agent

translation_agent = Agent(
    "openai:gpt-4o-mini",
    instructions="Translate the given message from English to Spanish. Be concise and accurate.",
)


async def translate_to_spanish(message: str) -> str:
    result = await translation_agent.run(message)
    return result.output
