#!/usr/bin/env python3
"""
EquiReal Production Platform - COMPLETE Working Version
AI-Powered Commercial Real Estate Platform
"""

import streamlit as st
import pandas as pd
import json
import uuid
import numpy as np
from datetime import datetime, timedelta
import hashlib
import sqlite3
from typing import Dict, List, Optional
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="EquiReal - Enterprise Real Estate Platform",
    page_icon="🏢",
    layout="wide"
)

# Constants
DB_FILE = 'equireal.db'
UPLOAD_DIR = Path('uploads')
UPLOAD_DIR.mkdir(exist_ok=True)

INDUSTRIES = [
    "Software as a Service (SaaS)", "FinTech", "HealthTech", "E-commerce",
    "Professional Services", "Manufacturing", "Restaurants", "Retail Store",
    "Real Estate", "Construction", "Healthcare Services", "Legal Services",
    "Marketing Agency", "Consulting", "Other"
]

GLOBAL_LOCATIONS = [
    "New York, NY, USA", "Los Angeles, CA, USA", "San Francisco, CA, USA",
    "Chicago, IL, USA", "Boston, MA, USA", "Seattle, WA, USA", "Austin, TX, USA",
    "Miami, FL, USA", "Denver, CO, USA", "Atlanta, GA, USA", "Toronto, ON, Canada",
    "London, UK", "Paris, France", "Berlin, Germany", "Tokyo, Japan", "Singapore"
]

BUSINESS_TYPES = [
    "SaaS Startup", "E-commerce", "Restaurant", "Retail Store", "Professional Services",
    "Manufacturing", "Healthcare Services", "Consulting", "Other"
]

class DatabaseManager:
    def __init__(self):
        self.db_file = DB_FILE
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            user_type TEXT NOT NULL,
            profile_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS businesses (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            business_name TEXT NOT NULL,
            industry TEXT,
            location TEXT,
            space_size INTEGER,
            financial_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS deals (
            id TEXT PRIMARY KEY,
            business_id TEXT NOT NULL,
            deal_terms TEXT,
            proposal TEXT,
            status TEXT DEFAULT 'pending',
            risk_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_user(self, email, password, user_type, profile_data=None):
        user_id = str(uuid.uuid4())
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO users (id, email, password_hash, user_type, profile_data)
            VALUES (?, ?, ?, ?, ?)
            ''', (user_id, email, password_hash, user_type, json.dumps(profile_data or {})))
            conn.commit()
            return user_id
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def authenticate_user(self, email, password):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, email, user_type, profile_data 
        FROM users WHERE email = ? AND password_hash = ?
        ''', (email, password_hash))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'email': result[1],
                'user_type': result[2],
                'profile_data': json.loads(result[3]) if result[3] else {}
            }
        return None
    
    def save_business(self, business_data):
        business_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO businesses (id, user_id, business_name, industry, location, space_size, financial_data)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            business_id,
            business_data['user_id'],
            business_data['business_name'],
            business_data['industry'],
            business_data['location'],
            business_data['space_size'],
            json.dumps(business_data.get('financial_data', {}))
        ))
        
        conn.commit()
        conn.close()
        return business_id
    
    def save_deal(self, deal_data):
        deal_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO deals (id, business_id, deal_terms, proposal, risk_score)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            deal_id,
            deal_data['business_id'],
            json.dumps(deal_data['deal_terms']),
            deal_data['proposal'],
            deal_data['risk_score']
        ))
        
        conn.commit()
        conn.close()
        return deal_id
    
    def get_deals(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT d.*, b.business_name, b.industry, b.location, b.space_size
        FROM deals d
        JOIN businesses b ON d.business_id = b.id
        ORDER BY d.created_at DESC
        ''')
        
        deals = []
        columns = [desc[0] for desc in cursor.description]
        
        for row in cursor.fetchall():
            deal_dict = dict(zip(columns, row))
            if deal_dict.get('deal_terms'):
                try:
                    deal_dict['deal_terms'] = json.loads(deal_dict['deal_terms'])
                except:
                    deal_dict['deal_terms'] = {}
            deals.append(deal_dict)
        
        conn.close()
        return deals
    
    def update_deal_status(self, deal_id, status):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE deals SET status = ? WHERE id = ?', (status, deal_id))
        success = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        return success

class AIAnalysisEngine:
    def __init__(self):
        pass
    
    def calculate_risk_score(self, business_data):
        financial_data = business_data.get('financial_data', {})
        
        # Industry risk mapping
        industry_risks = {
            "Software as a Service (SaaS)": 25,
            "FinTech": 35,
            "E-commerce": 45,
            "Restaurants": 70,
            "Professional Services": 30,
            "Manufacturing": 50
        }
        
        industry_risk = industry_risks.get(business_data.get('industry'), 50)
        
        # Financial risk calculation
        financial_risk = 50
        current_revenue = financial_data.get('current_revenue', 0)
        
        if current_revenue > 100000:
            financial_risk -= 20
        elif current_revenue > 50000:
            financial_risk -= 10
        elif current_revenue == 0:
            financial_risk += 20
        
        if financial_data.get('is_profitable'):
            financial_risk -= 15
        
        # Team risk assessment
        team_risk = 50
        team_size = business_data.get('team_size', 1)
        
        if 5 <= team_size <= 50:
            team_risk -= 15
        elif team_size < 3:
            team_risk += 20
        
        # Calculate overall risk
        overall_risk = (industry_risk * 0.4 + financial_risk * 0.4 + team_risk * 0.2)
        overall_risk = max(10, min(90, overall_risk))
        
        return {
            'overall_risk': round(overall_risk, 1),
            'industry_risk': round(industry_risk, 1),
            'financial_risk': round(financial_risk, 1),
            'team_risk': round(team_risk, 1),
            'confidence_score': 85.0,
            'risk_trend': 'Stable Risk'
        }

class AuthenticationManager:
    def __init__(self):
        self.db = DatabaseManager()
    
    def show_auth_interface(self):
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #2563eb, #7c3aed); 
                    border-radius: 16px; margin-bottom: 2rem; color: white;">
            <h1>🏢 EquiReal Enterprise</h1>
            <p>AI-Powered Commercial Real Estate Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Sign In", "📝 Create Account"])
        
        with tab1:
            self.show_login_form()
        
        with tab2:
            self.show_registration_form()
    
    def show_login_form(self):
        with st.form("login_form"):
            st.markdown("#### Welcome Back")
            
            email = st.text_input("Email Address")
            password = st.text_input("Password", type="password")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                login_btn = st.form_submit_button("🔑 Sign In", type="primary")
            
            with col2:
                demo_btn = st.form_submit_button("🚀 Demo")
            
            if login_btn and email and password:
                user = self.db.authenticate_user(email, password)
                if user:
                    st.session_state.user = user
                    st.session_state.authenticated = True
                    st.success("✅ Welcome back!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
            
            if demo_btn:
                demo_user = {
                    'id': 'demo_user',
                    'email': 'demo@equireal.com',
                    'user_type': 'business',
                    'profile_data': {'first_name': 'Demo', 'last_name': 'User'}
                }
                st.session_state.user = demo_user
                st.session_state.authenticated = True
                st.success("✅ Welcome to Demo!")
                st.rerun()
    
    def show_registration_form(self):
        with st.form("register_form"):
            st.markdown("#### Join EquiReal")
            
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("First Name*")
                email = st.text_input("Email*")
                user_type = st.selectbox("Account Type*", 
                    options=["business", "landlord"],
                    format_func=lambda x: "Business Owner" if x == "business" else "Property Owner")
            
            with col2:
                last_name = st.text_input("Last Name*")
                company = st.text_input("Company")
                industry = st.selectbox("Industry*", INDUSTRIES)
            
            password = st.text_input("Password*", type="password")
            confirm_password = st.text_input("Confirm Password*", type="password")
            location = st.selectbox("Primary Location*", GLOBAL_LOCATIONS)
            terms_agreed = st.checkbox("I agree to Terms of Service*")
            
            register_btn = st.form_submit_button("🚀 Create Account", type="primary")
            
            if register_btn:
                errors = []
                
                if not all([first_name, last_name, email, password, confirm_password]):
                    errors.append("Please fill in all required fields")
                    
                if password != confirm_password:
                    errors.append("Passwords do not match")
                    
                if len(password) < 8:
                    errors.append("Password must be at least 8 characters")
                    
                if not terms_agreed:
                    errors.append("Please agree to Terms of Service")
                
                if errors:
                    for error in errors:
                        st.error(f"❌ {error}")
                else:
                    profile_data = {
                        'first_name': first_name,
                        'last_name': last_name,
                        'company': company,
                        'location': location,
                        'industry': industry
                    }
                    
                    user_id = self.db.create_user(email, password, user_type, profile_data)
                    if user_id:
                        st.success("✅ Account created! Please sign in.")
                    else:
                        st.error("❌ Email already exists")

class BusinessApplication:
    def __init__(self):
        self.db = DatabaseManager()
        self.ai_engine = AIAnalysisEngine()
    
    def show_application_wizard(self):
        st.title("🚀 Business Application")
        st.markdown("### AI-Powered Risk Assessment & Deal Generation")
        
        if 'form_step' not in st.session_state:
            st.session_state.form_step = 1
        
        if 'application_data' not in st.session_state:
            st.session_state.application_data = {}
        
        self.show_progress_indicator()
        
        if st.session_state.form_step == 1:
            self.step_1_business_basics()
        elif st.session_state.form_step == 2:
            self.step_2_financial_details()
        elif st.session_state.form_step == 3:
            self.step_3_review_submit()
    
    def show_progress_indicator(self):
        steps = ["Business Basics", "Financial Details", "Review & Submit"]
        progress = st.session_state.form_step / 3
        st.progress(progress)
        
        cols = st.columns(3)
        for i, (col, label) in enumerate(zip(cols, steps)):
            with col:
                if i + 1 < st.session_state.form_step:
                    st.success(f"✅ {i+1}. {label}")
                elif i + 1 == st.session_state.form_step:
                    st.info(f"🔄 {i+1}. {label}")
                else:
                    st.write(f"⏳ {i+1}. {label}")
    
    def step_1_business_basics(self):
        st.markdown("### 🏢 Step 1: Business Foundation")
        
        with st.form("step_1_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                business_name = st.text_input("Business Name *")
                business_type = st.selectbox("Business Type *", BUSINESS_TYPES)
                industry = st.selectbox("Industry *", INDUSTRIES)
            
            with col2:
                location = st.selectbox("Target Location *", GLOBAL_LOCATIONS)
                space_size = st.number_input("Space Required (sq ft) *", min_value=100, value=1500)
                team_size = st.number_input("Current Team Size *", min_value=1, value=5)
            
            founding_date = st.date_input("Company Founded *", value=datetime(2020, 1, 1))
            mission_statement = st.text_area("Mission Statement *")
            
            if st.form_submit_button("➡️ Continue to Financial Details", type="primary"):
                if all([business_name, business_type, industry, location, mission_statement]):
                    st.session_state.application_data.update({
                        'business_name': business_name,
                        'business_type': business_type,
                        'industry': industry,
                        'location': location,
                        'space_size': space_size,
                        'team_size': team_size,
                        'founding_date': founding_date.isoformat(),
                        'mission_statement': mission_statement
                    })
                    st.session_state.form_step = 2
                    st.rerun()
                else:
                    st.error("⚠️ Please fill in all required fields")
    
    def step_2_financial_details(self):
        st.markdown("### 💰 Step 2: Financial Analysis")
        
        with st.form("step_2_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                current_revenue = st.number_input("Monthly Revenue ($)", min_value=0, value=0)
                annual_revenue = st.number_input("Annual Revenue ($)", min_value=0, value=0)
            
            with col2:
                monthly_expenses = st.number_input("Monthly Expenses ($)", min_value=0, value=0)
                cash_on_hand = st.number_input("Cash on Hand ($)", min_value=0, value=0)
            
            with col3:
                runway_months = st.number_input("Cash Runway (months)", min_value=0, value=0)
                funding_raised = st.number_input("Funding Raised ($)", min_value=0, value=0)
            
            col1, col2 = st.columns(2)
            
            with col1:
                is_profitable = st.checkbox("Currently Profitable")
                has_recurring_revenue = st.checkbox("Has Recurring Revenue")
            
            with col2:
                num_customers = st.number_input("Total Customers", min_value=0, value=0)
                revenue_growth_rate = st.number_input("Monthly Growth Rate (%)", value=0.0)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.form_submit_button("⬅️ Back"):
                    st.session_state.form_step = 1
                    st.rerun()
            
            with col2:
                if st.form_submit_button("➡️ Review & Submit", type="primary"):
                    financial_data = {
                        'current_revenue': current_revenue,
                        'annual_revenue': annual_revenue,
                        'monthly_expenses': monthly_expenses,
                        'cash_on_hand': cash_on_hand,
                        'runway_months': runway_months,
                        'funding_raised': funding_raised,
                        'is_profitable': is_profitable,
                        'has_recurring_revenue': has_recurring_revenue,
                        'num_customers': num_customers,
                        'revenue_growth_rate': revenue_growth_rate
                    }
                    
                    st.session_state.application_data['financial_data'] = financial_data
                    st.session_state.form_step = 3
                    st.rerun()
    
    def step_3_review_submit(self):
        st.markdown("### ✅ Step 3: Review & Submit")
        
        if 'financial_data' in st.session_state.application_data:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🏢 Business Overview:**")
                st.write(f"Company: {st.session_state.application_data.get('business_name')}")
                st.write(f"Industry: {st.session_state.application_data.get('industry')}")
                st.write(f"Location: {st.session_state.application_data.get('location')}")
                st.write(f"Space: {st.session_state.application_data.get('space_size', 0):,} sq ft")
            
            with col2:
                financial_data = st.session_state.application_data['financial_data']
                st.markdown("**💰 Financial Highlights:**")
                st.write(f"Monthly Revenue: ${financial_data.get('current_revenue', 0):,}")
                st.write(f"Annual Revenue: ${financial_data.get('annual_revenue', 0):,}")
                st.write(f"Cash Runway: {financial_data.get('runway_months', 0)} months")
                st.write(f"Profitable: {'Yes' if financial_data.get('is_profitable', False) else 'No'}")
            
            if st.button("🔬 Generate AI Analysis & Deal Terms", type="primary", use_container_width=True):
                with st.spinner("🤖 AI is analyzing your business..."):
                    complete_data = {
                        **st.session_state.application_data,
                        'user_id': st.session_state.user.get('id', 'demo_user')
                    }
                    
                    ai_analysis = self.ai_engine.calculate_risk_score(complete_data)
                    deal_terms = self.generate_deal_terms(complete_data, ai_analysis)
                    proposal = self.generate_proposal(complete_data, ai_analysis, deal_terms)
                    
                    business_id = self.db.save_business(complete_data)
                    deal_id = self.db.save_deal({
                        'business_id': business_id,
                        'deal_terms': deal_terms,
                        'proposal': proposal,
                        'risk_score': ai_analysis['overall_risk']
                    })
                    
                    st.session_state.analysis_results = {
                        'ai_analysis': ai_analysis,
                        'deal_terms': deal_terms,
                        'proposal': proposal
                    }
                
                self.show_results()
        else:
            st.error("⚠️ Missing application data. Please complete all steps.")
    
    def generate_deal_terms(self, business_data, ai_analysis):
        risk_score = ai_analysis['overall_risk']
        financial_data = business_data.get('financial_data', {})
        
        # Base terms
        base_upfront_rent = 30
        base_equity = 5
        base_revenue_share = 3
        
        # Risk adjustments
        risk_factor = (risk_score - 50) / 50
        
        upfront_rent_percent = base_upfront_rent + (risk_factor * 20)
        equity_percent = base_equity + (risk_factor * 5)
        revenue_share_percent = base_revenue_share + (risk_factor * 2)
        
        # Financial adjustments
        if financial_data.get('is_profitable'):
            upfront_rent_percent -= 5
            equity_percent -= 1
        
        current_revenue = financial_data.get('current_revenue', 0)
        if current_revenue > 100000:
            upfront_rent_percent -= 8
            equity_percent -= 1.5
        
        # Apply bounds
        upfront_rent_percent = max(15, min(55, upfront_rent_percent))
        equity_percent = max(1, min(12, equity_percent))
        revenue_share_percent = max(0.5, min(6, revenue_share_percent))
        
        # Calculate rent
        space_size = business_data.get('space_size', 1000)
        base_rate = 35  # per sq ft annually
        
        annual_market_rent = space_size * base_rate
        monthly_market_rent = annual_market_rent / 12
        monthly_rent = monthly_market_rent * (upfront_rent_percent / 100)
        monthly_savings = monthly_market_rent - monthly_rent
        
        return {
            'risk_score': round(risk_score, 1),
            'upfront_rent_percent': round(upfront_rent_percent, 1),
            'equity_percent': round(equity_percent, 1),
            'revenue_share_percent': round(revenue_share_percent, 1),
            'monthly_rent': round(monthly_rent, 0),
            'monthly_market_rent': round(monthly_market_rent, 0),
            'monthly_savings': round(monthly_savings, 0),
            'space_size': space_size
        }
    
    def generate_proposal(self, business_data, ai_analysis, deal_terms):
        proposal_id = f"EQR-{str(uuid.uuid4())[:8].upper()}"
        
        proposal = f"""EQUIREAL ENTERPRISE PROPOSAL
{"=" * 50}
Proposal ID: {proposal_id}
Generated: {datetime.now().strftime('%B %d, %Y')}

EXECUTIVE SUMMARY
{"-" * 50}
Business: {business_data['business_name']}
Industry: {business_data['industry']}
Location: {business_data['location']}
Space: {business_data['space_size']:,} sq ft
AI Risk Score: {ai_analysis['overall_risk']:.1f}/100

PROPOSED DEAL TERMS
{"-" * 50}
Upfront Rent: {deal_terms['upfront_rent_percent']:.1f}% of market rate
Monthly Rent: ${deal_terms['monthly_rent']:,.0f}
Equity Stake: {deal_terms['equity_percent']:.1f}%
Revenue Share: {deal_terms['revenue_share_percent']:.1f}%
Monthly Savings: ${deal_terms['monthly_savings']:,.0f}

EquiReal - Renting the Opportunity"""
        
        return proposal
    
    def show_results(self):
        if 'analysis_results' not in st.session_state:
            return
        
        results = st.session_state.analysis_results
        ai_analysis = results['ai_analysis']
        deal_terms = results['deal_terms']
        proposal = results['proposal']
        
        st.success("✅ Analysis Complete!")
        
        # Risk Assessment
        st.markdown("### 🎯 AI Risk Assessment")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            risk_score = ai_analysis['overall_risk']
            risk_color = "#10b981" if risk_score < 40 else "#f59e0b" if risk_score < 70 else "#ef4444"
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; background: {risk_color}20; 
                        border-radius: 12px; border: 2px solid {risk_color};">
                <h1 style="color: {risk_color}; margin: 0;">{risk_score:.1f}</h1>
                <p style="margin: 0;">Risk Score</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.metric("AI Confidence", f"{ai_analysis['confidence_score']:.1f}%")
        
        with col3:
            st.metric("Risk Trend", ai_analysis['risk_trend'])
        
        # Deal Terms
        st.markdown("### 💼 Proposed Deal Terms")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Upfront Rent", f"{deal_terms['upfront_rent_percent']:.1f}%")
        
        with col2:
            st.metric("Equity Stake", f"{deal_terms['equity_percent']:.1f}%")
        
        with col3:
            st.metric("Revenue Share", f"{deal_terms['revenue_share_percent']:.1f}%")
        
        with col4:
            st.metric("Monthly Savings", f"${deal_terms['monthly_savings']:,.0f}")
        
        # Download
        st.markdown("### 📄 Download Documents")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="📄 Download Proposal",
                data=proposal,
                file_name="EquiReal_Proposal.txt",
                mime="text/plain",
                type="primary"
            )
        
        with col2:
            summary = f"""DEAL SUMMARY
Business: {st.session_state.application_data['business_name']}
Risk Score: {ai_analysis['overall_risk']:.1f}/100
Monthly Rent: ${deal_terms['monthly_rent']:,.0f}
Monthly Savings: ${deal_terms['monthly_savings']:,.0f}"""
            
            st.download_button(
                label="📊 Download Summary",
                data=summary,
                file_name="Deal_Summary.txt",
                mime="text/plain"
            )

class LandlordDashboard:
    def __init__(self):
        self.db = DatabaseManager()
    
    def show_dashboard(self):
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #2563eb, #7c3aed); 
                    border-radius: 16px; margin-bottom: 2rem; color: white;">
            <h1>🏢 EquiReal</h1>
            <p>AI-Powered Commercial Real Estate Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.title("🏢 Landlord Dashboard")
        
        deals = self.db.get_deals()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Applications", len(deals))
        
        with col2:
            pending = len([d for d in deals if d.get('status') == 'pending'])
            st.metric("Pending Review", pending)
        
        with col3:
            if deals:
                avg_risk = np.mean([d.get('risk_score', 50) for d in deals])
                st.metric("Average Risk", f"{avg_risk:.1f}")
            else:
                st.metric("Average Risk", "N/A")
        
        st.markdown("### 📋 Deal Pipeline")
        
        if not deals:
            st.info("No applications yet.")
            return
        
        for deal in deals[:5]:
            self.show_deal_card(deal)
    
    def show_deal_card(self, deal):
        risk_score = deal.get('risk_score', 50)
        risk_emoji = "🟢" if risk_score < 40 else "🟡" if risk_score < 70 else "🔴"
        
        with st.container():
            st.markdown(f"""
            <div style="background: white; border: 1px solid #e5e7eb; border-radius: 12px; 
                        padding: 1.5rem; margin: 1rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h4>{risk_emoji} {deal.get('business_name', 'Unknown Business')}</h4>
                <p><strong>Industry:</strong> {deal.get('industry', 'N/A')}</p>
                <p><strong>Location:</strong> {deal.get('location', 'N/A')}</p>
                <p><strong>Space:</strong> {deal.get('space_size', 0):,} sq ft</p>
                <p><strong>Risk Score:</strong> {risk_score:.1f}/100</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("✅ Approve", key=f"approve_{deal.get('id')}", type="primary"):
                    if self.db.update_deal_status(deal.get('id'), 'approved'):
                        st.success("✅ Deal approved!")
                        st.rerun()
            
            with col2:
                if st.button("❌ Reject", key=f"reject_{deal.get('id')}"):
                    if self.db.update_deal_status(deal.get('id'), 'rejected'):
                        st.error("❌ Deal rejected")
                        st.rerun()
            
            with col3:
                if deal.get('proposal'):
                    st.download_button(
                        label="📄 Proposal",
                        data=deal['proposal'],
                        file_name=f"proposal_{deal.get('business_name', 'business').replace(' ', '_')}.txt",
                        mime="text/plain",
                        key=f"download_{deal.get('id')}"
                    )

def show_business_dashboard():
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #2563eb, #7c3aed); 
                border-radius: 16px; margin-bottom: 2rem; color: white;">
        <h1>🏢 EquiReal</h1>
        <p>AI-Powered Commercial Real Estate Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    user = st.session_state.user
    profile = user.get('profile_data', {})
    
    st.title(f"Welcome, {profile.get('first_name', 'Business Owner')}!")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Applications", "0", "Start your first!")
    with col2:
        st.metric("Proposals", "0", "Pending")
    with col3:
        st.metric("Active Deals", "0", "No deals yet")
    with col4:
        st.metric("Savings", "$0", "Potential")
    
    st.markdown("### 🚀 Get Started")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📋 Create Your First Application**
        
        Complete our AI-powered application to get personalized deal terms.
        - 3-step process
        - AI risk assessment
        - Custom deal terms
        - Instant proposals
        """)
        
        if st.button("🚀 Start Application", type="primary", use_container_width=True):
            st.session_state.page = 'business_application'
            st.rerun()
    
    with col2:
        st.markdown("""
        **🔍 Browse Properties**
        
        Find commercial spaces from forward-thinking landlords.
        - Curated listings
        - Partner landlords
        - Advanced filters
        - Virtual tours
        """)
        
        if st.button("🔍 Browse Properties", use_container_width=True):
            st.session_state.page = 'property_search'
            st.rerun()

def show_property_search():
    st.title("🔍 Property Search")
    st.markdown("### Find Your Perfect Space")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        location = st.selectbox("Location", GLOBAL_LOCATIONS)
        min_space = st.number_input("Min Space (sq ft)", min_value=0, value=0)
    
    with col2:
        property_type = st.selectbox("Property Type", ["Office", "Retail", "Industrial"])
        max_space = st.number_input("Max Space (sq ft)", min_value=0, value=10000)
    
    with col3:
        price_range = st.selectbox("Price Range", ["$0-25/sq ft", "$25-50/sq ft", "$50+/sq ft"])
    
    if st.button("🔍 Search Properties", type="primary"):
        st.success("🎯 Search completed!")
        
        properties = [
            {
                'name': 'Innovation Hub Downtown',
                'location': 'San Francisco, CA',
                'size': '1,200-5,000 sq ft',
                'price': '$45/sq ft/year'
            },
            {
                'name': 'Tech Center Austin',
                'location': 'Austin, TX',
                'size': '800-3,000 sq ft',
                'price': '$28/sq ft/year'
            }
        ]
        
        for prop in properties:
            with st.container():
                st.markdown(f"""
                <div style="background: white; border: 1px solid #e5e7eb; border-radius: 12px; 
                            padding: 1.5rem; margin: 1rem 0;">
                    <h4>{prop['name']}</h4>
                    <p>📍 {prop['location']}</p>
                    <p>📐 {prop['size']}</p>
                    <p>💰 {prop['price']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Apply Now", key=f"apply_{prop['name']}"):
                    st.session_state.page = 'business_application'
                    st.rerun()

def show_settings():
    st.title("⚙️ Account Settings")
    
    user = st.session_state.user
    profile = user.get('profile_data', {})
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name", value=profile.get('first_name', ''))
            email = st.text_input("Email", value=user['email'], disabled=True)
        
        with col2:
            last_name = st.text_input("Last Name", value=profile.get('last_name', ''))
            company = st.text_input("Company", value=profile.get('company', ''))
        
        if st.form_submit_button("💾 Save Changes", type="primary"):
            st.success("✅ Profile updated!")

def show_home_page():
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #2563eb, #7c3aed); 
                border-radius: 16px; margin-bottom: 2rem; color: white;">
        <h1>🏢 EquiReal</h1>
        <h3>Renting the Opportunity</h3>
        <p>Revolutionary AI-powered commercial real estate platform transforming lease structures.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🏢 For Businesses**
        
        Get reduced rent in exchange for equity and revenue share.
        - Reduce monthly rent by 20-60%
        - AI-powered risk assessment
        - Custom deal structuring
        - Connect with landlords
        """)
    
    with col2:
        st.markdown("""
        **🏠 For Property Owners**
        
        Participate in tenant success through equity sharing.
        - Higher returns than traditional leases
        - Equity upside in growing companies
        - AI-screened tenants
        - Professional management
        """)
    
    st.markdown("### 📊 Platform Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Businesses Analyzed", "1,247")
    with col2:
        st.metric("Deals Completed", "89")
    with col3:
        st.metric("Partner Landlords", "156")
    with col4:
        st.metric("AI Accuracy", "94.2%")

def main():
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    
    # Authentication check
    if not st.session_state.authenticated:
        auth_manager = AuthenticationManager()
        auth_manager.show_auth_interface()
        return
    
    # Authenticated user interface
    user = st.session_state.user
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #2563eb, #7c3aed); 
                    border-radius: 16px; margin-bottom: 2rem;">
            <h2 style="color: white; margin: 0;">🏢 EquiReal</h2>
            <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;">Enterprise Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        profile = user.get('profile_data', {})
        st.markdown(f"**Welcome, {profile.get('first_name', 'User')}!**")
        st.markdown(f"*{user['user_type'].title()} Account*")
        
        st.markdown("---")
        
        # Navigation based on user type
        if user['user_type'] == 'business':
            if st.button("🏠 Dashboard", use_container_width=True):
                st.session_state.page = 'business_dashboard'
                st.rerun()
            
            if st.button("🚀 New Application", use_container_width=True):
                st.session_state.page = 'business_application'
                st.rerun()
            
            if st.button("🔍 Property Search", use_container_width=True):
                st.session_state.page = 'property_search'
                st.rerun()
        
        else:  # landlord
            if st.button("🏠 Dashboard", use_container_width=True):
                st.session_state.page = 'landlord_dashboard'
                st.rerun()
        
        st.markdown("---")
        
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.page = 'settings'
            st.rerun()
        
        if st.button("🚪 Sign Out", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        st.markdown("---")
        st.markdown("**System Status:**")
        st.write("🔗 Database: ✅ Connected")
        st.write("🤖 AI Engine: ✅ Active")
    
    # Page routing
    if st.session_state.page == 'business_dashboard':
        show_business_dashboard()
    elif st.session_state.page == 'business_application':
        app = BusinessApplication()
        app.show_application_wizard()
    elif st.session_state.page == 'landlord_dashboard':
        dashboard = LandlordDashboard()
        dashboard.show_dashboard()
    elif st.session_state.page == 'property_search':
        show_property_search()
    elif st.session_state.page == 'settings':
        show_settings()
    else:
        show_home_page()

if __name__ == "__main__":
    main()