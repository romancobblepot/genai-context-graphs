"""Module 3 challenge - promote entities to long-term memory.

Complete the TODOs, then run:  python 3_long_term.py
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
        database=os.environ["NEO4J_DATABASE"]
    ),
    # The extraction pipeline runs spaCy and GLiNER before falling back to the
    # language model. Those two need extra packages (and a GPU-sized download),
    # so this course uses the LLM stage on its own. Without this, every stored
    # message logs two extractor failures before it succeeds.
    extraction=ExtractionConfig(enable_spacy=False, enable_gliner=False),
)

SESSION_ID = "graphacademy"

# Naming a person and an organization plainly gives the extraction pipeline
# something unambiguous to find.
MESSAGE = "I am Alex Mercer and I work at Ridgeline Labs."


async def main():
    async with MemoryClient(settings) as memory:
        conversation=await memory.short_term.add_message(session_id=SESSION_ID,role="user",content=MESSAGE)
        await memory.long_term.add_preference(category="communication",preference="Prefers concise answers")
        person, _ = await memory.long_term.add_entity(name="Alex", entity_type="PERSON")
        entities=await memory.long_term.search_entities(query="Alex",threshold=0.3)
        for entity in entities:
            print(entity.name)
asyncio.run(main())
