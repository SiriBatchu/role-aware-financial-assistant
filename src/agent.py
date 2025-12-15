"""LangGraph workflow and LLM agent."""

from typing import TypedDict, Annotated, List, Optional
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from .config import OPENAI_API_KEY, MODEL_NAME, MODEL_TEMPERATURE, MODEL_MAX_TOKENS, validate_config
from .retriever import get_retriever
from .guardrails import guardrail_check, log_access, python_calculator


# ============================================
# STATE DEFINITION
# ============================================

class FinancialState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]
    user_role: str
    context: str
    guardrail_triggered: Optional[bool]


# ============================================
# LLM INITIALIZATION
# ============================================

validate_config()
print("⚙️ Initializing GPT-4o-mini...")

llm = ChatOpenAI(
    model=MODEL_NAME,
    temperature=MODEL_TEMPERATURE,
    max_tokens=MODEL_MAX_TOKENS,
    api_key=OPENAI_API_KEY
)

print("✅ GPT-4o-mini is online!")


# ============================================
# WORKFLOW NODES
# ============================================

# Store retrieved docs for audit logging
_retrieved_docs = []


def retrieve_node(state: FinancialState):
    """Fetch documents based on user's security clearance."""
    global _retrieved_docs
    user_query = state["messages"][-1].content
    user_role = state["user_role"]

    print(f"   🔄 Agent ({user_role}) is retrieving data...")

    retriever = get_retriever()
    docs = retriever.retrieve(user_query, user_role, k=3)
    _retrieved_docs = docs  # Store for audit

    context_text = "\n\n".join(
        [f"Source ({d.metadata['sensitivity']}, {d.metadata['source']}): {d.page_content}" 
         for d in docs]
    )

    return {"context": context_text}


def generate_node(state: FinancialState):
    """Generate response using GPT-4o-mini based on role and context (with ReAct for calculations)."""
    context = state["context"]
    user_role = state["user_role"]
    messages = state["messages"]

    # Check if we just got a calculation result
    last_message = messages[-1]
    if isinstance(last_message, HumanMessage) and "Calculated Result:" in last_message.content:
        # We have calculation output - now give final answer
        system_prompt = "You have the calculated data. Now answer the user's question concisely using the result."
    else:
        # Dynamic tone based on role
        if user_role == "executive":
            tone = "Be extremely concise. Use bullet points. Focus on risks and strategic impact."
        elif user_role == "product_manager":
            tone = "Focus on product implications. Highlight timelines and feature impacts."
        else:
            tone = "Be detailed and thorough. Cite specific documents found."

        system_prompt = f"""You are a Financial Insights Assistant.

USER ROLE: {user_role}
INSTRUCTION: {tone}

RETRIEVED CONTEXT:
{context}

RULES:
- Only use information from the provided context
- If context is empty or irrelevant, say "I don't have access to that information."
- Never make up financial data
- If the user asks for a CALCULATION (growth, percentages, projections), write Python code to compute it.
  Wrap code in ```python blocks and assign the final value to a variable named 'result'.
"""

    prompt_sequence = [SystemMessage(content=system_prompt)] + messages
    response = llm.invoke(prompt_sequence)

    # Apply guardrails
    passed, final_response = guardrail_check(context, response.content)
    
    if not passed:
        return {"messages": [HumanMessage(content=final_response)], "guardrail_triggered": True}
    
    # Log access (only if not a calculation intermediate step)
    if "```python" not in response.content:
        log_access(user_role, messages[-1].content, _retrieved_docs, response.content)

    return {"messages": [response], "guardrail_triggered": False}


def tool_node(state: FinancialState):
    """Execute Python code if detected in the response (ReAct pattern)."""
    last_message = state["messages"][-1]
    content = last_message.content

    if "```python" in content:
        print("   🛠️ DETECTED CALCULATION REQUEST. Executing Code...")
        
        # Extract the code block
        code_block = content.split("```python")[1].split("```")[0]
        
        # Run the calculator tool
        output = python_calculator(code_block)
        
        # Return result as a new message
        return {"messages": [HumanMessage(content=output)]}
    
    return {"messages": []}


def should_continue(state: FinancialState):
    """Router: Check if we need to execute a tool or end."""
    last_message = state["messages"][-1]
    
    if hasattr(last_message, 'content') and "```python" in last_message.content:
        return "execute_tool"
    else:
        return END


# ============================================
# COMPILE WORKFLOW (with ReAct pattern)
# ============================================

workflow = StateGraph(FinancialState)

# Add Nodes
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("generate", generate_node)
workflow.add_node("tool_executor", tool_node)

# Add Edges
workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "generate")

# Conditional edge: generate -> tool_executor OR END
workflow.add_conditional_edges(
    "generate",
    should_continue,
    {
        "execute_tool": "tool_executor",
        END: END
    }
)

# Tool loops back to generate (to process the result)
workflow.add_edge("tool_executor", "generate")

agent = workflow.compile()

print("✅ Role-Aware Agent Graph compiled (with ReAct calculator)!")


# ============================================
# PUBLIC API
# ============================================

def ask(question: str, role: str = "analyst") -> str:
    """
    Main interface to ask questions.
    
    Args:
        question: The user's question
        role: One of 'analyst', 'product_manager', 'executive'
    
    Returns:
        The assistant's response
    """
    if role not in ["analyst", "product_manager", "executive"]:
        return f"❌ Invalid role: {role}. Use 'analyst', 'product_manager', or 'executive'"
    
    inputs = {
        "messages": [HumanMessage(content=question)],
        "user_role": role
    }
    
    result = agent.invoke(inputs)
    return result['messages'][-1].content
