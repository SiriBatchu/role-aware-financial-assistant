"""Gradio UI for the Financial Assistant."""

import gradio as gr
from .agent import ask
from .retriever import get_retriever
from .vision import generate_sample_chart, get_chart_insights, analyze_chart


def chat_with_role(message: str, history: list, role: str):
    """Chat function for Gradio interface."""
    if not message.strip():
        return history, "Please enter a question."
    
    # Get response
    response = ask(message, role)
    
    # Get docs display for transparency
    retriever = get_retriever()
    docs_display = retriever.get_docs_display(message, role)
    
    # Update history
    history = history + [[message, response]]
    
    return history, docs_display


def update_role_info(selected_role: str) -> str:
    """Update role description when role changes."""
    if selected_role == "analyst":
        return "🟢 **Analyst**: Access to public financial data only (earnings, press releases)."
    elif selected_role == "product_manager":
        return "🟡 **Product Manager**: Access to public + product roadmap data."
    else:
        return "🔴 **Executive**: Full access including confidential insider data."


def create_ui():
    """Create the Gradio interface."""
    
    with gr.Blocks(
        title="Role-Aware Financial Assistant",
        theme=gr.themes.Soft()
    ) as demo:
        
        gr.Markdown("""
        # 🏦 Role-Aware Financial Insights Assistant
        
        **Personalized financial analysis with role-based access controls and guardrails.**
        
        Select your role to see different levels of data access:
        - 🟢 **Analyst**: Public data only
        - 🟡 **Product Manager**: Public + Product roadmap  
        - 🔴 **Executive**: Full access including insider data
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                # Role selector
                role = gr.Dropdown(
                    choices=["analyst", "product_manager", "executive"],
                    value="analyst",
                    label="👤 Select Your Role"
                )
                
                # Role description
                role_info = gr.Markdown(
                    value="🟢 **Analyst**: Access to public financial data only (earnings, press releases)."
                )
                
                # Chat interface
                chatbot = gr.Chatbot(
                    label="💬 Conversation",
                    height=400
                )
                
                with gr.Row():
                    msg = gr.Textbox(
                        label="Your Question",
                        placeholder="Ask about financials, product roadmap, or insider updates...",
                        scale=4
                    )
                    submit_btn = gr.Button("Send", variant="primary", scale=1)
                
                clear_btn = gr.Button("🗑️ Clear Conversation")
            
            with gr.Column(scale=1):
                gr.Markdown("### 📄 Retrieved Documents")
                docs_display = gr.Markdown(
                    value="*Documents will appear here after you ask a question.*"
                )
                
                gr.Markdown("---")
                gr.Markdown("""
                ### 🔒 Try These Questions
                
                **1. Insider Access Test:**
                "What is the status of Project Blackwell?"
                - Analyst: ❌ No access
                - PM: 🟡 Roadmap only
                - Executive: 🔴 Full insider info
                
                **2. Product Data Test:**
                "What's on the product roadmap?"
                - Analyst: ❌ No access
                - PM/Exec: ✅ Full access
                
                **3. Public Data Test:**
                "What was Q3 revenue?"
                - All roles: ✅ Public data
                
                **4. Calculator Test:**
                "If Q3 revenue grows 10%, what would it be?"
                """)
        
        # Event handlers
        role.change(update_role_info, inputs=[role], outputs=[role_info])
        
        submit_btn.click(
            chat_with_role,
            inputs=[msg, chatbot, role],
            outputs=[chatbot, docs_display]
        ).then(lambda: "", outputs=[msg])
        
        msg.submit(
            chat_with_role,
            inputs=[msg, chatbot, role],
            outputs=[chatbot, docs_display]
        ).then(lambda: "", outputs=[msg])
        
        clear_btn.click(
            lambda: ([], "*Documents will appear here after you ask a question.*"),
            outputs=[chatbot, docs_display]
        )
        
        # Vision RAG Tab
        gr.Markdown("---")
        gr.Markdown("### 📊 Vision RAG - Chart Analysis")
        
        with gr.Row():
            with gr.Column(scale=1):
                chart_image = gr.Image(
                    label="Upload Financial Chart",
                    type="filepath"
                )
                generate_chart_btn = gr.Button("🎨 Generate Sample Chart")
            
            with gr.Column(scale=1):
                chart_query = gr.Textbox(
                    label="Ask a question about the chart",
                    placeholder="e.g., What was the revenue in 2024? Is there a decline?"
                )
                analyze_btn = gr.Button("🔍 Analyze Chart", variant="primary")
                chart_results = gr.Markdown(
                    value="*Upload a chart and ask a question to analyze it.*"
                )
        
        # Vision event handlers
        def gen_chart():
            try:
                path = generate_sample_chart()
                print(f"📊 Chart generated at: {path}")
                # Return chart path AND a success message
                return path, "✅ **Sample chart generated!** Now enter a description and click 'Analyze Chart'.\n\n*Example: 'A chart showing revenue decline in 2024'*"
            except Exception as e:
                print(f"❌ Chart generation error: {e}")
                return None, f"❌ Error generating chart: {e}"
        
        def analyze_uploaded_chart(image_path, query):
            try:
                print(f"🔍 Analyzing: path={image_path}, query={query}")
                if not image_path:
                    return "⚠️ **Please upload a chart first** or click '🎨 Generate Sample Chart' button on the left."
                if not query.strip():
                    return get_chart_insights(image_path)
                
                # Use GPT-4o-mini Vision for chart Q&A
                response = analyze_chart(image_path, query)
                print(f"📊 GPT-4o-mini response received")
                return f"📊 **Answer:**\n\n{response}"
            except Exception as e:
                print(f"❌ Analysis error: {e}")
                import traceback
                traceback.print_exc()
                return f"❌ Error analyzing chart: {e}"
        
        generate_chart_btn.click(gen_chart, outputs=[chart_image, chart_results])
        analyze_btn.click(
            analyze_uploaded_chart,
            inputs=[chart_image, chart_query],
            outputs=[chart_results]
        )
        
        gr.Markdown("""
        ---
        **Built with:** LangChain, LangGraph, GPT-4o-mini, FAISS | 
        **Features:** Role-Based Access Control, Guardrails, Audit Logging, Vision RAG (GPT-4o-mini Vision)
        """)
    
    return demo


def launch_ui():
    """Launch the Gradio UI."""
    print("\n🌐 Launching Gradio UI...")
    print("   Open http://localhost:7860 in your browser\n")
    
    demo = create_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
