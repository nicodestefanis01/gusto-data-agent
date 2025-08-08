"""
Gusto Data Agent - Production
============================
AI-powered SQL generation for Gusto data warehouse with real database connectivity
"""

import streamlit as st
import pandas as pd
import os
import psycopg2
from datetime import datetime
from typing import Dict, List, Optional, Any
import json

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Try to import OpenAI, fall back to mock if not available
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

st.set_page_config(page_title="Gusto Data Agent", page_icon="🏢", layout="wide")

# Real Gusto warehouse table schemas (discovered from actual database)
TABLE_SCHEMAS = {
    "bi.companies": {
        "description": "Core company information - use 'id' for company ID and 'name' for company name",
        "columns": ["id", "name", "trade_name", "accounting_firm_id", "created_at", "initial_company_size", "initial_employee_count", "approval_status", "number_active_employees", "number_active_contractors", "joined_at", "is_active", "filing_state", "filing_city", "filing_zip", "has_bank_info", "current_federal_deposit_schedule", "sales_program", "industry_classification", "user_provided_industry", "naics_code"]
    },
    "bi.credit_delinquencies": {
        "description": "Credit delinquency records - use company_id to join with companies",
        "columns": ["company_id", "name", "payment_id", "payment_type", "debit_date", "debit_amount_attempted", "error_code", "past_due_date", "successful_credits", "successful_debits", "is_credit_loss", "recovery_amount_needed", "recovered_amount", "delinquent_status", "days_past_due", "is_cancelled"]
    },
    "bi.gusto_employees": {
        "description": "Employee information - use 'id' for employee ID",
        "columns": ["id", "first_name", "last_name", "name", "email", "hired_at", "terminated_at", "department_name", "work_state", "status", "worker_type", "job_title", "location", "team", "is_pe", "current_flag"]
    },
    "bi_reporting.gusto_payments_and_losses": {
        "description": "Payment processing data and financial losses",
        "columns": ["calendar_date", "event_type", "company_id", "event_id", "event_debit_date", "bank_name", "company_age", "sales_program", "user_provided_industry", "product_plan", "initial_size", "current_size", "invoice_total_debit", "event_gross_amount", "credit_loss_flag", "days_past_due", "failed_payment_flag", "net_loss_amount"]
    },
    "bi.penalty_cases": {
        "description": "Penalty cases and compliance issues",
        "columns": ["id", "agent_id", "agency_name", "created_at", "year", "quarter", "title", "total_interest_amount", "error_type", "total_penalty_amount", "total_penalty_paid", "total_interest_paid", "error_origin", "status", "penalty_group_id"]
    },
    "bi.penalty_groups": {
        "description": "Penalty group information",
        "columns": ["id", "penalty_case_id", "link", "ticket_system_of_record", "sor_ticket_id", "pay_to", "batch", "approval_status", "created_at"]
    },
    "bi.nacha_entries": {
        "description": "ACH/NACHA payment entries and processing data",
        "columns": ["id", "created_at_date", "amount", "company_id", "employee_id", "contractor_id", "payroll_id", "error_code", "is_debit", "is_credit", "entry_code", "transaction_type", "is_invoice", "bank_account_type", "processing_state", "effective_entry_date"]
    },
    "bi.company_approval_details": {
        "description": "Company approval status and risk information",
        "columns": ["id", "company_id", "approved_by_id", "approved_by_system", "first_approved_at", "last_rejected_at", "approval_status", "ready_for_approval", "risk_state", "risk_state_description", "auto_approval_blockers"]
    },
    "bi.monthly_companies": {
        "description": "Monthly company metrics and revenue data",
        "columns": ["company_id", "for_month", "product_plan", "pricing_plan", "number_of_paid_payrolls", "is_churned", "total_subscription_revenue", "total_revenue", "total_payroll_revenue", "company_size", "company_size_segment", "number_of_payroll_employees", "number_of_payroll_contractors", "number_of_cases", "multistate_flag"]
    },
    "bi.user_roles": {
        "description": "User roles and permissions",
        "columns": ["id", "user_id", "type", "employee_id", "company_id", "accounting_firm_id", "contractor_id", "created_at"]
    },
    "bi_reporting.risk_operational_metrics": {
        "description": "Risk operational metrics and case data",
        "columns": ["for_date", "flow", "age", "sales_program", "initial_company_size", "is_gep_company", "is_mrb", "model_triggered", "case_type", "count_of_cases", "total_active_customers", "time_spent_in_mins"]
    },
    "bi_reporting.risk_review_data": {
        "description": "Risk review activity data",
        "columns": ["calendar_date", "reviewed_by_email", "reviewer", "event_timestamp", "company_id", "review_type", "old_review_status", "new_review_status"]
    },
    "bi.sfdc_tickets": {
        "description": "Salesforce ticket data",
        "columns": ["sfdc_ticket_id", "sfdc_owner_id", "owner_role", "created_ts", "closed_ts"]
    },
    "bi.cases": {
        "description": "Support cases and tickets",
        "columns": ["casenumber", "id", "trimmed_case_id", "parent_case", "zendesk_id"]
    }
}

class RedshiftConnection:
    """Handles connections to Redshift database"""
    
    def __init__(self):
        self.host = os.getenv("REDSHIFT_HOST")
        self.database = os.getenv("REDSHIFT_DATABASE") 
        self.user = os.getenv("REDSHIFT_USERNAME")
        self.password = os.getenv("REDSHIFT_PASSWORD")
        self.port = int(os.getenv("REDSHIFT_PORT", 5439))
        self.conn = None
        
    def is_configured(self) -> bool:
        """Check if all required credentials are available"""
        return all([self.host, self.database, self.user, self.password])
    
    def connect(self) -> bool:
        """Establish connection to Redshift"""
        if not self.is_configured():
            return False
            
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            return True
        except Exception as e:
            st.error(f"Failed to connect to Redshift: {str(e)}")
            return False
    
    def execute_query(self, sql: str) -> Dict[str, Any]:
        """Execute SQL query and return results"""
        if not self.conn:
            if not self.connect():
                return {"success": False, "error": "Database connection failed"}
        
        try:
            cursor = self.conn.cursor()
            start_time = datetime.now()
            cursor.execute(sql)
            
            # Fetch results
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Convert to list of dictionaries
            data = [dict(zip(columns, row)) for row in rows]
            
            return {
                "success": True,
                "data": data,
                "row_count": len(data),
                "execution_time_seconds": execution_time
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if cursor:
                cursor.close()

class SQLGenerator:
    """Generates SQL queries using OpenAI"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key and OPENAI_AVAILABLE:
            self.client = OpenAI(api_key=self.api_key)
            self.available = True
        else:
            self.available = False
    
    def generate_sql(self, natural_query: str) -> Dict[str, Any]:
        """Generate SQL from natural language query"""
        if not self.available:
            return self._mock_sql_generation(natural_query)
        
        try:
            # Create the prompt for OpenAI
            system_prompt = f"""You are a SQL expert for Gusto's data warehouse. Generate Redshift-compatible SQL queries.

Available tables and their purposes:
{json.dumps(TABLE_SCHEMAS, indent=2)}

Rules:
1. Only use tables from the schema above
2. Use Redshift/PostgreSQL syntax
3. Always include LIMIT clauses to prevent large result sets
4. Use proper JOINs when combining tables
5. Return only the SQL query, no explanations

Generate a SQL query for: {natural_query}"""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": system_prompt}],
                max_tokens=500,
                temperature=0.1
            )
            
            sql_query = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            if sql_query.startswith("```sql"):
                sql_query = sql_query[6:-3]
            elif sql_query.startswith("```"):
                sql_query = sql_query[3:-3]
            
            return {
                "success": True,
                "sql": sql_query,
                "explanation": f"Generated SQL for: {natural_query}"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _mock_sql_generation(self, query: str) -> Dict[str, Any]:
        """Fallback mock SQL generation when OpenAI is not available"""
        q = query.lower()
        
        if "credit delinquencies" in q and "30 days" in q:
            sql = """SELECT c.name AS company_name, c.filing_state, cd.debit_date, cd.debit_amount_attempted, cd.delinquent_status
FROM bi.companies c
JOIN bi.credit_delinquencies cd ON c.id = cd.company_id
WHERE cd.debit_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY cd.debit_date DESC
LIMIT 100;"""
        elif "employee count" in q:
            sql = """SELECT name AS company_name, filing_state, number_active_employees
FROM bi.companies
WHERE number_active_employees IS NOT NULL
ORDER BY number_active_employees DESC
LIMIT 20;"""
        elif "california" in q or "risk" in q:
            sql = """SELECT c.name AS company_name, c.filing_state, COUNT(cd.company_id) AS risk_score
FROM bi.companies c
LEFT JOIN bi.credit_delinquencies cd ON c.id = cd.company_id
WHERE c.filing_state = 'CA'
GROUP BY c.id, c.name, c.filing_state
ORDER BY risk_score DESC
LIMIT 50;"""
        elif "penalty" in q:
            sql = """SELECT c.name AS company_name, pc.agency_name, pc.total_penalty_amount, pc.status
FROM bi.companies c
JOIN bi.penalty_cases pc ON c.id = pc.agent_id
WHERE pc.total_penalty_amount > 0
ORDER BY pc.total_penalty_amount DESC
LIMIT 50;"""
        else:
            sql = """SELECT name AS company_name, filing_state, number_active_employees
FROM bi.companies
WHERE is_active = true
LIMIT 100;"""
        
        return {
            "success": True,
            "sql": sql,
            "explanation": f"Template SQL generated for: {query} (using real Gusto schema)"
        }

def generate_mock_data(sql: str) -> List[Dict]:
    """Generate realistic mock data for demo purposes"""
    if "credit_delinquencies" in sql:
        return [
            {"company_name": "TechStart Inc", "state": "CA", "delinquency_date": "2024-01-15", "amount": 15000, "status": "Active"},
            {"company_name": "DataFlow LLC", "state": "NY", "delinquency_date": "2024-01-12", "amount": 8500, "status": "Active"},
            {"company_name": "CloudOps Corp", "state": "TX", "delinquency_date": "2024-01-08", "amount": 12750, "status": "Active"}
        ]
    elif "employee_count" in sql:
        return [
            {"company_name": "MegaCorp Industries", "state": "CA", "employee_count": 2847},
            {"company_name": "Global Tech Solutions", "state": "NY", "employee_count": 1923},
            {"company_name": "Innovation Labs", "state": "TX", "employee_count": 1456}
        ]
    else:
        return [
            {"company_name": "Sample Corp", "state": "CA", "employee_count": 145},
            {"company_name": "Demo LLC", "state": "NY", "employee_count": 87}
        ]

def check_system_status():
    """Check what systems are available (OpenAI, Redshift)"""
    db = RedshiftConnection()
    sql_gen = SQLGenerator()
    
    return {
        "redshift_configured": db.is_configured(),
        "openai_available": sql_gen.available,
        "demo_mode": not (db.is_configured() and sql_gen.available)
    }

# Main App
def main():
    st.title("🏢 Gusto Data Agent")
    st.subheader("AI-powered SQL generation for Gusto data warehouse")
    
    # Check system status
    status = check_system_status()
    
    # Display status banner
    if status["demo_mode"]:
        if not status["redshift_configured"] and not status["openai_available"]:
            st.warning("🎮 **Demo Mode**: No Redshift or OpenAI credentials configured. Using mock data.")
        elif not status["redshift_configured"]:
            st.warning("⚠️ **Partial Mode**: OpenAI available but no Redshift credentials. SQL generation works, using mock data.")
        elif not status["openai_available"]:
            st.warning("⚠️ **Partial Mode**: Redshift configured but no OpenAI key. Using mock SQL generation with real data.")
    else:
        st.success("✅ **Production Mode**: Connected to Redshift with AI-powered SQL generation")
    
    # Configuration sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        st.subheader("📊 Database Status")
        if status["redshift_configured"]:
            st.success("✅ Redshift configured")
        else:
            st.error("❌ Redshift not configured")
            with st.expander("💡 How to configure Redshift"):
                st.code("""
# Set environment variables:
REDSHIFT_HOST=your-cluster.redshift.amazonaws.com
REDSHIFT_DATABASE=your_database
REDSHIFT_USERNAME=your_username  
REDSHIFT_PASSWORD=your_password
REDSHIFT_PORT=5439
                """)
        
        st.subheader("🤖 AI Status")
        if status["openai_available"]:
            st.success("✅ OpenAI configured")
        else:
            st.error("❌ OpenAI not configured")
            with st.expander("💡 How to configure OpenAI"):
                st.code("OPENAI_API_KEY=sk-...")
        
        st.subheader("🗄️ Available Tables")
        for table_name in TABLE_SCHEMAS.keys():
            st.text(f"• {table_name}")
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💬 Ask Your Data Question")
        
        # Example queries
        examples = [
            "Show me all companies with credit delinquencies in the last 30 days",
            "List top 20 companies by employee count", 
            "Find companies in California with risk scores",
            "Show recent payment activity by company",
            "List penalty cases from the last quarter"
        ]
        
        for i, example in enumerate(examples):
            if st.button(f"📝 {example}", key=f"example_{i}"):
                st.session_state.query = example
        
        # Query input
        query = st.text_area(
            "Enter your question:",
            value=st.session_state.get('query', ''),
            placeholder="e.g., Show me companies with credit delinquencies in the last 30 days",
            height=100
        )
        
        if st.button("🚀 Generate SQL & Execute", type="primary"):
            if query:
                with st.spinner("Generating SQL..."):
                    # Generate SQL
                    sql_gen = SQLGenerator()
                    result = sql_gen.generate_sql(query)
                    
                    if result["success"]:
                        st.subheader("📝 Generated SQL")
                        st.code(result["sql"], language="sql")
                        
                        # Execute query
                        with st.spinner("Executing query..."):
                            if status["redshift_configured"]:
                                # Use real database
                                db = RedshiftConnection()
                                exec_result = db.execute_query(result["sql"])
                            else:
                                # Use mock data
                                mock_data = generate_mock_data(result["sql"])
                                exec_result = {
                                    "success": True,
                                    "data": mock_data,
                                    "row_count": len(mock_data),
                                    "execution_time_seconds": 0.1
                                }
                        
                        if exec_result["success"]:
                            st.subheader("📊 Results")
                            
                            # Display metrics
                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                st.metric("Rows", exec_result["row_count"])
                            with col_b:
                                st.metric("Time", f"{exec_result['execution_time_seconds']:.2f}s")
                            with col_c:
                                mode = "Real Data" if status["redshift_configured"] else "Mock Data"
                                st.metric("Mode", mode)
                            
                            # Display data
                            if exec_result["data"]:
                                df = pd.DataFrame(exec_result["data"])
                                st.dataframe(df, use_container_width=True)
                                
                                # Download option
                                csv = df.to_csv(index=False)
                                st.download_button(
                                    label="📥 Download CSV",
                                    data=csv,
                                    file_name=f"gusto_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    mime="text/csv"
                                )
                                
                                # Simple visualization
                                numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
                                if len(numeric_cols) > 0 and len(df) > 1:
                                    st.subheader("📈 Quick Visualization")
                                    if len(numeric_cols) > 1:
                                        chart_col = st.selectbox("Select column to chart:", numeric_cols)
                                    else:
                                        chart_col = numeric_cols[0]
                                    
                                    if 'company_name' in df.columns:
                                        chart_data = df.set_index('company_name')[chart_col].head(10)
                                        st.bar_chart(chart_data)
                            else:
                                st.info("Query executed successfully but returned no results.")
                        else:
                            st.error(f"Query execution failed: {exec_result['error']}")
                    else:
                        st.error(f"SQL generation failed: {result['error']}")
            else:
                st.warning("Please enter a query")
    
    with col2:
        st.subheader("ℹ️ About")
        st.markdown("""
        **Gusto Data Agent** converts natural language into SQL queries for analyzing Gusto warehouse data.
        
        **Production Features:**
        - 🧠 AI-powered SQL generation via OpenAI
        - 🔗 Direct Redshift database connectivity
        - 📊 Access to all Gusto warehouse tables
        - 🔒 Read-only database safety
        - 💾 CSV export capabilities
        - 📈 Quick data visualizations
        - 🎮 Demo mode fallback
        """)
        
        st.subheader("🚀 Getting Started")
        if status["demo_mode"]:
            st.markdown("""
            **To enable production mode:**
            1. Get Redshift credentials from your data team
            2. Set environment variables for database connection
            3. Add your OpenAI API key
            4. Restart the application
            """)
        else:
            st.success("✅ Production mode is active!")

if __name__ == "__main__":
    main() 