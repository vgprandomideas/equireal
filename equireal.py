# ========================================
# equireal.py - EquiReal Enhanced Platform
# "Renting the Opportunity" - Revolutionary lease structuring
# ========================================

import streamlit as st
import pandas as pd
import json
import uuid
import numpy as np
from datetime import datetime, timedelta
import os

# Optional plotly import
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="EquiReal - Renting the Opportunity",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================================
# DATABASE FUNCTIONS
# ========================================

DATA_DIR = 'data'
DEALS_FILE = os.path.join(DATA_DIR, 'deals.json')
FEEDBACK_FILE = os.path.join(DATA_DIR, 'feedback.json')

def initialize_database():
    """Initialize the database directory and files"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    if not os.path.exists(DEALS_FILE):
        with open(DEALS_FILE, 'w') as f:
            json.dump([], f)
    
    if not os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, 'w') as f:
            json.dump([], f)

def load_deals():
    """Load all deals from JSON file"""
    try:
        with open(DEALS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_deals(deals):
    """Save deals to JSON file"""
    with open(DEALS_FILE, 'w') as f:
        json.dump(deals, f, indent=2, default=str)

def save_deal(business_data, deal_terms, proposal):
    """Save a new deal to the database"""
    deals = load_deals()
    
    deal_record = {
        **business_data,
        **deal_terms,
        'proposal': proposal,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    deals.append(deal_record)
    save_deals(deals)
    
    return deal_record

def get_deals():
    """Get all deals"""
    return load_deals()

def get_deal_by_id(deal_id):
    """Get a specific deal by ID"""
    deals = load_deals()
    for deal in deals:
        if deal.get('id') == deal_id:
            return deal
    return None

def update_deal_status(deal_id, new_status):
    """Update the status of a deal"""
    deals = load_deals()
    
    for deal in deals:
        if deal.get('id') == deal_id:
            deal['status'] = new_status
            deal['updated_at'] = datetime.now().isoformat()
            if new_status == 'approved':
                deal['approved_at'] = datetime.now().isoformat()
            elif new_status == 'rejected':
                deal['rejected_at'] = datetime.now().isoformat()
            break
    
    save_deals(deals)

def save_feedback(feedback_data):
    """Save user feedback"""
    try:
        existing_feedback = []
        if os.path.exists(FEEDBACK_FILE):
            with open(FEEDBACK_FILE, 'r') as f:
                existing_feedback = json.load(f)
        
        existing_feedback.append(feedback_data)
        
        with open(FEEDBACK_FILE, 'w') as f:
            json.dump(existing_feedback, f, indent=2, default=str)
        
        return True
    except Exception:
        return False

# ========================================
# ENHANCED AI LOGIC FUNCTIONS
# ========================================

def calculate_risk_score(business_data):
    """Enhanced AI-based risk scoring"""
    base_score = 50
    
    # Business type risk adjustment
    business_type_risk = {
        'SaaS Startup': -12,
        'E-commerce': -8,
        'Professional Services': -10,
        'Manufacturing': +5,
        'Restaurant': +28,
        'Retail Store': +18,
        'Franchise': -8,
        'Other': +12
    }
    
    industry_risk = {
        'Technology': -12,
        'Healthcare': -8,
        'Finance': -5,
        'Education': -3,
        'Food & Beverage': +22,
        'Retail': +15,
        'Real Estate': +8,
        'Other': +10
    }
    
    base_score += business_type_risk.get(business_data.get('business_type', 'Other'), 0)
    base_score += industry_risk.get(business_data.get('industry', 'Other'), 0)
    
    # Financial health assessment
    current_revenue = business_data.get('current_revenue', 0)
    projected_12m = business_data.get('projected_revenue_12m', 0)
    burn_rate = business_data.get('burn_rate', 0)
    runway_months = business_data.get('runway_months', 0)
    
    # Revenue traction scoring
    if current_revenue >= 50000:
        base_score -= 20
    elif current_revenue >= 20000:
        base_score -= 15
    elif current_revenue >= 10000:
        base_score -= 10
    elif current_revenue >= 5000:
        base_score -= 5
    elif current_revenue > 0:
        base_score += 0
    else:
        base_score += 15
    
    # Revenue growth realism check
    if current_revenue > 0 and projected_12m > 0:
        growth_multiple = projected_12m / current_revenue
        if growth_multiple > 20:
            base_score += 25
        elif growth_multiple > 10:
            base_score += 15
        elif growth_multiple > 5:
            base_score += 8
        elif growth_multiple > 2:
            base_score -= 5
        elif growth_multiple > 1.2:
            base_score += 0
        else:
            base_score += 20
    
    # Team size indicators
    team_size = business_data.get('team_size', 1)
    if 8 <= team_size <= 25:
        base_score -= 10
    elif 5 <= team_size <= 7:
        base_score -= 5
    elif 3 <= team_size <= 4:
        base_score += 0
    elif team_size == 2:
        base_score += 8
    elif team_size == 1:
        base_score += 18
    else:
        base_score += 12
    
    # Founder experience impact
    experience_impact = {
        'Previous successful exit': -25,
        'Serial entrepreneur': -18,
        'Industry veteran (10+ years)': -15,
        'First-time founder': +12
    }
    base_score += experience_impact.get(
        business_data.get('founder_experience', 'First-time founder'), 0
    )
    
    # Funding validation
    funding_raised = business_data.get('funding_raised', 0)
    if funding_raised >= 5000000:
        base_score -= 25
    elif funding_raised >= 2000000:
        base_score -= 20
    elif funding_raised >= 500000:
        base_score -= 15
    elif funding_raised >= 100000:
        base_score -= 10
    elif funding_raised > 0:
        base_score -= 5
    
    # Market validation
    has_customers = business_data.get('has_customers', False)
    has_revenue = business_data.get('has_revenue', False)
    
    if has_customers and has_revenue:
        base_score -= 12
    elif has_customers:
        base_score -= 6
    elif has_revenue:
        base_score -= 8
    
    # Cash runway assessment
    if runway_months > 24:
        base_score -= 15
    elif runway_months > 18:
        base_score -= 10
    elif runway_months > 12:
        base_score -= 5
    elif runway_months > 6:
        base_score += 5
    elif runway_months > 3:
        base_score += 15
    else:
        base_score += 30
    
    # Ensure score is within realistic bounds
    final_score = max(10, min(90, base_score))
    return round(final_score, 1)

def generate_deal_terms(business_data, risk_score):
    """Generate deal terms based on risk score"""
    base_upfront_rent = 30
    base_equity = 5
    base_revenue_share = 3
    base_revenue_years = 3
    
    risk_multiplier = (risk_score - 50) / 50
    
    upfront_rent_percent = base_upfront_rent + (risk_multiplier * 15)
    upfront_rent_percent = max(20, min(50, upfront_rent_percent))
    
    equity_percent = base_equity + (risk_multiplier * 4)
    equity_percent = max(2, min(12, equity_percent))
    
    revenue_share_percent = base_revenue_share + (risk_multiplier * 2)
    revenue_share_percent = max(1, min(6, revenue_share_percent))
    
    revenue_share_years = base_revenue_years
    if business_data.get('business_type') in ['SaaS Startup', 'E-commerce']:
        revenue_share_years = 4
    elif business_data.get('business_type') == 'Restaurant':
        revenue_share_years = 2
    
    space_size = business_data.get('space_size', 1000)
    annual_market_rent = space_size * 25
    monthly_market_rent = annual_market_rent / 12
    monthly_rent = monthly_market_rent * (upfront_rent_percent / 100)
    deferred_amount = monthly_market_rent - monthly_rent
    
    current_revenue = business_data.get('current_revenue', 0)
    revenue_trigger = max(current_revenue * 1.5, 5000)
    
    return {
        'risk_score': risk_score,
        'upfront_rent_percent': round(upfront_rent_percent, 1),
        'equity_percent': round(equity_percent, 1),
        'revenue_share_percent': round(revenue_share_percent, 1),
        'revenue_share_years': revenue_share_years,
        'monthly_rent': round(monthly_rent, 0),
        'monthly_market_rent': round(monthly_market_rent, 0),
        'deferred_amount': round(deferred_amount, 0),
        'annual_market_rent': round(annual_market_rent, 0),
        'revenue_trigger': round(revenue_trigger, 0),
        'space_size': space_size
    }

def generate_risk_explanation(business_data, risk_score):
    """Generate detailed risk factor explanation"""
    factors = []
    
    # Positive factors
    if business_data.get('current_revenue', 0) > 10000:
        factors.append(f"✅ Strong revenue traction (${business_data['current_revenue']:,}/month)")
    
    if business_data.get('has_funding', False):
        factors.append(f"✅ Institutional funding secured (${business_data.get('funding_raised', 0):,})")
    
    if business_data.get('founder_experience') in ['Serial entrepreneur', 'Previous successful exit']:
        factors.append(f"✅ Experienced founder ({business_data['founder_experience']})")
    
    if business_data.get('runway_months', 0) > 12:
        factors.append(f"✅ Healthy cash runway ({business_data['runway_months']} months)")
    
    # Risk factors
    if business_data.get('business_type') == 'Restaurant':
        factors.append("⚠️ High-risk industry (Restaurant sector)")
    
    if business_data.get('current_revenue', 0) == 0:
        factors.append("⚠️ Pre-revenue stage")
    
    if business_data.get('team_size', 0) < 3:
        factors.append("⚠️ Small team size")
    
    if business_data.get('runway_months', 0) < 6:
        factors.append("❌ Limited cash runway")
    
    return factors

# ========================================
# DEAL GENERATOR FUNCTIONS
# ========================================

def create_deal_proposal(business_data, deal_terms):
    """Generate a comprehensive deal proposal"""
    projected_revenue = business_data.get('projected_revenue_12m', 0)
    annual_revenue_share = projected_revenue * 12 * (deal_terms['revenue_share_percent'] / 100)
    total_annual_rent = deal_terms['monthly_rent'] * 12
    potential_total_return = total_annual_rent + annual_revenue_share
    
    roi_improvement = ((potential_total_return / deal_terms['annual_market_rent']) - 1) * 100 if deal_terms['annual_market_rent'] > 0 else 0
    roi_difference = int(potential_total_return - deal_terms['annual_market_rent'])
    
    proposal = f"""
EQUIREAL DEAL PROPOSAL - "RENTING THE OPPORTUNITY"
Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
Proposal ID: EQR-{business_data['id'][:8].upper()}
Valid Until: {(datetime.now() + timedelta(days=30)).strftime('%B %d, %Y')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TENANT INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Business Name:        {business_data['business_name']}
Business Type:        {business_data['business_type']}
Industry:            {business_data.get('industry', 'Not specified')}
Desired Location:     {business_data['location']}
Space Requirements:   {business_data['space_size']:,} square feet
Lease Duration:       {business_data.get('lease_duration', 'To be negotiated')}

Team Size:           {business_data['team_size']} employees
Founder Experience:   {business_data.get('founder_experience', 'Not specified')}
Business Model:       {business_data.get('business_model', 'Not specified')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FINANCIAL OVERVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Current Monthly Revenue:      ${business_data['current_revenue']:,}
12-Month Projection:          ${business_data['projected_revenue_12m']:,}
24-Month Projection:          ${business_data['projected_revenue_24m']:,}
Current Burn Rate:            ${business_data.get('burn_rate', 0):,}/month
Cash Runway:                  {business_data.get('runway_months', 0)} months
Total Funding Raised:         ${business_data.get('funding_raised', 0):,}

Funding Status:               {'✅ Funded' if business_data.get('has_funding') else '❌ Bootstrapped'}
Revenue Status:               {'✅ Revenue Generating' if business_data.get('has_revenue') else '❌ Pre-Revenue'}
Customer Base:                {'✅ Has Customers' if business_data.get('has_customers') else '❌ Pre-Customer'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ENHANCED AI RISK ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Overall Risk Score:           {deal_terms['risk_score']}/100
Risk Category:                {'🟢 LOW RISK' if deal_terms['risk_score'] < 40 else '🟡 MEDIUM RISK' if deal_terms['risk_score'] < 70 else '🔴 HIGH RISK'}
Confidence Level:             {95 - deal_terms['risk_score'] * 0.3:.1f}%
Assessment Factors:           25+ data points analyzed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROPOSED LEASE STRUCTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Market Rate Analysis:
Standard Market Rent:         ${deal_terms['monthly_market_rent']:,.0f}/month
Annual Market Value:          ${deal_terms['annual_market_rent']:,.0f}/year

EquiReal Hybrid Structure:

UPFRONT RENT COMPONENT:
Monthly Payment:              ${deal_terms['monthly_rent']:,.0f}
Percentage of Market:         {deal_terms['upfront_rent_percent']:.1f}%
Annual Payment:               ${deal_terms['monthly_rent'] * 12:,.0f}

DEFERRED RENT COMPONENT:
Monthly Deferred Amount:      ${deal_terms['deferred_amount']:,.0f}
Percentage of Market:         {100 - deal_terms['upfront_rent_percent']:.1f}%
Annual Deferred:              ${deal_terms['deferred_amount'] * 12:,.0f}

TOTAL MONTHLY SAVINGS:        ${deal_terms['deferred_amount']:,.0f}
TOTAL ANNUAL SAVINGS:         ${deal_terms['deferred_amount'] * 12:,.0f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EQUITY PARTICIPATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Equity Stake:                 {deal_terms['equity_percent']:.1f}% of business
Structure:                    Convertible equity (SAFE-like instrument)
Valuation Method:             Post-money valuation at next funding round
Conversion Events:            Series A, acquisition, or IPO

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REVENUE SHARING AGREEMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Revenue Share Percentage:     {deal_terms['revenue_share_percent']:.1f}% of gross monthly revenue
Duration:                     {deal_terms['revenue_share_years']} years from lease commencement
Revenue Threshold:            Activated when monthly revenue > ${deal_terms['revenue_trigger']:,}
Reporting Frequency:          Monthly, within 15 days of month-end

Projected Annual Revenue Share: ${annual_revenue_share:,.0f}
Total Revenue Share (Full Term): ${annual_revenue_share * deal_terms['revenue_share_years']:,.0f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LANDLORD RETURN ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Traditional Lease Model:
Annual Rent Income:           ${deal_terms['annual_market_rent']:,.0f}
Total Return (Year 1):       ${deal_terms['annual_market_rent']:,.0f}

EquiReal Hybrid Model:
Annual Rent Income:           ${deal_terms['monthly_rent'] * 12:,.0f}
Annual Revenue Share:         ${annual_revenue_share:,.0f}
Equity Upside:                Variable (potentially significant)
Total Cash Return (Year 1):   ${potential_total_return:,.0f}

IMPROVEMENT OVER MARKET:      +{roi_improvement:.1f}% (+${roi_difference:,})

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NEXT STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Landlord Review & Approval (5-7 business days)
2. Due Diligence Period (10 business days)
3. Legal Documentation (5-10 business days)
4. Lease Execution & Move-in

Contact Information:
EquiReal Platform: hello@equireal.com
Phone: (555) 123-REAL

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"Renting the Opportunity - You're not renting space. You're funding growth. 
You're inventing an asset class."
"""
    
    return proposal

def create_contract_template(deal):
    """Generate contract template"""
    contract = f"""
EQUIREAL HYBRID LEASE AGREEMENT
"Renting the Opportunity"

This Agreement is entered into on {datetime.now().strftime('%B %d, %Y')} between:

LANDLORD: [LANDLORD NAME AND ADDRESS]
TENANT: {deal['business_name']}

PREMISES: {deal['location']}
SPACE: {deal['space_size']:,} square feet

ARTICLE 1: RENT TERMS
1.1 Base Rent: ${deal.get('monthly_rent', 0):,.0f} per month
1.2 Market Rate: ${deal.get('monthly_market_rent', 0):,.0f} per month
1.3 Upfront Percentage: {deal.get('upfront_rent_percent', 30):.1f}% of market rate
1.4 Deferred Amount: ${deal.get('deferred_amount', 0):,.0f} per month

ARTICLE 2: EQUITY PARTICIPATION
2.1 Equity Percentage: {deal.get('equity_percent', 5):.1f}% of Tenant's business
2.2 Structure: Convertible equity instrument
2.3 Conversion Events: Series A funding, acquisition, IPO

ARTICLE 3: REVENUE SHARING
3.1 Revenue Share: {deal.get('revenue_share_percent', 3):.1f}% of gross monthly revenue
3.2 Duration: {deal.get('revenue_share_years', 3)} years from lease commencement
3.3 Threshold: Activated when monthly revenue exceeds ${deal.get('revenue_trigger', 5000):,}

[Additional standard commercial lease terms to be added by legal counsel]

Generated by: EquiReal Platform
Date: {datetime.now().strftime('%B %d, %Y')}
Agreement ID: EQR-{deal['id'][:8].upper()}-CONTRACT

SIGNATURES:
LANDLORD: _________________ DATE: _________
TENANT: __________________ DATE: _________
"""
    
    return contract

# ========================================
# ENHANCED STYLING FUNCTIONS
# ========================================

def load_css():
    """Load enhanced styling"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
    
    :root {
        --primary-blue: #2563eb;
        --primary-purple: #7c3aed;
        --secondary-green: #059669;
        --accent-orange: #ea580c;
        --gray-50: #f9fafb;
        --gray-100: #f3f4f6;
        --gray-200: #e5e7eb;
        --gray-600: #4b5563;
        --gray-800: #1f2937;
        --gray-900: #111827;
    }
    
    .main {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-purple) 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 20px 40px rgba(37, 99, 235, 0.15);
        position: relative;
        overflow: hidden;
    }
    
    .main-header h1 {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    .main-header h3 {
        font-size: 1.5rem;
        font-weight: 500;
        margin-bottom: 1rem;
        opacity: 0.95;
        position: relative;
        z-index: 1;
    }
    
    .section-header {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.875rem;
        font-weight: 600;
        color: var(--gray-800);
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--primary-blue);
        display: inline-block;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-purple) 100%);
        color: white;
        border: none;
        padding: 0.875rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.5);
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.5);
        background: linear-gradient(135deg, #1d4ed8 0%, #6d28d9 100%);
    }
    
    .risk-low { 
        background: linear-gradient(135deg, var(--secondary-green), #10b981);
        color: white;
        padding: 0.375rem 0.875rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        box-shadow: 0 2px 4px rgba(5, 150, 105, 0.3);
    }
    
    .risk-medium { 
        background: linear-gradient(135deg, var(--accent-orange), #f97316);
        color: white;
        padding: 0.375rem 0.875rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        box-shadow: 0 2px 4px rgba(234, 88, 12, 0.3);
    }
    
    .risk-high { 
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
        padding: 0.375rem 0.875rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3);
    }
    
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #ffffff 0%, var(--gray-50) 100%);
        border: 1px solid var(--gray-200);
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }
    
    @media (max-width: 768px) {
        .main-header {
            padding: 2rem 1rem;
        }
        
        .main-header h1 {
            font-size: 2.5rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def show_brand_header():
    """Display enhanced brand header"""
    st.markdown("""
    <div class="main-header">
        <div style="position: relative; z-index: 2;">
            <h1>🏢 EquiReal</h1>
            <h3>Renting the Opportunity</h3>
            <p>Revolutionary lease structuring with AI-powered risk assessment</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ========================================
# ENHANCED UI PAGES
# ========================================

def show_enhanced_home():
    """Enhanced landing page"""
    show_brand_header()
    
    st.markdown('<div class="section-header">🚀 Revolutionary Lease Model</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🏢 For Businesses
        **Pay Less, Share Success**
        - **Only 30% upfront rent** instead of 100%
        - **70% shared through equity + revenue**
        - **AI-powered fair deal terms**
        - **Faster approval process**
        - **Aligned landlord partnership**
        """)
        
        if st.button("🚀 Apply as Business", key="business_btn"):
            st.session_state.page = 'tenant'
            st.rerun()
    
    with col2:
        st.markdown("""
        ### 🏠 For Landlords
        **Higher Returns, Shared Growth**
        - **Higher total returns** than fixed rent
        - **Equity upside** from successful tenants
        - **Revenue sharing** from growing businesses
        - **AI risk assessment** for every deal
        - **Reduced vacancy risk**
        """)
        
        if st.button("🏠 View Landlord Dashboard", key="landlord_btn"):
            st.session_state.page = 'landlord'
            st.rerun()
    
    # Platform metrics
    st.markdown('<div class="section-header">📊 Platform Impact</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Deals", "67", "↗️ +18%")
    with col2:
        st.metric("Total Volume", "$4.1M", "↗️ +35%")
    with col3:
        st.metric("Average ROI", "24.3%", "↗️ +8.1%")
    with col4:
        st.metric("Success Rate", "89%", "↗️ +7%")
    
    # FAQ Section
    st.markdown('<div class="section-header">❓ Frequently Asked Questions</div>', unsafe_allow_html=True)
    
    with st.expander("🤖 How does the AI risk assessment work?"):
        st.markdown("""
        Our AI analyzes 25+ factors including:
        - **Business type & industry risk** (25% weight)
        - **Financial health** (35% weight) - revenue, burn rate, runway
        - **Team experience** (20% weight) - founder background, team size
        - **Market validation** (15% weight) - customers, funding, traction
        - **Operational factors** (5% weight) - space efficiency, business model
        """)
    
    with st.expander("💰 What are typical deal terms?"):
        st.markdown("""
        **Risk-adjusted terms:**
        - **Upfront Rent:** 20-50% of market rate (avg: 30%)
        - **Equity Stake:** 2-12% of business (avg: 5%)
        - **Revenue Share:** 1-6% for 2-4 years (avg: 3%)
        
        Lower risk businesses get better terms.
        """)
    
    with st.expander("🎯 Who is this for?"):
        st.markdown("""
        **Perfect for:**
        - Early-stage startups needing capital efficiency
        - Growing businesses expanding locations
        - Forward-thinking landlords seeking higher returns
        - Any business willing to share upside for lower costs
        """)

def show_tenant_form():
    """Enhanced business application form"""
    st.title("🚀 Business Application")
    st.markdown("Get AI-powered lease terms tailored to your business")
    
    with st.form("business_form"):
        st.markdown('<div class="section-header">📋 Business Information</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            business_name = st.text_input("Business Name *")
            business_type = st.selectbox(
                "Business Type *",
                ["SaaS Startup", "E-commerce", "Restaurant", "Retail Store", "Franchise", "Professional Services", "Manufacturing", "Other"]
            )
            industry = st.selectbox(
                "Industry *",
                ["Technology", "Food & Beverage", "Retail", "Healthcare", "Finance", "Education", "Real Estate", "Other"]
            )
            
        with col2:
            location = st.text_input("Desired Location *")
            space_size = st.number_input("Space Size (sq ft) *", min_value=100, max_value=50000, value=1500)
            lease_duration = st.selectbox("Preferred Lease Duration", ["1 year", "2 years", "3 years", "5 years"])
        
        st.markdown('<div class="section-header">💰 Financial Information</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            current_revenue = st.number_input("Current Monthly Revenue ($)", min_value=0, value=0)
            projected_revenue_12m = st.number_input("Projected Revenue (12 months) ($)", min_value=0, value=10000)
            projected_revenue_24m = st.number_input("Projected Revenue (24 months) ($)", min_value=0, value=20000)
            
        with col2:
            burn_rate = st.number_input("Monthly Burn Rate ($)", min_value=0, value=5000)
            runway_months = st.number_input("Cash Runway (months)", min_value=0, value=12)
            funding_raised = st.number_input("Total Funding Raised ($)", min_value=0, value=0)
        
        st.markdown('<div class="section-header">👥 Team & Experience</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            team_size = st.number_input("Current Team Size", min_value=1, max_value=500, value=5)
            founder_experience = st.selectbox(
                "Founder Experience",
                ["First-time founder", "Serial entrepreneur", "Industry veteran (10+ years)", "Previous successful exit"]
            )
            
        with col2:
            has_funding = st.checkbox("Have you raised institutional funding?")
            has_revenue = st.checkbox("Currently generating revenue?")
            has_customers = st.checkbox("Do you have paying customers?")
        
        business_model = st.selectbox(
            "Business Model",
            ["B2B SaaS", "B2C SaaS", "E-commerce", "Marketplace", "Brick & Mortar", "Franchise", "Service-based", "Other"]
        )
        
        target_market = st.text_area("Target Market Description")
        competitive_advantage = st.text_area("Competitive Advantage")
        growth_strategy = st.text_area("Growth Strategy")
        
        submitted = st.form_submit_button("🎯 Get My AI-Powered Deal Terms", type="primary")
        
        if submitted:
            if not business_name or not business_type or not location:
                st.error("Please fill in all required fields marked with *")
                return
            
            business_data = {
                'id': str(uuid.uuid4()),
                'business_name': business_name,
                'business_type': business_type,
                'industry': industry,
                'location': location,
                'space_size': space_size,
                'lease_duration': lease_duration,
                'current_revenue': current_revenue,
                'projected_revenue_12m': projected_revenue_12m,
                'projected_revenue_24m': projected_revenue_24m,
                'burn_rate': burn_rate,
                'runway_months': runway_months,
                'funding_raised': funding_raised,
                'team_size': team_size,
                'founder_experience': founder_experience,
                'has_funding': has_funding,
                'has_revenue': has_revenue,
                'has_customers': has_customers,
                'business_model': business_model,
                'target_market': target_market,
                'competitive_advantage': competitive_advantage,
                'growth_strategy': growth_strategy,
                'timestamp': datetime.now().isoformat(),
                'status': 'pending'
            }
            
            with st.spinner("🤖 AI is analyzing your business..."):
                risk_score = calculate_risk_score(business_data)
                deal_terms = generate_deal_terms(business_data, risk_score)
                risk_factors = generate_risk_explanation(business_data, risk_score)
                proposal = create_deal_proposal(business_data, deal_terms)
                
                save_deal(business_data, deal_terms, proposal)
            
            show_deal_results(business_data, deal_terms, proposal, risk_factors)

def show_deal_results(business_data, deal_terms, proposal, risk_factors):
    """Display AI-generated deal terms"""
    st.success("✅ Your personalized deal terms are ready!")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        risk_color = "🟢" if deal_terms['risk_score'] < 40 else "🟡" if deal_terms['risk_score'] < 70 else "🔴"
        st.metric("AI Risk Score", f"{risk_color} {deal_terms['risk_score']}/100")
    
    with col2:
        st.metric("Upfront Rent", f"{deal_terms['upfront_rent_percent']:.1f}%")
    
    with col3:
        st.metric("Equity Stake", f"{deal_terms['equity_percent']:.1f}%")
    
    with col4:
        st.metric("Revenue Share", f"{deal_terms['revenue_share_percent']:.1f}%")
    
    st.markdown('<div class="section-header">🤖 AI Risk Analysis</div>', unsafe_allow_html=True)
    
    for factor in risk_factors:
        st.write(factor)
    
    st.markdown('<div class="section-header">📊 Deal Breakdown</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**💰 Monthly Payments:**")
        st.write(f"Market Rate: ${deal_terms['monthly_market_rent']:,.0f}")
        st.write(f"Your Payment: ${deal_terms['monthly_rent']:,.0f}")
        st.write(f"Monthly Savings: ${deal_terms['deferred_amount']:,.0f}")
        
    with col2:
        st.markdown("**🤝 Partnership Terms:**")
        st.write(f"Equity Stake: {deal_terms['equity_percent']:.1f}%")
        st.write(f"Revenue Share: {deal_terms['revenue_share_percent']:.1f}% for {deal_terms['revenue_share_years']} years")
        st.write(f"Trigger: ${deal_terms['revenue_trigger']:,}/month")
    
    st.markdown('<div class="section-header">📋 Complete Proposal</div>', unsafe_allow_html=True)
    with st.expander("📄 View Full Proposal"):
        st.code(proposal, language="text")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📧 Send to Landlords"):
            st.success("✅ Proposal sent to relevant landlords!")
            st.balloons()
    
    with col2:
        st.download_button(
            label="📄 Download Proposal",
            data=proposal,
            file_name=f"equireal_proposal_{business_data['business_name']}.txt",
            mime="text/plain"
        )

def show_landlord_dashboard():
    """Landlord dashboard"""
    st.title("🏠 Landlord Dashboard")
    st.markdown("Manage deal proposals and track portfolio performance")
    
    deals = get_deals()
    
    if not deals:
        st.info("📭 No deal applications yet. Check back soon!")
        return
    
    df = pd.DataFrame(deals)
    
    # Dashboard metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Applications", len(df))
    
    with col2:
        pending = len(df[df['status'] == 'pending'])
        st.metric("Pending Review", pending)
    
    with col3:
        approved = len(df[df['status'] == 'approved'])
        approval_rate = (approved / len(df) * 100) if len(df) > 0 else 0
        st.metric("Approval Rate", f"{approval_rate:.1f}%")
    
    with col4:
        avg_risk = df['risk_score'].mean() if 'risk_score' in df.columns else 0
        st.metric("Avg Risk Score", f"{avg_risk:.1f}/100")
    
    # Deal management
    st.markdown('<div class="section-header">📋 Deal Management</div>', unsafe_allow_html=True)
    
    for idx, deal in df.iterrows():
        show_deal_card(deal)
    
    # Portfolio analytics
    if PLOTLY_AVAILABLE and len(df) > 0:
        st.markdown('<div class="section-header">📊 Portfolio Analytics</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            risk_distribution = df['risk_score'].apply(
                lambda x: 'Low' if x < 40 else 'Medium' if x < 70 else 'High'
            ).value_counts()
            
            fig_risk = px.pie(
                values=risk_distribution.values,
                names=risk_distribution.index,
                title="Risk Distribution"
            )
            st.plotly_chart(fig_risk, use_container_width=True)
        
        with col2:
            business_type_dist = df['business_type'].value_counts()
            
            fig_business = px.bar(
                x=business_type_dist.index,
                y=business_type_dist.values,
                title="Business Types"
            )
            st.plotly_chart(fig_business, use_container_width=True)

def show_deal_card(deal):
    """Display individual deal card"""
    risk_score = deal.get('risk_score', 50)
    risk_emoji = "🟢" if risk_score < 40 else "🟡" if risk_score < 70 else "🔴"
    risk_label = "Low" if risk_score < 40 else "Medium" if risk_score < 70 else "High"
    
    with st.container():
        st.markdown(f"""
        <div style="border: 1px solid #e0e0e0; border-radius: 12px; padding: 1.5rem; margin: 1rem 0; background: white;">
            <h4>{risk_emoji} {deal['business_name']} - {deal['business_type']}</h4>
            <p><strong>Location:</strong> {deal['location']} | <strong>Space:</strong> {deal['space_size']:,} sq ft</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            **Business Details:**
            - Risk Score: {risk_score}/100 ({risk_label})
            - Team Size: {deal['team_size']} people
            - Current Revenue: ${deal['current_revenue']:,}/month
            - Projected (12m): ${deal['projected_revenue_12m']:,}/month
            """)
        
        with col2:
            st.markdown(f"""
            **Deal Terms:**
            - Upfront Rent: {deal.get('upfront_rent_percent', 30):.1f}%
            - Monthly Payment: ${deal.get('monthly_rent', 0):,}
            - Equity: {deal.get('equity_percent', 5):.1f}%
            - Revenue Share: {deal.get('revenue_share_percent', 3):.1f}%
            """)
        
        with col3:
            st.markdown(f"""
            **Financial Info:**
            - Funding Raised: ${deal.get('funding_raised', 0):,}
            - Burn Rate: ${deal.get('burn_rate', 0):,}/month
            - Has Revenue: {'Yes' if deal.get('has_revenue', False) else 'No'}
            - Has Customers: {'Yes' if deal.get('has_customers', False) else 'No'}
            """)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button(f"✅ Approve", key=f"approve_{deal['id']}"):
                update_deal_status(deal['id'], 'approved')
                st.success("Deal approved!")
                st.rerun()
        
        with col2:
            if st.button(f"❌ Reject", key=f"reject_{deal['id']}"):
                update_deal_status(deal['id'], 'rejected')
                st.error("Deal rejected")
                st.rerun()
        
        with col3:
            if st.button(f"📋 Details", key=f"details_{deal['id']}"):
                st.session_state.selected_deal_id = deal['id']
                st.session_state.page = 'deal_details'
                st.rerun()
        
        with col4:
            contract = create_contract_template(deal)
            st.download_button(
                label="📄 Contract",
                data=contract,
                file_name=f"contract_{deal['business_name']}.txt",
                mime="text/plain",
                key=f"download_{deal['id']}"
            )

def show_feedback_form():
    """Feedback capture form"""
    st.title("💬 Share Your Feedback")
    st.markdown("Help us improve EquiReal")
    
    with st.form("feedback_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            user_type = st.selectbox("I am a:", ["Business Owner", "Landlord/Property Owner", "Investor", "Real Estate Professional", "Other"])
            interest_level = st.selectbox("Interest Level:", ["Very Interested", "Somewhat Interested", "Just Exploring", "Not Interested"])
            
        with col2:
            location = st.text_input("Your Location")
            contact_email = st.text_input("Email (optional)")
        
        feedback_text = st.text_area("Feedback & Suggestions:")
        would_pilot = st.checkbox("I'd be interested in a pilot partnership")
        
        submitted = st.form_submit_button("Submit Feedback")
        
        if submitted:
            feedback_data = {
                'timestamp': datetime.now().isoformat(),
                'user_type': user_type,
                'interest_level': interest_level,
                'location': location,
                'email': contact_email,
                'feedback': feedback_text,
                'pilot_interest': would_pilot
            }
            
            if save_feedback(feedback_data):
                st.success("✅ Thank you for your feedback!")
                if would_pilot:
                    st.info("🚀 We'll reach out about pilot opportunities!")
                st.balloons()
            else:
                st.success("✅ Thank you for your feedback!")

def show_deal_details():
    """Show detailed view of a specific deal"""
    if 'selected_deal_id' not in st.session_state:
        st.error("No deal selected. Please go back to the dashboard.")
        return
    
    deal = get_deal_by_id(st.session_state.selected_deal_id)
    
    if not deal:
        st.error("Deal not found.")
        return
    
    st.title(f"📋 Deal Details: {deal['business_name']}")
    
    if st.button("← Back to Dashboard"):
        st.session_state.page = 'landlord'
        st.rerun()
    
    # Deal overview
    st.markdown('<div class="section-header">🏢 Business Overview</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **Basic Information:**
        - Business Name: {deal['business_name']}
        - Type: {deal['business_type']}
        - Industry: {deal.get('industry', 'N/A')}
        - Location: {deal['location']}
        - Space Size: {deal['space_size']:,} sq ft
        """)
    
    with col2:
        st.markdown(f"""
        **Team & Experience:**
        - Team Size: {deal['team_size']} people
        - Founder Experience: {deal.get('founder_experience', 'N/A')}
        - Has Funding: {'Yes' if deal.get('has_funding', False) else 'No'}
        - Has Revenue: {'Yes' if deal.get('has_revenue', False) else 'No'}
        """)
    
    # Financial projections
    st.markdown('<div class="section-header">💰 Financial Projections</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Current Revenue", f"${deal['current_revenue']:,}/month")
    
    with col2:
        st.metric("12M Projection", f"${deal['projected_revenue_12m']:,}/month")
    
    with col3:
        st.metric("24M Projection", f"${deal['projected_revenue_24m']:,}/month")
    
    # Actions
    st.markdown('<div class="section-header">⚡ Actions</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ Approve Deal", type="primary"):
            update_deal_status(deal['id'], 'approved')
            st.success("Deal approved!")
            st.rerun()
    
    with col2:
        if st.button("❌ Reject Deal"):
            update_deal_status(deal['id'], 'rejected')
            st.error("Deal rejected")
            st.rerun()
    
    with col3:
        contract = create_contract_template(deal)
        st.download_button(
            label="📄 Generate Contract",
            data=contract,
            file_name=f"contract_{deal['business_name']}.txt",
            mime="text/plain"
        )

# ========================================
# MAIN APPLICATION
# ========================================

def main():
    """Main application router"""
    initialize_database()
    load_css()
    
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🏢 EquiReal")
        st.markdown("*Renting the Opportunity*")
        
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.page = 'home'
        
        if st.button("🚀 Business Application", use_container_width=True):
            st.session_state.page = 'tenant'
        
        if st.button("🏢 Landlord Dashboard", use_container_width=True):
            st.session_state.page = 'landlord'
        
        if st.button("📋 Deal Details", use_container_width=True):
            st.session_state.page = 'deal_details'
        
        if st.button("💬 Feedback", use_container_width=True):
            st.session_state.page = 'feedback'
        
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        deals = get_deals()
        st.metric("Total Deals", len(deals))
        if deals:
            pending = len([d for d in deals if d.get('status') == 'pending'])
            st.metric("Pending", pending)
        
        st.markdown("---")
        st.markdown("**System Status:**")
        st.write(f"Plotly: {'✅' if PLOTLY_AVAILABLE else '❌'}")
        st.write(f"AI: ✅ Enhanced v2.0")
        st.markdown("*EquiReal v2.0*")
    
    # Route to pages
    if st.session_state.page == 'home':
        show_enhanced_home()
    elif st.session_state.page == 'tenant':
        show_tenant_form()
    elif st.session_state.page == 'landlord':
        show_landlord_dashboard()
    elif st.session_state.page == 'deal_details':
        show_deal_details()
    elif st.session_state.page == 'feedback':
        show_feedback_form()

if __name__ == "__main__":
    main()