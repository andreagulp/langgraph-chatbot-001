import os
from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

# Initialize the language model
api_key = os.environ.get("ANTHROPIC_API_KEY")
tavily_api_key = os.environ.get("TAVILY_API_KEY")

if not api_key or not tavily_api_key:
    raise ValueError("API keys are not set or are empty.")

llm = ChatAnthropic(
    model="claude-3-5-sonnet-20240620",
    api_key=api_key
)

# Initialize the Tavily search tool
search_tool = TavilySearchResults(max_results=2)
tools = [search_tool]

# Bind tools to the LLM
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# Add chatbot node
graph_builder.add_node("chatbot", chatbot)

# Add tool node
tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

# Add conditional edges
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)

# Any time a tool is called, we return to the chatbot to decide the next step
graph_builder.add_edge("tools", "chatbot")

# Set entry point
graph_builder.set_entry_point("chatbot")

# Initialize MemorySaver
memory = MemorySaver()

# Compile the graph with memory
graph = graph_builder.compile(checkpointer=memory)

# Function to create a new conversation
def create_new_conversation():
    return {
        "messages": [],
    }

# Initialize an in-memory storage for conversation history
conversation_history = create_new_conversation()