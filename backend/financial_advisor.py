import location_handler

def create_financial_prompt(user_data):
    """
    Create a detailed financial advice prompt for the AI
    
    Args:
        user_data: Dictionary containing:
            - age
            - income
            - debt
            - savings
            - city
            - state
            - goals
    
    Returns:
        Formatted prompt string
    """
    prompt = f"""You are a professional financial advisor. Provide detailed, actionable financial advice for this person:

Age: {user_data['age']}
Annual Income: ${user_data['income']:,}
Total Debt: ${user_data['debt']:,}
Current Savings: ${user_data['savings']:,}
Location: {user_data['city']}, {user_data['state']}
Financial Goals: {user_data['goals']}

Please provide:
1. A clear assessment of their current financial situation
2. Prioritized action steps they should take immediately
3. Long-term financial planning recommendations
4. Debt management strategies specific to their situation
5. Savings and investment advice appropriate for their age and income

Be specific, practical, and encouraging. Use bullet points for clarity."""

    return prompt

def enhance_with_location(ai_response, city, state):
    """
    Enhance AI response with location-specific resources
    
    Args:
        ai_response: The AI-generated financial advice
        city: User's city
        state: User's state
    
    Returns:
        Enhanced response with local resources
    """
    resources = location_handler.get_location_resources(city, state)
    
    if resources:
        location_info = location_handler.format_location_resources(resources)
        return f"{ai_response}\n\n{location_info}"
    else:
        return f"{ai_response}\n\n📍 Note: No specific local resources found for {city}, {state}. Consider searching for local credit unions and financial counseling services in your area."