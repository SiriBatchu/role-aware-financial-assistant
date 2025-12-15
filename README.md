# 🏦 Role-Aware Financial Insights Assistant

**Personalized Financial Analyst using Agentic RAG with Role-Based Access Controls**

A sophisticated AI-powered financial assistant that delivers fast, context-rich insights tailored to different organizational roles. Built with guardrails and role-based access controls, it ensures sensitive data stays visible only to the right people.

---

### 🔗 Quick Links
- **Live Demo:** [Hugging Face Space](https://huggingface.co/spaces/mohibkhan949/role-aware-financial-assistant)
- **Video Presentation:** [YouTube](https://youtu.be/JLQCUWa6SnM)
- **Project Slides:** [PowerPoint Deck](https://github.com/Mohib1402/role-aware-financial-assistant/blob/main/Role%20Aware%20Financial%20Insights%20Assistant.pptx)
- **Project Report:** [Report](https://github.com/Mohib1402/role-aware-financial-assistant/blob/main/Report_%20Role-Aware%20Financial%20Insights%20Assistant.pdf)

---


## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Role-Based Access Control](#role-based-access-control)
- [Technical Components](#technical-components)
- [Validation Tests](#validation-tests)
- [Project Structure](#project-structure)
- [Future Enhancements](#future-enhancements)
- [Team Contributions](#team-contributions)

---

## 🎯 Project Overview

This project implements a **Role-Aware Financial Insights Assistant** using **Agentic RAG (Retrieval-Augmented Generation)** patterns. It demonstrates:

1. **Role-Based Access Control (RBAC)**: Different users see different data based on their security clearance
2. **Agentic RAG with LangGraph**: Stateful workflow orchestration for multi-step reasoning
3. **ReAct Pattern**: Tool-using agent that can perform calculations
4. **Guardrails**: PII detection and hallucination prevention
5. **Audit Logging**: Compliance-ready access tracking

### Use Case

Financial organizations need to provide AI-powered insights while maintaining strict data access controls:
- **Analysts** should only see public financial data
- **Product Managers** need access to product roadmaps
- **Executives** require full visibility including confidential insider information

This assistant automatically enforces these boundaries while providing personalized response styles.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **3-Tier RBAC** | Analyst, Product Manager, Executive access levels |
| **GPT-4o-mini** | High-quality responses with instruction following |
| **LangGraph Workflow** | Stateful agent with conditional routing |
| **ReAct Calculator** | Python code execution for financial calculations |
| **PII Detection** | Blocks responses containing SSN, credit cards, emails, phones |
| **Hallucination Check** | Prevents confident answers without context |
| **Audit Logging** | JSONL logs for compliance tracking |
| **Dynamic Prompts** | Role-specific response styles (concise vs detailed) |
| **Gradio UI** | Interactive web interface for demonstration |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        GRADIO UI                                 │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │ Role Selector│  │  Chat Box    │  │ Retrieved Docs Panel  │  │
│  └─────────────┘  └──────────────┘  └────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LANGGRAPH WORKFLOW                            │
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────────┐               │
│  │ RETRIEVE │───▶│ GENERATE │───▶│ TOOL_EXECUTOR│               │
│  │  (RBAC)  │    │  (LLM)   │◀───│ (Calculator) │               │
│  └──────────┘    └────┬─────┘    └──────────────┘               │
│                       │                                          │
│                       ▼                                          │
│              ┌─────────────┐                                     │
│              │  GUARDRAILS │                                     │
│              │ (PII, Halluc)│                                    │
│              └──────┬──────┘                                     │
│                     │                                            │
│                     ▼                                            │
│              ┌─────────────┐                                     │
│              │ AUDIT LOG   │                                     │
│              └─────────────┘                                     │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VECTOR STORE (FAISS)                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                 │
│  │ 🟢 PUBLIC  │  │ 🟡 PRODUCT │  │ 🔴 INSIDER │                 │
│  │  (4 docs)  │  │  (3 docs)  │  │  (4 docs)  │                 │
│  └────────────┘  └────────────┘  └────────────┘                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Installation

### Prerequisites

- Python 3.9+
- OpenAI API Key

### Setup

```bash
# Clone/navigate to project
cd role_aware_financial_assistant

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Configure API key
echo 'OPENAI_API_KEY=sk-proj-your-key-here' > .env
```

---

## 💻 Usage

### Launch Web UI

```bash
python main.py
```

Then open **http://localhost:7860** in your browser.

### Run CLI Demo

```bash
python main.py --demo
```

### Python API

```python
from src.agent import ask

# Ask as different roles
ask("What was Q3 revenue?", role="analyst")
ask("What's the product roadmap?", role="product_manager")  
ask("What is the status of Project Blackwell?", role="executive")

# Calculation example
ask("If Q3 revenue of $18.12B grows 10%, what's the new amount?", role="analyst")
```

---

## 🔐 Role-Based Access Control

### Data Sensitivity Levels

| Level | Documents | Example Content |
|-------|-----------|-----------------|
| 🟢 **PUBLIC** | 4 | Q3 earnings, stock buyback, gross margin |
| 🟡 **PRODUCT** | 3 | Blackwell B200 roadmap, feature priorities |
| 🔴 **INSIDER** | 4 | Project delays, legal issues, internal forecasts |

### Role Permissions

| Role | Public | Product | Insider | Response Style |
|------|--------|---------|---------|----------------|
| **Analyst** | ✅ | ❌ | ❌ | Detailed, cite sources |
| **Product Manager** | ✅ | ✅ | ❌ | Focus on timelines |
| **Executive** | ✅ | ✅ | ✅ | Concise bullet points |

### Access Control Demo

**Question:** "What is the status of Project Blackwell?"

| Role | Response |
|------|----------|
| Analyst | "I don't have access to that information." |
| Product Manager | "Blackwell B200 chip targets Q2 2025 launch..." |
| Executive | "• Project Blackwell facing 3-month delay<br>• Cause: TSMC packaging yield issues<br>• Impact: Q2 2025 launch at risk" |

---

## 🔧 Technical Components

### 1. Vector Store & Embeddings

- **FAISS** for efficient similarity search
- **HuggingFace all-MiniLM-L6-v2** for local embeddings (no API needed)
- Post-retrieval filtering for RBAC enforcement

### 2. LLM Integration

- **GPT-4o-mini** via LangChain
- Temperature: 0.1 (consistent financial analysis)
- Max tokens: 512

### 3. LangGraph Workflow

```python
# Nodes
retrieve_node  → Fetches documents based on role
generate_node  → Produces response with dynamic prompts
tool_executor  → Runs Python calculations

# Edges (ReAct Pattern)
retrieve → generate → [tool_executor ↔ generate] → END
```

### 4. Guardrails

**PII Detection Patterns:**
- SSN: `\d{3}-\d{2}-\d{4}`
- Credit Card: `\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}`
- Email: Standard email regex
- Phone: `\d{3}[-.]?\d{3}[-.]?\d{4}`

**Hallucination Prevention:**
- Blocks confident answers when no context retrieved

### 5. Audit Logging

Every query is logged to `audit_log.jsonl`:

```json
{
  "timestamp": "2024-12-11T10:30:00",
  "user_role": "executive",
  "query": "What is Project Blackwell status?",
  "docs_sensitivity": ["insider", "product", "public"],
  "docs_sources": ["Internal Memo", "Product Planning", "10-Q"],
  "response_length": 245,
  "guardrail_triggered": false
}
```

---

## ✅ Validation Tests

All tests pass with the current implementation:

| Test | Description | Result |
|------|-------------|--------|
| RBAC Analyst Block | Analyst cannot see insider data | ✅ PASS |
| RBAC Executive Access | Executive sees all data | ✅ PASS |
| RBAC Product Manager | PM sees public + product | ✅ PASS |
| Public Data Access | All roles see public data | ✅ PASS |
| Dynamic Tone | Executives get concise responses | ✅ PASS |
| Calculator Tool | ReAct pattern executes Python | ✅ PASS |

### Run Tests

```bash
python main.py --demo
```

---

## 📁 Project Structure

```
role_aware_financial_assistant/
├── main.py                 # Entry point (UI or demo)
├── requirements.txt        # Python dependencies
├── .env                    # API key configuration
├── audit_log.jsonl         # Access logs (auto-generated)
├── README.md               # This file
│
├── src/
│   ├── __init__.py
│   ├── config.py           # Configuration & environment
│   ├── data.py             # Financial documents (11 docs)
│   ├── retriever.py        # Vector store + RBAC logic
│   ├── guardrails.py       # PII detection, audit, calculator
│   ├── agent.py            # LangGraph workflow + LLM
│   ├── ui.py               # Gradio interface
│   └── vision.py           # ColPali Vision RAG
│
├── tests/
│   ├── __init__.py
│   └── test_all.py         # Comprehensive test suite (23 tests)
│
└── venv/                   # Virtual environment
```

---

## 📊 Vision RAG (Chart Analysis)

The system includes **GPT-4o-mini Vision** for analyzing financial charts:

### Features
- **Read text** from charts (company names, values, labels)
- **Answer questions** accurately about visual data
- Upload any financial chart or generate a sample

### Usage in UI
1. Scroll down to "Vision RAG - Chart Analysis" section
2. Click "Generate Sample Chart" or upload your own
3. Ask questions like "What was the revenue in 2024?" or "Is this Netflix data?"
4. Get accurate AI-powered answers

### Python API
```python
from src.vision import analyze_chart, generate_sample_chart

# Generate a sample chart
chart_path = generate_sample_chart()

# Ask questions about the chart
answer = analyze_chart(chart_path, "What company's revenue is shown?")
print(answer)  # "The chart shows NVIDIA annual revenue..."
```

---

## 🔮 Future Enhancements

1. **Multi-turn Memory**: Persistent conversation context
2. **More Tools**: Web search, database queries, Excel analysis
3. **User Authentication**: Real login system with role assignment
4. **Deployment**: Docker container, cloud deployment

---

## 👥 Team Contributions

| Member | Role & Contributions |
|--------|----------------------|
| **Aishly Manglani** | LangGraph workflow design, ReAct pattern implementation, agent architecture |
| **Syeda Nida Khader** | Role-Based Access Control (RBAC) logic, retriever filtering, security design |
| **MohibKhan Pathan** | GPT-4o-mini integration, Vision RAG module, Hugging Face deployment |
| **Siri Batchu** | UI testing, sample data review |

*Documentation, testing, and reporting completed by all team members.*

---

## 📚 Technologies Used

- **LangChain** - LLM orchestration framework
- **LangGraph** - Stateful agent workflows
- **GPT-4o-mini** - Large language model
- **FAISS** - Vector similarity search
- **HuggingFace** - Local embeddings
- **Gradio** - Web UI framework
- **Python 3.9+** - Runtime

---

## 📄 License

MIT License - Academic use permitted.

---

## 🙏 Acknowledgments

- **OpenAI** for GPT-4o-mini API
- **LangChain** & **LangGraph** for the orchestration framework
- **HuggingFace** for open-source embeddings and hosting
- **Google Gemini** for assistance with documentation framing and formatting
