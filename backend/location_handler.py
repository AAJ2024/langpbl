import json
import os

LOCATION_DATA_FILE = 'location_resources.json'

def load_location_data():
    """Load location resources from JSON file"""
    if not os.path.exists(LOCATION_DATA_FILE):
        print(f"Warning: {LOCATION_DATA_FILE} not found")
        return {}
    
    with open(LOCATION_DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_location_resources(city, state):
    """
    Get local resources for a specific location
    
    Args:
        city: City name (e.g., "Athens")
        state: State abbreviation (e.g., "GA")
    
    Returns:
        Dictionary with local resources or None if not found
    """
    location_data = load_location_data()
    location_key = f"{city}, {state}"
    
    return location_data.get(location_key)

def format_location_resources(resources):
    """Format location resources into a readable string"""
    if not resources:
        return "No local resources found for your area."
    
    formatted = "\n\n📍 LOCAL RESOURCES FOR YOUR AREA:\n\n"
    
    # Credit Unions
    if resources.get('credit_unions'):
        formatted += "🏦 LOCAL CREDIT UNIONS:\n"
        for cu in resources['credit_unions']:
            formatted += f"\n• {cu['name']}\n"
            formatted += f"  Phone: {cu['phone']}\n"
            formatted += f"  Website: {cu['website']}\n"
            formatted += f"  Services: {', '.join(cu['services'])}\n"
            if cu.get('notes'):
                formatted += f"  Note: {cu['notes']}\n"
    
    # Counseling Centers
    if resources.get('counseling_centers'):
        formatted += "\n💼 FREE FINANCIAL COUNSELING:\n"
        for center in resources['counseling_centers']:
            formatted += f"\n• {center['name']}\n"
            if center.get('location'):
                formatted += f"  Location: {center['location']}\n"
            formatted += f"  Phone: {center['phone']}\n"
            formatted += f"  Website: {center['website']}\n"
            formatted += f"  Services: {', '.join(center['services'])}\n"
            if center.get('hours'):
                formatted += f"  Hours: {center['hours']}\n"
    
    # State Programs
    if resources.get('state_programs'):
        formatted += "\n🎓 STATE FINANCIAL PROGRAMS:\n"
        for program in resources['state_programs']:
            formatted += f"\n• {program['name']}\n"
            formatted += f"  Website: {program['website']}\n"
            if program.get('description'):
                formatted += f"  {program['description']}\n"
            if program.get('eligibility'):
                formatted += f"  Eligibility: {program['eligibility']}\n"
    
    # Cost of Living
    if resources.get('cost_of_living'):
        col = resources['cost_of_living']
        formatted += "\n💰 COST OF LIVING IN YOUR AREA:\n"
        formatted += f"• Average 1BR Rent: {col['average_rent_1br']}/month\n"
        formatted += f"• Average 2BR Rent: {col['average_rent_2br']}/month\n"
        formatted += f"• Monthly Expenses: {col['monthly_expenses']}\n"
        formatted += f"• Food: {col['food_monthly']}/month\n"
        formatted += f"• Transportation: {col['transportation']}/month\n"
        formatted += f"• Utilities: {col['utilities']}/month\n"
    
    # Tax Info
    if resources.get('tax_info'):
        tax = resources['tax_info']
        formatted += "\n📊 TAX INFORMATION:\n"
        formatted += f"• State Income Tax: {tax['state_income_tax']}\n"
        if tax.get('city_income_tax'):
            formatted += f"• City Income Tax: {tax['city_income_tax']}\n"
        formatted += f"• Sales Tax: {tax['sales_tax']}\n"
        if tax.get('property_tax'):
            formatted += f"• Property Tax: {tax['property_tax']}\n"
    
    return formatted

def get_available_locations():
    """Get list of all available locations"""
    location_data = load_location_data()
    return list(location_data.keys())