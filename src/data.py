"""Financial documents with sensitivity levels."""

RAW_FINANCIAL_DATA = [
    # 🟢 PUBLIC DATA (Accessible to all roles)
    {
        "content": "NVIDIA Q3 Revenue reported at $18.12 Billion, up 206% YoY. Data Center revenue was the primary driver.",
        "metadata": {"source": "10-Q", "sensitivity": "public", "category": "financials", "year": 2024}
    },
    {
        "content": "The company announced a stock buyback program of $25 Billion.",
        "metadata": {"source": "Press Release", "sensitivity": "public", "category": "financials", "year": 2024}
    },
    {
        "content": "NVIDIA's gaming segment revenue reached $2.86 billion, showing steady consumer demand.",
        "metadata": {"source": "10-Q", "sensitivity": "public", "category": "financials", "year": 2024}
    },
    {
        "content": "The company's gross margin improved to 74.0%, up from 70.1% in the previous quarter.",
        "metadata": {"source": "10-Q", "sensitivity": "public", "category": "financials", "year": 2024}
    },
    
    # 🟡 PRODUCT DATA (Accessible to Product Managers and Executives)
    {
        "content": "Product Roadmap: Next-gen Blackwell B200 chip targets Q2 2025 launch. Focus on AI training workloads.",
        "metadata": {"source": "Product Planning", "sensitivity": "product", "category": "roadmap", "year": 2025}
    },
    {
        "content": "Feature prioritization for H100 successor includes 2x memory bandwidth and improved power efficiency.",
        "metadata": {"source": "Product Planning", "sensitivity": "product", "category": "roadmap", "year": 2025}
    },
    {
        "content": "Customer feedback indicates strong demand for inference-optimized chips in edge computing scenarios.",
        "metadata": {"source": "Product Research", "sensitivity": "product", "category": "research", "year": 2024}
    },
    
    # 🔴 INSIDER DATA (Accessible ONLY to Executives)
    {
        "content": "CONFIDENTIAL: Project 'Blackwell' is facing a 3-month delay due to packaging yield issues at TSMC.",
        "metadata": {"source": "Internal Memo", "sensitivity": "insider", "category": "operations", "year": 2025}
    },
    {
        "content": "CONFIDENTIAL: Legal team is preparing for a potential antitrust inquiry regarding the ARM acquisition attempt.",
        "metadata": {"source": "Legal Brief", "sensitivity": "insider", "category": "legal", "year": 2023}
    },
    {
        "content": "CONFIDENTIAL: Q4 revenue projection internally revised down by 8% due to supply chain constraints.",
        "metadata": {"source": "Internal Forecast", "sensitivity": "insider", "category": "financials", "year": 2024}
    },
    {
        "content": "CONFIDENTIAL: Executive compensation packages under review, potential 15% increase for retention.",
        "metadata": {"source": "HR Memo", "sensitivity": "insider", "category": "hr", "year": 2024}
    }
]
