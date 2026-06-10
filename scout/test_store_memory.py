from scout.memory.episodic import EpisodicMemory

memory = EpisodicMemory()

memory.store_episode(
    task="Fix FastAPI CORS issue",

    error="frontend blocked by CORS",

    actions=[
        "added CORSMiddleware",
        "allowed localhost:3000"
    ],

    outcome="frontend connected"
)

print("Memory stored successfully.")