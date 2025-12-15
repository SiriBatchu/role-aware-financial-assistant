#!/usr/bin/env python3
"""
Role-Aware Financial Insights Assistant
========================================
Main entry point for the application.

Usage:
    python main.py          # Launch Gradio UI
    python main.py --demo   # Run CLI demo
"""

import sys


def run_demo():
    """Run CLI demonstration."""
    from src.agent import ask
    
    print("\n" + "="*60)
    print("🎯 ROLE-AWARE FINANCIAL ASSISTANT - DEMO")
    print("="*60)
    
    test_cases = [
        {
            "question": "What is the status of Project Blackwell?",
            "roles": ["analyst", "product_manager", "executive"],
            "description": "Testing insider data access control"
        },
        {
            "question": "What's on the product roadmap for 2025?",
            "roles": ["analyst", "product_manager"],
            "description": "Testing product data access control"
        },
        {
            "question": "What was Q3 revenue?",
            "roles": ["analyst"],
            "description": "Testing public data access"
        }
    ]
    
    for test in test_cases:
        print(f"\n{'─'*60}")
        print(f"📋 TEST: {test['description']}")
        print(f"❓ QUESTION: {test['question']}")
        print("─"*60)
        
        for role in test["roles"]:
            print(f"\n👤 ROLE: {role.upper()}")
            response = ask(test["question"], role)
            print(f"💬 RESPONSE:\n{response}\n")
    
    print("\n" + "="*60)
    print("✅ DEMO COMPLETE")
    print("="*60)
    print("\n📊 Audit log saved to: audit_log.jsonl")


def main():
    """Main entry point."""
    print("\n" + "="*60)
    print("🚀 ROLE-AWARE FINANCIAL ASSISTANT")
    print("="*60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        run_demo()
    else:
        from src.ui import launch_ui
        launch_ui()


if __name__ == "__main__":
    main()
