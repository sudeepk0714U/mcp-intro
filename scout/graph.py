from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, add_messages
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain.tools import BaseTool

from typing import TypedDict, Annotated, List
import os


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


def build_agent_graph(tools: List[BaseTool] = []):

    system_prompt = """
Your name is Scout and you are an expert data scientist. You help customers manage their data science projects by leveraging the tools available to you. Your goal is to collaborate with the customer in incrementally building their analysis or data modeling project. Version control is a critical aspect of this project, so you must use the git tools to manage the project's version history and maintain a clean, easy to understand commit history.

<filesystem>
You have access to a set of tools that allow you to interact with the user's local filesystem.
You are only able to access files within the working directory `projects`.
The absolute path to this directory is: {working_dir}
If you try to access a file outside of this directory, you will receive an error.
Always use absolute paths when specifying files.
</filesystem>

<version_control>
You have access to git and Github tools.
You should use git tools to manage the version history of the project and Github tools to manage the project's remote repository.
Keep a clean, logical commit history for the repo where each commit should represent a logical, atomic change.
</version_control>

<projects>
A project is a directory within the `projects` directory.

When using the create_new_project tool to create a new project, the following commands will be run for you:
    a. mkdir <project_name>
    b. cd <project_name>
    c. uv init .
    d. git init
    e. mkdir data

Every project has the exact same structure.
</projects>

<data>
When the user refers to data for a project, they are referring to the data within the data directory of the project.

All projects must use the data directory to store all data related to the project.

The user can also load data into this directory.

You have a set of tools called dataflow that allow you to interact with the customer's data.

The dataflow tools are used to load data into the session to query and work with it.

You must always first load data into the session before you can do anything with it.
</data>

<code>
The main.py file is the entry point for the project and will contain all the code to load, transform, and model the data.

You will primarily work on this file to complete the user's requests.

main.py should only be used to implement permanent changes to the data that will be committed to git.
</code>

<tools>
{tools}
</tools>

Assist the customer in all aspects of their data science workflow.
"""

    llm = ChatOpenAI(
        name="Scout",
        model="gpt-4.1-mini-2025-04-14"
    )

    if tools:

        llm = llm.bind_tools(tools)

        tools_json = [
            tool.model_dump_json(
                include=["name", "description"]
            )
            for tool in tools
        ]

        system_prompt = system_prompt.format(
            tools="\n".join(tools_json),
            working_dir=os.environ.get("MCP_FILESYSTEM_DIR")
        )

    def assistant(state: AgentState):

        response = llm.invoke(
            [SystemMessage(content=system_prompt)]
            + state["messages"]
        )

        return {
            "messages": [response]
        }

    builder = StateGraph(AgentState)

    builder.add_node(
        "Scout",
        assistant
    )

    builder.add_node(
        "tools",
        ToolNode(tools)
    )

    builder.add_edge(
        START,
        "Scout"
    )

    builder.add_conditional_edges(
        "Scout",
        tools_condition
    )

    builder.add_edge(
        "tools",
        "Scout"
    )

    return builder.compile(
        checkpointer=MemorySaver()
    )


if __name__ == "__main__":

    from IPython.display import display, Image

    graph = build_agent_graph()

    display(
        Image(
            graph.get_graph().draw_mermaid_png()
        )
    )