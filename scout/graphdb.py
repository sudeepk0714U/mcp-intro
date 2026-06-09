import os
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph

load_dotenv()

# ============================================================
# Neo4j Initialization
# ============================================================
graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
    database=os.getenv("NEO4J_DATABASE")
)

# ============================================================
# Clear old graph
# ============================================================
graph.query("""
MATCH (n)
DETACH DELETE n
""")
print("Old graph deleted.")

# ============================================================
# Establish Schema Constraints (Ensures high-accuracy merges)
# ============================================================
print("Applying database unique constraints...")
constraints = [
    "CREATE CONSTRAINT FOR (p:Project) REQUIRE p.id IS UNIQUE",
    "CREATE CONSTRAINT FOR (e:Error) REQUIRE e.id IS UNIQUE",
    "CREATE CONSTRAINT FOR (f:Fix) REQUIRE f.id IS UNIQUE",
    "CREATE CONSTRAINT FOR (r:Rule) REQUIRE r.id IS UNIQUE",
    "CREATE CONSTRAINT FOR (b:BestPractice) REQUIRE b.id IS UNIQUE",
    "CREATE CONSTRAINT FOR (i:Infrastructure) REQUIRE i.id IS UNIQUE",
    "CREATE CONSTRAINT FOR (pl:Pipeline) REQUIRE pl.id IS UNIQUE"
]

for constraint in constraints:
    try:
        graph.query(constraint)
    except Exception as e:
        # Fails gracefully if constraints already exist in the Neo4j instance
        pass

# ============================================================
# Load Paragraph Memory File
# ============================================================
with open("agent_memory.txt", "r", encoding="utf-8") as f:
    text = f.read()

# ============================================================
# Chunking by Paragraph
# ============================================================
chunks = []
for paragraph in text.split("\n\n"):
    paragraph = paragraph.strip()
    if len(paragraph) > 50:
        chunks.append(
            Document(
                page_content=paragraph,
                metadata={"source": "agent_memory"}
            )
        )

print(f"Chunks created: {len(chunks)}")

# ============================================================
# LLM Configuration
# ============================================================
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0  # Deterministic parsing
)

# ============================================================
# High-Accuracy Graph Transformer Configuration
# ============================================================
transformer = LLMGraphTransformer(
    llm=llm,
    allowed_nodes=[
        "Error",
        "Fix",
        "Rule",
        "BestPractice",
        "File",
        "Infrastructure",
        "Tool",
        "Pipeline",
        "Project"
    ],
    allowed_relationships=[
        "HAS_FIX",
        "HAS_RULE",
        "HAS_CAUSE",
        "AFFECTS",
        "USES",
        "DEPENDS_ON",
        "TRIGGERS",
        "PART_OF",
        "BELONGS_TO",
        "SOLVES"
    ],
    # Forcing properties directly ensures unstructured text maps cleanly to attributes
    node_properties=["category", "symptom", "cause", "reason", "implementation"],
    relationship_properties=False
)

# ============================================================
# Graph Processing & Construction
# ============================================================
print("Generating graph documents via LLM...")
graph_documents = transformer.convert_to_graph_documents(chunks)
print(f"Generated graph documents: {len(graph_documents)}")

# ============================================================
# Data Storage
# ============================================================
print("Writing graph structures to Neo4j Instance...")
graph.add_graph_documents(
    graph_documents,
    baseEntityLabel=True,    # Dynamically maps nodes with a fallback baseline identifier
    include_source=True      # Maps structural linkages back to original Document text chunks
)
print("Graph data loading completed.")

# ============================================================
# Post-Processing Normalization (Fuzzy Match Prevention)
# ============================================================
print("Executing identifier normalization...")
normalization_queries = [
    "MATCH (e:Error) SET e.id = toLower(e.id)",
    "MATCH (f:Fix) SET f.id = toLower(f.id)",
    "MATCH (r:Rule) SET r.id = toLower(r.id)"
]
for query in normalization_queries:
    graph.query(query)

# ============================================================
# Refresh Schema Context
# ============================================================
graph.refresh_schema()

# ============================================================
# High-Accuracy System Knowledge Graph Audit
# ============================================================
print("\n===== RUNNING KNOWLEDGE GRAPH STRUCTURAL AUDIT =====")

validation_suite = {
    "Total Node Density": "MATCH (n) RETURN count(n) AS count",
    "Total Active Strategic Edges": "MATCH ()-[r]->() RETURN count(r) AS count",
    "Isolated Entity Check": "MATCH (n) WHERE NOT (n)-[]-() RETURN count(n) AS count",
    "Error-Resolution Core Mapping Matrix": """
        MATCH (e:Error)-[r1]->(f:Fix)
        OPTIONAL MATCH (e)-[r2]->(rule:Rule)
        RETURN e.id AS TargetError, type(r1) AS EdgeType, f.id AS FixAction, rule.id AS RuleViolated
        LIMIT 5
    """
}

for validation_name, cypher_query in validation_suite.items():
    print(f"\n[Audit Run] -> {validation_name}:")
    try:
        audit_result = graph.query(cypher_query)
        print(audit_result)
    except Exception as query_error:
        print(f"Audit metric failed execution: {str(query_error)}")