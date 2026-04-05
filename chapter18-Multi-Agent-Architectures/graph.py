from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from langgraph.graph.message import MessagesState
from langgraph.prebuilt import ToolNode, tools_condition, InjectedState
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from pydantic import BaseModel
from typing_extensions import Literal, Annotated

class SupervisorOutput(BaseModel):

    next_agent: Literal["korean_agent", "greek_agent", "spanish_agent", "japanese_agent", "__end__"]
    reasoning: str

class AgentsState(MessagesState):
    current_agent: str
    transfered_by: str
    reasoning: str

llm = init_chat_model("openai:gpt-4o-mini")

def make_agent_tool(tool_name, tool_description, system_prompt, tools):

    def agent_node(state: AgentsState):
        llm_with_tools = llm.bind_tools(tools)
        response = llm_with_tools.invoke(
        f"""
        {system_prompt}

        Conversation History:
        {state['messages']}
        """
        )
        return {"messages": [response]}

    agent_builder = StateGraph(AgentsState)

    agent_builder.add_node("agent", agent_node)
    agent_builder.add_node("tools",ToolNode(tools=tools))

    agent_builder.add_edge(START, "agent")
    agent_builder.add_conditional_edges("agent", tools_condition)
    agent_builder.add_edge("tools", "agent")
    agent_builder.add_edge("agent", END)

    agent = agent_builder.compile()

    @tool(name_or_callable=tool_name, description=tool_description)
    def agent_tool(state: Annotated[dict, InjectedState]):
        # 위처럼 하면 tool에 현재 스테이트를 넣어줄 수 있다.

        result = agent.invoke(state)
        return result["messages"][-1].content

    return agent_tool

tools = [
    make_agent_tool(
        tool_name="korean_agent",
        tool_description="Use this when the user is speaking korean",
        system_prompt="You're a korean customer support agent you speak in korean",
        tools=[],
    ),
    make_agent_tool(
        tool_name="spanish_agent",
        tool_description="Use this when the user is speaking spanish",
        system_prompt="You're a spanish customer support agent you speak in spanish",
        tools=[],
    ),
    make_agent_tool(
        tool_name="greek_agent",
        tool_description="Use this when the user is speaking greek",
        system_prompt="You're a greek customer support agent you speak in greek",
        tools=[],
    ),
]

def supervisor(state: AgentsState):
    llm_with_tools = llm.bind_tools(tools=tools)
    result = llm_with_tools.invoke(state["messages"])
    return {"messages": [result]}

graph_builder = StateGraph(AgentsState)

graph_builder.add_node("supervisor", supervisor)
graph_builder.add_node("tools", ToolNode(tools=tools))

graph_builder.add_edge(START, "supervisor")
graph_builder.add_conditional_edges("supervisor", tools_condition)
graph_builder.add_edge("tools", "supervisor")
graph_builder.add_edge("supervisor", END)

graph = graph_builder.compile()
