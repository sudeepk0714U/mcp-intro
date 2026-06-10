from langchain_openai import ChatOpenAI
import json


llm = ChatOpenAI(
    model="gpt-4.1-mini-2025-04-14",
    temperature=0
)


def reflect_on_execution(
    user_query,
    assistant_response,
    tool_outputs=None
):

    prompt = f"""
You are an autonomous engineering reflection system.

Analyze the following execution.

USER REQUEST:
{user_query}

ASSISTANT RESPONSE:
{assistant_response}

TOOL OUTPUTS:
{tool_outputs}

Your tasks:

1. Identify the core engineering issue
2. Identify reusable debugging knowledge
3. Extract useful recovery strategies
4. Decide whether this memory is useful long-term

Return ONLY valid JSON.

JSON FORMAT:

{{
    "should_store": true,
    "task": "...",
    "error": "...",
    "actions": ["...", "..."],
    "outcome": "...",
    "success": true
}}
"""

    response = llm.invoke(prompt)

    content = response.content.strip()

    try:
        return json.loads(content)

    except Exception:

        print("Reflection parsing failed.")

        return {
            "should_store": False
        }