import os
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from langchain_core.prompts.prompt import PromptTemplate

load_dotenv()

CYPHER_GENERATION_TEMPLATE = """Task: Generate a Cypher statement to query a graph database.

CRITICAL INSTRUCTIONS:
1. DO NOT guess relationship names. ALWAYS use anonymous/blank relationships like `(a)-[]-(b)` to connect nodes. This ensures maximum recall.
2. Node labels are CASE-SENSITIVE (e.g., Error, Fix, Rule, BestPractice, Project).
3. NEVER restrict the direction of the relationship. Always use undirected edges.
4. ALWAYS use fuzzy matching. Example: `WHERE toLower(e.id) CONTAINS "flake8" OR toLower(e.symptom) CONTAINS "flake8"`.
5. RETURN the actual nodes (e.g., `RETURN a, b`) rather than guessing property names, so the QA agent gets the full JSON of the node.

Schema:
{schema}

Question: {question}
"""

QA_TEMPLATE = """You are a helpful engineering assistant answering questions based on a Knowledge Graph.
You will be provided with information extracted from the graph database.

Information:
{context}

Question: {question}

Instructions:
1. Use the provided Information to answer the question.
2. If the Information only partially answers the question, give the partial answer. Do not say "I don't know" if you have some useful facts.
3. If the Information is completely empty ([]), then you may say you don't know based on the context.
4. Format your answer nicely for an engineer to read.
"""

cypher_prompt = PromptTemplate(
    input_variables=["schema", "question"],
    template=CYPHER_GENERATION_TEMPLATE
)

qa_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=QA_TEMPLATE
)


def get_chain():
    graph = Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD"),
        database=os.getenv("NEO4J_DATABASE", "neo4j")
    )
    graph.refresh_schema()

    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    return GraphCypherQAChain.from_llm(
        cypher_llm=llm,
        qa_llm=llm,
        graph=graph,
        verbose=True,
        cypher_prompt=cypher_prompt,
        qa_prompt=qa_prompt,
        allow_dangerous_requests=True,
        return_direct=False
    )


@tool
def graph_memory(question: str) -> str:
    """Query Scout's long-term memory stored in Neo4j knowledge graph.
    Use this tool when:
    - User reports an error you have seen before
    - User asks about a previous fix or solution
    - User asks about best practices for Docker, CI/CD, EC2, flake8
    - You need context about past deployments or infrastructure
    - You are about to suggest something — check memory first
    Input should be a natural language question about the error or topic.
    """
    try:
        chain = get_chain()
        response = chain.invoke({"query": question})
        return response["result"]
    except Exception as e:
        return f"Memory query failed: {str(e)}"