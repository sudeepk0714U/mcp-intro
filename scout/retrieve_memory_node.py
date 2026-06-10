# scout/retrieve_memory_node.py

from scout.memory.episodic import EpisodicMemory

memory = EpisodicMemory()

async def retrieve_memory_node(state):

    latest_message = state["messages"][-1]

    query = latest_message.content

    memories = memory.search_similar(
        query=query,
        limit=5
    )

    state["retrieved_memories"] = memories

    return state