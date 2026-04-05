from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from langgraph.graph.message import MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from pydantic import BaseModel
from typing_extensions import Literal

class SupervisorOutput(BaseModel):

    next_agent: Literal["korean_agent", "greek_agent", "spanish_agent", "japanese_agent", "__end__"]
    reasoning: str

class AgentsState(MessagesState):
    current_agent: str
    transfered_by: str
    reasoning: str

llm = init_chat_model("openai:gpt-4o-mini")

def make_agent(prompt, tools):

    def agent_node(state: AgentsState):
        llm_with_tools = llm.bind_tools(tools)
        response = llm_with_tools.invoke(
        f"""
        {prompt}

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

    return agent_builder.compile()

def supervisor(state: AgentsState):
    structured_llm = llm.with_structured_output(SupervisorOutput)
    response = structured_llm.invoke(
        f"""
        You are a supervisor that routes conversations to the appropriate language agent.

        Analyse the customers request and the conversation history and decide which agent should handle the conversation.

        The options for the next agent are:
        - 'korean_agent'
        - 'greek_agent'
        - 'spanish_agent'
        - 'japanese_agent'
        - __end__

        If the agent has finished and replied feel free to finish the conversation returning __end__

        <CONVERSATION_HISTORY>
        {state.get("messages", [])}
        </CONVERSATION_HISTORY>
        """
    )
    return Command(goto=response.next_agent, update={"reasoning": response.reasoning})

graph_builder = StateGraph(AgentsState)

graph_builder.add_node("supervisor", supervisor, destinations=("korean_agent", "greek_agent", "spanish_agent", "japanese_agent", END))

graph_builder.add_node(
    "korean_agent",
    make_agent(prompt="You're a Korean customer support agent. You only speak and understand Korean.", tools=[])
)
graph_builder.add_node(
    "greek_agent",
    make_agent(prompt="You're a Greek customer support agent. You only speak and understand Greek.", tools=[])
)
graph_builder.add_node(
    "spanish_agent",
    make_agent(prompt="You're a Spanish customer support agent. You only speak and understand Spanish.", tools=[])
)
graph_builder.add_node(
    "japanese_agent",
    make_agent(prompt="You're a Japanese customer support agent. You only speak and understand Japanese.", tools=[])
)

graph_builder.add_edge(START, "supervisor")
graph_builder.add_edge("korean_agent", "supervisor")
graph_builder.add_edge("greek_agent", "supervisor")
graph_builder.add_edge("spanish_agent", "supervisor")
graph_builder.add_edge("japanese_agent", "supervisor")

graph = graph_builder.compile()
