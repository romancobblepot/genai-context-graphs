"""Find out why long_term.search_entities returns nothing although entities exist.

Run from the course repo so it finds your .env:

    cd /workspaces/genai-context-graphs
    python diagnose_search.py

Read-only: prints index states, whether entities have embeddings, and search results
for several queries. Never prints credentials.
"""

import asyncio
import inspect
import os

from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j_agent_memory import ExtractionConfig, MemoryClient, MemorySettings
from neo4j_agent_memory.config import Neo4jConfig
from neo4j_agent_memory.memory.long_term import LongTermMemory

load_dotenv(os.path.join(os.getcwd(), ".env"))


def check_graph():
    driver = GraphDatabase.driver(
        os.environ["NEO4J_URI"],
        auth=(os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"]),
    )
    with driver.session(database=os.environ["NEO4J_DATABASE"]) as session:
        print("--- vector indexes ---")
        for r in session.run(
            "SHOW INDEXES YIELD name, type, state, populationPercent "
            "WHERE type = 'VECTOR' RETURN name, state, populationPercent"
        ):
            print(r["name"], r["state"], r["populationPercent"])
        print("--- do entities have embeddings? ---")
        for r in session.run(
            "MATCH (e:Entity) RETURN e.name AS name, "
            "e.embedding IS NOT NULL AS has_embedding, "
            "CASE WHEN e.embedding IS NULL THEN 0 ELSE size(e.embedding) END AS dims"
        ):
            print(r["name"], r["has_embedding"], r["dims"])
    driver.close()


async def check_search():
    print("--- search_entities signature ---")
    print(inspect.signature(LongTermMemory.search_entities))

    settings = MemorySettings(
        neo4j=Neo4jConfig(
            uri=os.environ["NEO4J_URI"],
            username=os.environ["NEO4J_USERNAME"],
            password=os.environ["NEO4J_PASSWORD"],
            database=os.environ["NEO4J_DATABASE"],
        ),
        extraction=ExtractionConfig(enable_spacy=False, enable_gliner=False),
    )
    params = inspect.signature(LongTermMemory.search_entities).parameters
    score_params = [p for p in params if "threshold" in p or "score" in p]

    async with MemoryClient(settings) as memory:
        print("--- default search ---")
        for query in ["Alex", "Alex Mercer", "Ridgeline Labs", "person who works at a lab"]:
            results = await memory.long_term.search_entities(query=query)
            print(repr(query), "->", [e.name for e in results])

        for p in score_params:
            print(f"--- search with {p}=0.0 ---")
            results = await memory.long_term.search_entities(query="Alex", **{p: 0.0})
            print([e.name for e in results])

        print("--- direct name lookup ---")
        found = await memory.long_term.get_entity_by_name("Alex Mercer")
        print(found.name if found else None)


if __name__ == "__main__":
    check_graph()
    asyncio.run(check_search())
