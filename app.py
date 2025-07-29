"""
Gusto Data Agent - Demo
======================
AI-powered SQL generation for Gusto data warehouse
"""

import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Gusto Data Agent", page_icon="🏢", layout="wide")

def generate_sql(query):
<<<<<<< HEAD
    """Generate SQL based on natural language query - Mock implementation"""
    q = query.lower()
    
=======
    q = query.lower()
>>>>>>> 5d3ea4924ee8e99ba7ee8299af546148a56bf072
    if "credit delinquencies" in q and "30 days" in q:
        return """SELECT c.company_name, c.state, cd.delinquency_date, cd.amount, cd.status
FROM bi.companies c
JOIN bi.credit_delinquencies cd ON c.company_id = cd.company_id
WHERE cd.delinquency_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY cd.delinquency_date DESC;"""
<<<<<<< HEAD
    
=======
>>>>>>> 5d3ea4924ee8e99ba7ee8299af546148a56bf072
    elif "employee count" in q:
        return """SELECT company_name, state, employee_count
FROM bi.companies
ORDER BY employee_count DESC
LIMIT 10;"""
<<<<<<< HEAD
    
=======
>>>>>>> 5d3ea4924ee8e99ba7ee8299af546148a56bf072
    elif "california" in q or "risk" in q:
        return """SELECT c.company_name, c.state, COUNT(cd.company_id) AS risk_score
FROM bi.companies c
LEFT JOIN bi.credit_delinquencies cd ON c.company_id = cd.company_id
WHERE c.state = 'CA'
GROUP BY c.company_id, c.company_name, c.state
ORDER BY risk_score DESC;"""
<<<<<<< HEAD
    
    elif "payments" in q or "revenue" in q:
        return """SELECT company_name, SUM(payment_amount) as total_payments
FROM bi.companies c
JOIN bi_reporting.gusto_payments_and_losses gpl ON c.company_id = gpl.company_id
GROUP BY company_name
ORDER BY total_payments DESC
LIMIT 10;"""
    
    elif "penalties" in q:
        return """SELECT c.company_name, pg.penalty_type, COUNT(*) as penalty_count
FROM bi.companies c
JOIN bi.penalty_cases pc ON c.company_id = pc.company_id
JOIN bi.penalty_groups pg ON pc.penalty_group_id = pg.id
GROUP BY c.company_name, pg.penalty_type
ORDER BY penalty_count DESC;"""
    
=======
>>>>>>> 5d3ea4924ee8e99ba7ee8299af546148a56bf072
    else:
        return """SELECT company_name, state, employee_count
FROM bi.companies
LIMIT 100;"""

def generate_data(sql):
<<<<<<< HEAD
    """Generate mock data based on SQL query"""
=======
>>>>>>> 5d3ea4924ee8e99ba7ee8299af546148a56bf072
    if "credit_delinquencies" in sql:
        return [
            {"company_name": "TechStart Inc", "state": "CA", "delinquency_date": "2024-01-15", "amount": 15000, "status": "Active"},
            {"company_name": "DataFlow LLC", "state": "NY", "delinquency_date": "2024-01-12", "amount": 8500, "status": "Active"},
<<<<<<< HEAD
            {"company_name": "CloudOps Corp", "state": "TX", "delinquency_date": "2024-01-08", "amount": 12750, "status": "Active"},
            {"company_name": "SecureNet Systems", "state": "FL", "delinquency_date": "2024-01-05", "amount": 22000, "status": "Resolved"},
            {"company_name": "ModernApps Co", "state": "WA", "delinquency_date": "2024-01-03", "amount": 9800, "status": "Active"}
=======
            {"company_name": "CloudOps Corp", "state": "TX", "delinquency_date": "2024-01-08", "amount": 12750, "status": "Active"}
>>>>>>> 5d3ea4924ee8e99ba7ee8299af546148a56bf072
        ]
    elif "employee_count" in sql:
        return [
            {"company_name": "MegaCorp Industries", "state": "CA", "employee_count": 2847},
            {"company_name": "Global Tech Solutions", "state": "NY", "employee_count": 1923},
<<<<<<< HEAD
            {"company_name": "Innovation Labs", "state": "TX", "employee_count": 1456},
            {"company_name": "Enterprise Systems", "state": "IL", "employee_count": 1234},
            {"company_name": "Digital Dynamics", "state": "WA", "employee_count": 987}
        ]
    elif "risk_score" in sql:
        return [
            {"company_name": "HighRisk Ventures", "state": "CA", "risk_score": 8},
            {"company_name": "CautionCorp", "state": "CA", "risk_score": 5},
            {"company_name": "StableTech Inc", "state": "CA", "risk_score": 2},
            {"company_name": "SecureOps LLC", "state": "CA", "risk_score": 1},
            {"company_name": "SafeGuard Systems", "state": "CA", "risk_score": 0}
        ]
    elif "payments" in sql:
        return [
            {"company_name": "PaymentPro Inc", "total_payments": 1250000},
            {"company_name": "RevenueCorp", "total_payments": 980000},
            {"company_name": "CashFlow Solutions", "total_payments": 750000},
            {"company_name": "MoneyMakers LLC", "total_payments": 650000},
            {"company_name": "FinTech Innovations", "total_payments": 500000}
        ]
    elif "penalties" in sql:
        return [
            {"company_name": "ComplianceFail Corp", "penalty_type": "Late Filing", "penalty_count": 12},
            {"company_name": "RegulationIgnore LLC", "penalty_type": "Tax Violation", "penalty_count": 8},
            {"company_name": "LatePayment Inc", "penalty_type": "Payment Default", "penalty_count": 6},
            {"company_name": "RuleBreaker Co", "penalty_type": "Compliance Issue", "penalty_count": 4}
=======
            {"company_name": "Innovation Labs", "state": "TX", "employee_count": 1456}
>>>>>>> 5d3ea4924ee8e99ba7ee8299af546148a56bf072
        ]
    else:
        return [
            {"company_name": "Sample Corp", "state": "CA", "employee_count": 145},
<<<<<<< HEAD
            {"company_name": "Demo LLC", "state": "NY", "employee_count": 87},
            {"company_name": "Test Industries", "state": "TX", "employee_count": 203},
            {"company_name": "Example Co", "state": "FL", "employee_count": 156}
        ]

# Main App UI
st.title("🏢 Gusto Data Agent")
st.subheader("AI-powered SQL generation for Gusto data warehouse")

# Demo mode notice
st.info("🎮 **Demo Mode**: Showcasing interface with realistic mock data")

# Create two columns for layout
=======
            {"company_name": "Demo LLC", "state": "NY", "employee_count": 87}
        ]

st.title("🏢 Gusto Data Agent")
st.subheader("AI-powered SQL generation for Gusto data warehouse")
st.info("🎮 Demo Mode: Showcasing interface with realistic mock data")

>>>>>>> 5d3ea4924ee8e99ba7ee8299af546148a56bf072
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("💬 Ask Your Data Question")
    
<<<<<<< HEAD
    # Example queries
    examples = [
        "Show me all companies with credit delinquencies in the last 30 days",
        "List top 10 companies by employee count", 
        "Find companies in California with high risk scores",
        "Show total payments by company",
        "List companies with the most penalties"
    ]
    
    # Quick example buttons
=======
    examples = [
        "Show me all companies with credit delinquencies in the last 30 days",
        "List top 10 companies by employee count", 
        "Find companies in California with high risk scores"
    ]
    
>>>>>>> 5d3ea4924ee8e99ba7ee8299af546148a56bf072
    for i, example in enumerate(examples):
        if st.button(f"📝 {example}", key=i):
            st.session_state.query = example
    
<<<<<<< HEAD
    # Text input for custom queries
    query = st.text_area(
        "Enter your question:",
        value=st.session_state.get('query', ''),
        placeholder="e.g., Show me companies with credit delinquencies",
        height=100
=======
    query = st.text_area(
        "Enter your question:",
        value=st.session_state.get('query', ''),
        placeholder="e.g., Show me companies with credit delinquencies"
>>>>>>> 5d3ea4924ee8e99ba7ee8299af546148a56bf072
    )
    
    if st.button("🚀 Generate SQL & Execute", type="primary"):
        if query:
<<<<<<< HEAD
            with st.spinner("Generating SQL and fetching results..."):
                # Generate SQL
                sql = generate_sql(query)
                
                st.subheader("📝 Generated SQL")
                st.code(sql, language="sql")
                
                # Generate and display results
                results = generate_data(sql)
                st.subheader("📊 Results")
                
                if results:
                    df = pd.DataFrame(results)
                    st.dataframe(df, use_container_width=True)
                    
                    # Download button
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"gusto_data_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                    
                    # Simple chart if numeric data exists
                    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
                    if len(numeric_cols) > 0 and len(df) > 1:
                        st.subheader("📈 Quick Visualization")
                        chart_col = st.selectbox("Select column to chart:", numeric_cols)
                        if 'company_name' in df.columns:
                            fig = st.bar_chart(data=df.set_index('company_name')[chart_col])
                        else:
                            fig = st.line_chart(data=df[chart_col])
                else:
                    st.warning("No results found for your query.")
=======
            sql = generate_sql(query)
            st.subheader("📝 Generated SQL")
            st.code(sql, language="sql")
            
            results = generate_data(sql)
            st.subheader("📊 Results")
            df = pd.DataFrame(results)
            st.dataframe(df)
            
            csv = df.to_csv(index=False)
            st.download_button("📥 Download CSV", csv, "results.csv")
>>>>>>> 5d3ea4924ee8e99ba7ee8299af546148a56bf072
        else:
            st.warning("Please enter a query")

with col2:
    st.subheader("ℹ️ About")
    st.markdown("""
<<<<<<< HEAD
    **Gusto Data Agent** converts natural language into SQL queries for analyzing Gusto warehouse data.
    
    **Features:**
    - 🧠 AI-powered SQL generation
    - 📊 Access to all Gusto warehouse tables  
    - 🔒 Read-only database safety
    - 💾 CSV export capabilities
    - 📈 Quick data visualizations
    """)
    
    st.subheader("🗄️ Available Tables")
    tables = [
        "bi.companies",
        "bi.credit_delinquencies", 
        "bi.gusto_employees",
        "bi_reporting.gusto_payments_and_losses",
        "bi.penalty_cases",
        "bi.nacha_entries",
        "zenpayroll_production_no.session_events"
    ]
    
    for table in tables:
        st.text(f"• {table}")
    
    st.markdown("*...and 20+ more tables*")
    
    st.subheader("💡 Tips")
    st.markdown("""
    - Be specific in your requests
    - Mention time ranges when needed
    - Ask for "top N" results to limit output
    - Use business terms like "delinquencies" or "penalties"
    """)

# Footer
st.markdown("---")
st.markdown("**🏢 Built for Gusto Data Team** | Demo Version with Mock Data")
=======
    **Gusto Data Agent** converts natural language into SQL queries.
    
    **Features:**
    - 🧠 AI-powered SQL generation
    - 📊 Gusto warehouse tables  
    - 🔒 Read-only safety
    - 💾 CSV export
    """)
    
    st.subheader("🗄️ Tables")
    tables = ["bi.companies", "bi.credit_delinquencies", "bi.gusto_employees"]
    for table in tables:
        st.text(f"• {table}")

st.markdown("---")
st.markdown("**🏢 Built for Gusto Data Team**")
>>>>>>> 5d3ea4924ee8e99ba7ee8299af546148a56bf072
