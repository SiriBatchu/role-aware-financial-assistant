"""Vision RAG module using GPT-4o-mini for financial chart analysis."""

import os
import base64
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from typing import List, Tuple, Optional

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client
_client = None


def get_openai_client():
    """Get or create OpenAI client."""
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client


def encode_image_to_base64(image_path: str) -> str:
    """Convert image file to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def generate_sample_chart() -> str:
    """Generate a sample financial chart for demo purposes."""
    # Use absolute path to ensure Gradio can find it
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    chart_path = os.path.join(script_dir, "sample_revenue_chart.png")
    
    # Always regenerate to ensure fresh chart
    if os.path.exists(chart_path):
        os.remove(chart_path)
    
    # Create sample revenue data
    years = ['2021', '2022', '2023', '2024']
    revenue = [10.0, 15.5, 22.3, 18.1]  # Note the dip in 2024
    colors = ['#4CAF50', '#4CAF50', '#4CAF50', '#f44336']  # Red for decline
    
    plt.figure(figsize=(8, 5))
    bars = plt.bar(years, revenue, color=colors, edgecolor='black', linewidth=1.2)
    plt.title("NVIDIA Annual Revenue (Billions USD)", fontsize=14, fontweight='bold')
    plt.xlabel("Fiscal Year", fontsize=12)
    plt.ylabel("Revenue ($B)", fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add value labels
    for bar, val in zip(bars, revenue):
        plt.text(bar.get_x() + bar.get_width()/2, val + 0.5, 
                f"${val}B", ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Add trend annotation
    plt.annotate('↓ Decline', xy=(3, 18.1), xytext=(3.3, 20),
                fontsize=10, color='red',
                arrowprops=dict(arrowstyle='->', color='red'))
    
    plt.tight_layout()
    plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"✅ Generated sample chart: {chart_path}")
    return chart_path


def analyze_chart(image_path: str, query: str) -> str:
    """
    Analyze a financial chart image using GPT-4o-mini Vision.
    
    Args:
        image_path: Path to the chart image
        query: Question about the chart
    
    Returns:
        AI-generated answer about the chart
    """
    try:
        client = get_openai_client()
        
        # Encode image to base64
        base64_image = encode_image_to_base64(image_path)
        
        # Determine image type
        if image_path.lower().endswith(".png"):
            media_type = "image/png"
        elif image_path.lower().endswith((".jpg", ".jpeg")):
            media_type = "image/jpeg"
        else:
            media_type = "image/png"
        
        # Call GPT-4o-mini with vision
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a financial analyst expert at reading and interpreting charts, graphs, and financial visualizations. Provide clear, accurate, and concise answers based on what you see in the image."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": query
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"⚠️ Chart analysis error: {e}")
        import traceback
        traceback.print_exc()
        return f"Error analyzing chart: {e}"


def get_chart_insights(image_path: str) -> str:
    """
    Get automatic insights from a financial chart using GPT-4o-mini Vision.
    
    Returns a formatted string with the analysis results.
    """
    query = """Analyze this financial chart and provide:
1. What company/topic does this chart show?
2. What type of chart is this?
3. What is the time period covered?
4. What are the key trends or insights?
5. Any notable data points (highest, lowest, changes)?

Be concise but thorough."""
    
    response = analyze_chart(image_path, query)
    
    return f"📊 **Chart Analysis (GPT-4o-mini Vision):**\n\n{response}"


# Quick test function
def test_vision():
    """Test the vision module."""
    print("\n" + "="*50)
    print("🧪 VISION RAG TEST (GPT-4o-mini Vision)")
    print("="*50)
    
    # Generate sample chart
    chart_path = generate_sample_chart()
    
    print(f"\n📈 Analyzing chart: {chart_path}")
    
    # Test with a question
    test_query = "What company's revenue is shown in this chart, and what was the revenue in 2024?"
    print(f"❓ Question: {test_query}\n")
    
    response = analyze_chart(chart_path, test_query)
    
    print("📊 GPT-4o-mini Response:")
    print("-" * 50)
    print(response)
    print("-" * 50)
    
    # Check if it correctly identified NVIDIA
    if "nvidia" in response.lower():
        print("✅ PASSED: Correctly identified NVIDIA")
    else:
        print("⚠️ Response may not have identified the company correctly")
    
    return response


if __name__ == "__main__":
    test_vision()
