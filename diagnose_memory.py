"""Diagnose why search_entities returns nothing in the GraphAcademy module 3 challenge.

Run from the course repo so it finds your .env:

    cd /workspaces/genai-context-graphs
    python /path/to/diagnose_memory.py

Read-only: it prints node counts, entity names and extraction stats, never credentials.
"""

import asyncio
import os

from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j_agent_memory import ExtractionConfig, MemoryClient, MemorySettings
from neo4j_agent_memory.config import Neo4jConfig

ENV_PATH = os.path.join(os.getcwd(), ".env")
SCRIPT_PATH = os.path.join(os.getcwd(), "3_long_term.py")

load_dotenv(ENV_PATH)


def check_setup():
    print("--- setup ---")
    print(".env found:", os.path.exists(ENV_PATH))
    print("OPENAI_API_KEY set:", bool(os.environ.get("OPENAI_API_KEY")))
    if os.path.exists(SCRIPT_PATH):
        with open(SCRIPT_PATH) as f:
            print("3_long_term.py calls wait_for_extraction:", "wait_for_extraction" in f.read())
    else:
        print("3_long_term.py not found in", os.getcwd())


def check_graph():
    driver = GraphDatabase.driver(
        os.environ["NEO4J_URI"],
        auth=(os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"]),
    )
    with driver.session(database=os.environ["NEO4J_DATABASE"]) as session:
        print("--- node counts by label ---")
        for r in session.run("MATCH (n) RETURN labels(n) AS labels, count(*) AS n"):
            print(r["labels"], r["n"])
        print("--- nodes with a name ---")
        for r in session.run(
            "MATCH (e) WHERE e.name IS NOT NULL RETURN labels(e) AS labels, e.name AS name LIMIT 20"
        ):
            print(r["labels"], r["name"])
    driver.close()


async def check_memory():
    settings = MemorySettings(
        neo4j=Neo4jConfig(
            uri=os.environ["NEO4J_URI"],
            username=os.environ["NEO4J_USERNAME"],
            password=os.environ["NEO4J_PASSWORD"],
            database=os.environ["NEO4J_DATABASE"],
        ),
        extraction=ExtractionConfig(enable_spacy=False, enable_gliner=False),
    )
    async with MemoryClient(settings) as memory:
        print("--- extraction stats ---")
        print(await memory.long_term.get_extraction_stats())
        print("--- lookup by name: Alex Mercer ---")
        print(await memory.long_term.get_entity_by_name("Alex Mercer"))


if __name__ == "__main__":
    check_setup()
    check_graph()
    asyncio.run(check_memory())
