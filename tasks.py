from crewai import Task
from tools import search_tool
from agents import market_research_analyst, technology_expert, business_consultant

def create_tasks(product_name):
    """Create highly focused, time-efficient tasks for the given product name"""
    
    # Task 1: Quick Market Analysis
    task1 = Task(
        description=f"""Conduct a rapid market analysis for {product_name}. 
                        Focus ONLY on essential information. Current date is June 2025.
                        
                        Provide exactly these 5 points (keep each under 2 sentences):
                        1. Primary target customer (age, income, behavior)
                        2. Market size estimate (global/regional)
                        3. Top 3 direct competitors
                        4. Best marketing channel (online/offline/hybrid)
                        5. Suggested price range
                        
                        Total response: Maximum 300 words. Be direct and specific.""",
        agent=market_research_analyst,
        expected_output="5-point market analysis covering target customers, market size, competitors, marketing channel, and pricing (max 300 words).",
        tools=[search_tool]
    )

    # Task 2: Technical Assessment (Simplified)
    task2 = Task(
        description=f"""Provide a basic technical assessment for {product_name}. 
                    Focus on practical implementation only.
                    
                    Cover exactly these 4 areas (2 sentences each):
                    1. Manufacturing method (how it's made)
                    2. Key equipment needed
                    3. Main quality control point
                    4. Biggest technical challenge
                    
                    Total response: Maximum 250 words. Focus on practicality.""",
        agent=technology_expert,
        expected_output="4-point technical assessment covering manufacturing, equipment, quality control, and challenges (max 250 words).",
        tools=[search_tool]
    )

    # Task 3: Business Strategy (Streamlined)
    task3 = Task(
        description=f"""Create a focused business strategy for {product_name} using the previous analyses.
                    Current date is June 2025.
                    
                    Provide exactly these 6 elements (keep each concise):
                    1. Business model (B2B/B2C/subscription/one-time)
                    2. Primary revenue stream
                    3. Launch timeline (3-6-12 months)
                    4. Success metric (1 key KPI)
                    5. Biggest risk
                    6. Initial funding estimate
                    
                    Total response: Maximum 350 words. Be actionable and realistic.""",
        agent=business_consultant,
        expected_output="6-point business strategy with model, revenue, timeline, metrics, risks, and funding (max 350 words).",
        context=[task1, task2],
        tools=[search_tool]
    )
    
    return [task1, task2, task3]

def create_emergency_tasks(product_name):
    """Create ultra-simplified tasks for when the main tasks are failing"""
    
    print("🆘 Creating emergency simplified tasks...")
    
    task1 = Task(
        description=f"""Quick analysis: Who would buy {product_name} and why? 
                        Answer in exactly 3 sentences. No research needed if obvious.""",
        agent=market_research_analyst,
        expected_output="3-sentence customer analysis.",
        tools=[]  # No tools to avoid timeouts
    )

    task2 = Task(
        description=f"""Simple question: How difficult is it to make {product_name}? 
                        Answer in exactly 2 sentences.""",
        agent=technology_expert,
        expected_output="2-sentence technical difficulty assessment.",
        tools=[]
    )

    task3 = Task(
        description=f"""Basic business plan: How would you sell {product_name}? 
                        Answer in exactly 4 sentences covering: how to sell, pricing, timeline, main challenge.""",
        agent=business_consultant,
        expected_output="4-sentence basic business plan.",
        context=[task1, task2],
        tools=[]
    )
    
    return [task1, task2, task3]