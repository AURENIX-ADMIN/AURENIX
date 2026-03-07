from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

# Define the state of the agent
class AgentState(TypedDict):
    messages: list[BaseMessage]
    context: Dict[str, Any]
    verdict: str

# Define nodes
def analysis_node(state: AgentState):
    """
    Analyzes the input data.
    """
    messages = state['messages']
    # In reality, call LLM here
    # response = llm.invoke(messages)
    
    print("Analyzing data...")
    return {"messages": [AIMessage(content="Data analysis complete. Found potential discrepancy in invoice #123.")]}

def verification_node(state: AgentState):
    """
    Verifies the analysis against policy.
    """
    # Simulate verification
    print("Verifying against policy...")
    return {"verdict": "FLAGGED", "messages": [AIMessage(content="Policy check: Flagged for high variance.")]}

def double_check_node(state: AgentState):
    """
    Self-correction loop.
    """
    print("Double checking findings...")
    return {"messages": [AIMessage(content="Double check confirmed. Discrepancy persisted.")]}

# Build the graph
def build_auditor_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("analyze", analysis_node)
    workflow.add_node("verify", verification_node)
    workflow.add_node("double_check", double_check_node)
    
    workflow.set_entry_point("analyze")
    
    workflow.add_edge("analyze", "verify")
    
    # Conditional logic
    def check_verdict(state):
        if state.get("verdict") == "FLAGGED":
            return "double_check"
        return END
        
    workflow.add_conditional_edges(
        "verify",
        check_verdict,
        {
            "double_check": "double_check",
            END: END
        }
    )
    
    workflow.add_edge("double_check", END)
    
    app = workflow.compile()
    return app

if __name__ == "__main__":
    # Simple test
    app = build_auditor_graph()
    initial_state = {
        "messages": [HumanMessage(content="Audit invoice #123")], 
        "context": {}, 
        "verdict": "UNKNOWN"
    }
    result = app.invoke(initial_state)
    print("Final State:", result)
