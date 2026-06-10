# test_memory.py

from scout.memory.episodic import EpisodicMemory

memory = EpisodicMemory()

memory.store_episode(
    task="Fix Docker build",

    error="npm dependency conflict",

    actions=[
        "deleted package-lock.json",
        "reinstalled dependencies"
    ],

    outcome="Docker build successful",

    success=True
)

results = memory.search_similar(
    "Docker dependency issue"
)

print(results)