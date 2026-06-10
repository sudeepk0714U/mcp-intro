import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph
from langchain_neo4j import GraphCypherQAChain
from langchain_core.prompts.prompt import PromptTemplate


# Load environment variables (NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, OPENAI_API_KEY)
load_dotenv()


def main():
    print("🔌 Connecting to Neo4j and initializing LLM...")

    # 1. Initialize Graph Connection
    graph = Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD"),
        database=os.getenv("NEO4J_DATABASE", "neo4j")
    )

    # Refresh schema so the LLM knows exactly what nodes and properties exist
    graph.refresh_schema()

    # 2. Initialize the LLM
    # Using temperature=0 for the Cypher generation ensures strict, accurate database queries
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    # 1. Create a smarter prompt for the LLM Cypher Generator
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

    cypher_prompt = PromptTemplate(
        input_variables=["schema", "question"],
        template=CYPHER_GENERATION_TEMPLATE
    )

    # ==========================================
    # 2. THE HELPFUL QA SYNTHESIS PROMPT
    # ==========================================
    QA_TEMPLATE = """You are a helpful engineering assistant answering questions based on a Knowledge Graph.
    You will be provided with information extracted from the graph database.

    Information:
    {context}

    Question: {question}

    Instructions:
    1. Use the provided Information to answer the question. 
    2. If the Information only partially answers the question (e.g., provides ports but not the OS), give the partial answer! Do not say "I don't know" if you have some useful facts.
    3. If the Information is completely empty ([]), then you may say you don't know based on the context.
    4. Format your answer nicely for an engineer to read.
    """

    qa_prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=QA_TEMPLATE
    )

    # ==========================================
    # 3. INITIALIZE THE CHAIN WITH BOTH PROMPTS
    # ==========================================
    chain = GraphCypherQAChain.from_llm(
        cypher_llm=llm,
        qa_llm=llm,
        graph=graph,
        verbose=True,
        cypher_prompt=cypher_prompt,  # Overrides Cypher generation
        qa_prompt=qa_prompt,  # Overrides Answer synthesis
        allow_dangerous_requests=True,
        return_direct=False
    )

    print("✅ System Ready! Running test prompts...\n")
    print("=" * 60)

    # 4. Actual Prompts to Test
    test_prompts = [
        "My `docker ps` command shows an empty PORTS column. Why is this happening and what is the exact command to fix it?",
        "Why do we need to copy dependency files before application files in our Dockerfile, and how exactly do we implement that?",
        "We have an MCP server for deployments. What parameters does the `deploy` tool require, and what specific sequence of actions does it perform?",
        "What are the exact steps involved in our CI/CD pipeline sequence?",
        "What framework, database, and caching layer (like Redis) are we using for the todo-app?"
    ]


    # 5. Execute Prompts
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n🗣️  PROMPT {i}: {prompt}")
        print("-" * 60)

        try:
            # Run the query through the chain
            response = chain.invoke({"query": prompt})
            print(f"\n🤖 ANSWER:\n{response['result']}\n")
        except Exception as e:
            print(f"\n❌ Error processing prompt: {e}\n")

        print("=" * 60)


if __name__ == "__main__":
    main()