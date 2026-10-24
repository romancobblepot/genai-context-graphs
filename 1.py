"""Module 2 challenge - build a conversation memory layer.

Complete the TODOs, then run:  python 2_short_term.py
"""

import asyncio
import os
from dotenv import load_dotenv
from neo4j_agent_memory import ExtractionConfig, MemoryClient, MemorySettings
from neo4j_agent_memory.config import Neo4jConfig

load_dotenv()

settings = MemorySettings(
    neo4j=Neo4jConfig(
        uri=os.environ["NEO4J_URI"],
        username=os.environ["NEO4J_USERNAME"],
        password=os.environ["NEO4J_PASSWORD"],
    ),
    # The extraction pipeline runs spaCy and GLiNER before falling back to the
    # language model. Those two need extra packages (and a GPU-sized download),
    # so this course uses the LLM stage on its own. Without this, every stored
    # message logs two extractor failures before it succeeds.
)

SESSION_ID = "graphacademy"

EXCHANGE = [
    ("user", "My name is Alex and I prefer concise answers."),
    ("assistant", "Noted, Alex. I will keep my answers short."),
    ("user", "What do you know about me?"),
]


async def main():
    async with MemoryClient(settings) as memory:
        await memory.short_term.add_message(
            session_id="user_123",
            role="user",
            content="Review Jessica Norris account for a credit limit increase"
        )

        sessions=memory.short_term.list_sessions()
        for s in sessions:
            print(s.session_id)

asyncio.run(main())
