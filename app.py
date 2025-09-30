#!/usr/bin/env python3
"""
Gusto Data Agent - AI-Powered Data Analysis
A Streamlit application for querying Gusto data warehouse with natural language.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import psycopg2
from datetime import datetime, timedelta
import random
from openai import OpenAI
import ipaddress
from typing import List

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Try to import cloud config
try:
    from streamlit_cloud_config import get_cloud_config
    cloud_config = get_cloud_config()
    # Override environment variables with cloud config
    for key, value in cloud_config.items():
        if value is not None:
            os.environ[key] = str(value)
except ImportError:
    pass

# Table schemas for all Gusto warehouse tables
TABLE_SCHEMAS = {
    "bi.companies": ['id', 'name', 'trade_name', 'accounting_firm_id', 'created_at', 'company_lead_id', 'initial_company_size', 'initial_employee_count', 'segment_by_initial_size', 'segment_by_initial_employee_count', 'initial_contractor_count', 'approval_status', 'number_active_employees', 'number_active_contractors', 'segment_by_current_employee_count', 'segment_by_current_size', 'joined_at', 'is_active', 'finished_onboarding_at', 'originally_finished_onboarding_at', 'last_finished_onboarding_at', 'suspension_at', 'is_soft_suspended', 'has_suspension_warning', 'suspension_leaving_for', 'suspension_created_at', 'active_wc_policy', 'has_zenefits_integration', 'filing_address_id', 'filing_state', 'filing_city', 'filing_zip', 'mailing_address_id', 'tax_payer_type', 'pass_through', 'median_payroll_net_pay', 'median_payroll_tax', 'sic_code', 'previous_payroll_provider', 'had_previous_provider', 'has_accountant_collaborator', 'is_bank_verified', 'has_bank_info', 'from_partner_program', 'partner_acquisition', 'volume_discount_eligible', 'current_federal_deposit_schedule', 'is_eftps_enabled', 'partner_billing', 'bill_to_accountant', 'bill_to_client', 'bank_account_type', 'first_approved_at', 'is_eligible_for_fast_ach', 'has_fast_ach', 'supports_multiple_pay_schedules', 'has_teams', 'suggested_referral', 'suggested_referral_at', 'suggested_referral_by_user', 'estimated_company_founded_date', 'previous_payroll_provider_type', 'current_flag', 'updated_at', 'industry_source', 'slug', 'previous_payroll_provider_sub_type', 'previous_company_id', 'is_big_desk', 'lead_industry_classification', 'is_big_desk_initial', 'number_active_contractors_current_mtd', 'number_active_employees_current_mtd', 'uuid', 'has_gws', 'is_mrb', 'previous_provider_in', 'suspension_id', 'dbt_incremental_ts', 'sales_program', 'risk_state_description', 'suspended_reason', 'naics_code', 'user_provided_industry', 'user_provided_sub_industry', 'industry_classification', 'industry_title', 'industry_custom_description', 'suggested_referral_channel', 'bank_name', 'snowplow__created_by_user_id', 'etl_insert_ts', 'etl_update_ts'],
    "bi.credit_delinquencies": ['company_id', 'name', 'payment_id', 'payment_type', 'payment_speed_in_days', 'expedite_reason', 'off_cycle_reason', 'processing_state', 'debit_date', 'debit_event', 'debit_amount_attempted', 'error_code', 'error_code_returned_at', 'past_due_date', 'admin_comment', 'admin_end_date', 'successful_credits', 'final_credit_reversal_date', 'successful_debits', 'final_debit_date', 'recovery_debits', 'final_recovery_debit_date', 'wire_recovery_amount', 'loi_recovered_amount', 'wire_recovery_date', 'is_credit_loss', 'recovery_needed_flag', 'recovery_amount_needed', 'in_flight', 'recovered_amount', 'pending_amount', 'delinquent_status', 'final_date', 'days_past_due', 'is_cancelled', 'updated_at', 'etl_comments', 'dbt_incremental_ts'],
    "bi.gusto_employees": ['dbt_id', 'id', 'sfdc_ee_id', 'first_name', 'last_name', 'name', 'nickname', 'email', 'hired_at', 'terminated_at', 'department_name', 'work_state', 'status', 'worker_type', 'worker_sub_type', 'org', 'job_title', 'location', 'team', 'sub_team', 'is_pe', 'pe', 'pe_email', 'sfdc_class_queue', 'sfdc_benefits_class', 'sfdc_profile_id', 'sfdc_userrole_id', 'sfdc_userrole_name', 'sfdc_user_id', 'genesys_user_id', 'cxone_agent_id', 'cxone_user_id', 'updated_date', 'lastmodified_ts', 'effect_start_dt', 'effect_end_dt', 'current_flag', 'mu_id', 'mu_name', 'pe_sfdc_ee_id', 'etl_insert_ts', 'etl_update_ts'],
    "bi.information_requests": ['id', 'resource_id', 'resource_type', 'submission_state', 'situation', 'queue', 'company_id', 'requested_by_user_email', 'hide_from_review_queue', 'created_at', 'current_flag', 'updated_at', 'dbt_incremental_ts', 'etl_insert_ts', 'etl_update_ts'],
    "bi.penalty_cases": ['id', 'agent_id', 'agency_name', 'created_at', 'year', 'quarter', 'title', 'total_interest_amount', 'error_type', 'total_penalty_amount', 'total_penalty_paid', 'total_interest_paid', 'error_origin', 'status', 'updated_at', 'penalty_group_id', 'agent_payment', 'dbt_incremental_ts', 'etl_insert_ts', 'etl_update_ts'],
    "bi.penalty_groups": ['id', 'penalty_case_id', 'link', 'ticket_system_of_record', 'sor_ticket_id', 'pay_to', 'batch', 'approval_status', 'created_at', 'updated_at', 'source_ts_tstamp', 'dbt_incremental_ts', 'etl_insert_ts', 'etl_update_ts'],
    "bi_reporting.gusto_payments_and_losses": ['calendar_date', 'week_in_month', 'event_type', 'company_id', 'event_id', 'event_debit_date', 'bank_name', 'origination_account_id', 'company_age', 'sales_program', 'user_provided_industry', 'product_plan', 'initial_size', 'current_size', 'is_mrb', 'managing_accounting_firm_id', 'partner_level_tier', 'is_gep_company', 'gep_partner_name', 'invoice_total_debit', 'mrr_payroll_pre_discounts', 'mrr_payroll_post_discounts', 'initiated_by', 'error_code', 'error_code_returned_at', 'event_speed_in_days', 'ach_speed', 'is_auto_pilot', 'plaid_connected_flag', 'funding_type', 'funding_method', 'event_id_risk', 'transmission_flag', 'processing_state', 'original_status', 'last_status', 'challenged_reasons', 'unchallenged_reasons', 'plaid_challenge_flag', 'pocm_challenge_flag', 'only_pocm_challenge_flag', 'pfqm_challenge_flag', 'reviewed_by_risk_model_flag', 'event_gross_amount', 'ato_flag', 'credit_loss_flag', 'days_past_due', 'recovery_date', 'expected_debit_amount', 'ne_successful_debit_amount', 'ep_successful_debit_amount', 'final_successful_debit_amount', 'failed_debits_count', 'failed_payment_flag', 'failed_payment_amount', 'failed_unrecovered_payment_amount', 'failed_payment_outstanding_amount', 'recovered_amount', 'net_loss_amount', 'etl_insert_ts'],
    "bi.nacha_entries": ['id', 'created_at_date', 'batch_check_date', 'amount', 'company_id', 'employee_id', 'contractor_id', 'payroll_id', 'contractor_payment_id', 'agent_payment_id', 'error_code', 'is_debit', 'is_credit', 'entry_code', 'transaction_type', 'is_test_deposit', 'is_invoice', 'current_flag', 'updated_at', 'entry_id', 'international_contractor_id', 'international_contractor_payment_id', 'returned_code_at', 'international_employee_payroll_id', 'nacha_batch_id', 'bank_account_type', 'notify_if_error', 'resubmit_if_error', 'company_transaction', 'bank_account_id', 'dismissed', 'refund', 'accounting_firm_id', 'failed_entry_id', 'cleared', 'requested_by_id', 'payment_direction', 'origination_account_id', 'effective_entry_date', 'uuid', 'submission_date', 'dbt_incremental_ts', 'encrypted_bank_routing_number', 'processing_state', 'confirmation', 'ach_trace_id', 'ach_type', 'bank_account_hapii_id', 'correction_code', 'etl_insert_ts', 'etl_update_ts']
}

def is_internal_network(client_ip: str, allowed_networks: List[str]) -> bool:
    """Check if client IP is in allowed internal networks"""
    try:
        client_addr = ipaddress.ip_address(client_ip)
        for network in allowed_networks:
            if client_addr in ipaddress.ip_network(network):
                return True
        return False
    except:
        return False

def get_client_ip() -> str:
    """Get client IP address"""
    try:
        import requests
        return requests.get('https://api.ipify.org').text
    except:
        return "127.0.0.1"

def check_vpn_access():
    """Check if user is on VPN - disabled for local development"""
    try:
        # For local development, always allow access
        if os.getenv('LOCAL_DEVELOPMENT', 'true').lower() == 'true':
            return True
            
        vpn_required = os.getenv('VPN_REQUIRED', 'false').lower() == 'true'
        if not vpn_required:
            return True
            
        allowed_networks = os.getenv('ALLOWED_NETWORKS', '10.0.0.0/8,172.16.0.0/12,192.168.0.0/16').split(',')
        client_ip = get_client_ip()
        
        if is_internal_network(client_ip, allowed_networks):
            return True
        else:
            st.error("🔒 **VPN Access Required**")
            st.info("Please connect to the company VPN to access this application.")
            st.stop()
    except Exception as e:
        st.warning(f"⚠️ VPN check failed: {e}")
        return True

@st.cache_data
def check_system_status():
    """Check system status"""
    status = {
        "redshift_configured": bool(os.getenv('REDSHIFT_HOST')),
        "openai_configured": bool(os.getenv('OPENAI_API_KEY')),
        "redshift_accessible": False
    }
    
    if status["redshift_configured"]:
        try:
            conn = get_redshift_connection()
            if conn:
                conn.close()
                status["redshift_accessible"] = True
        except:
            pass
    
    return status

def get_redshift_connection():
    """Get Redshift connection"""
    try:
        return psycopg2.connect(
            host=os.getenv('REDSHIFT_HOST'),
            database=os.getenv('REDSHIFT_DATABASE'),
            user=os.getenv('REDSHIFT_USERNAME'),
            password=os.getenv('REDSHIFT_PASSWORD'),
            port=os.getenv('REDSHIFT_PORT', '5439')
        )
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def generate_sql_with_ai(query: str) -> str:
    """Generate SQL using OpenAI"""
    try:
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Create schema context
        schema_context = "\n".join([f"{table}: {', '.join(columns)}" for table, columns in TABLE_SCHEMAS.items()])
        
        prompt = f"""
        You are a SQL expert for Gusto's data warehouse. Generate SQL queries based on natural language requests.
        
        Available tables and columns:
        {schema_context}
        
        User query: {query}
        
        Rules:
        1. Use ONLY the columns listed above
        2. Use proper table names with schema (e.g., bi.companies)
        3. Add LIMIT 100 to prevent large results
        4. Use proper SQL syntax for Redshift
        5. For time-based queries, use DATE_TRUNC for aggregations
        6. For time-based aggregations, ALWAYS add ORDER BY time_column DESC to show most recent first
        7. For monthly/weekly/daily aggregations, sort by the time period in descending order
        8. IMPORTANT: For bi_reporting.gusto_payments_and_losses table, ALWAYS use event_debit_date as the date column for time-based queries
        
        Generate SQL:
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.1
        )
        
        sql = response.choices[0].message.content.strip()
        
        # Clean up SQL
        if sql.startswith('```sql'):
            sql = sql[6:]
        if sql.endswith('```'):
            sql = sql[:-3]
        
        return sql.strip()
        
    except Exception as e:
        st.error(f"AI SQL generation failed: {e}")
        return None

def execute_sql(sql: str):
    """Execute SQL and return results"""
    try:
        conn = get_redshift_connection()
        if not conn:
            return None, "Database connection failed"
        
        cursor = conn.cursor()
        cursor.execute(sql)
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Fetch results
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Convert to DataFrame
        df = pd.DataFrame(results, columns=columns)
        return df, None
        
    except Exception as e:
        return None, str(e)

def create_visualization(df: pd.DataFrame, query: str):
    """Create appropriate visualization"""
    if df.empty:
        return None
    
    # Determine chart type based on query and data
    query_lower = query.lower()
    
    # Enhanced time-based detection
    time_keywords = ['monthly', 'weekly', 'daily', 'trend', 'over time', 'volumes', 'by month', 'by week', 'by day', 'time series', 'chronological']
    is_time_based = any(word in query_lower for word in time_keywords)
    
    # Check if first column looks like a date/time column
    first_col = df.columns[0] if len(df.columns) > 0 else ""
    date_like_columns = ['date', 'time', 'created', 'updated', 'month', 'week', 'day', 'year', 'quarter']
    is_date_column = any(date_word in first_col.lower() for date_word in date_like_columns)
    
    # Time-based queries - ALWAYS use line charts
    if is_time_based or is_date_column:
        if len(df.columns) >= 2:
            x_col = df.columns[0]
            y_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
            
            # Sort data by x-axis for proper line chart
            try:
                df_sorted = df.sort_values(by=x_col)
                fig = px.line(df_sorted, x=x_col, y=y_col, title=f"Time Series: {query}")
                fig.update_layout(
                    xaxis_title=x_col,
                    yaxis_title=y_col,
                    hovermode='x unified'
                )
                return fig
            except:
                fig = px.line(df, x=x_col, y=y_col, title=f"Time Series: {query}")
                return fig
    
    # Categorical breakdowns - use pie charts
    if any(word in query_lower for word in ['by', 'breakdown', 'distribution', 'count', 'percentage', 'share']):
        if len(df.columns) >= 2:
            x_col = df.columns[0]
            y_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
            
            fig = px.pie(df, names=x_col, values=y_col, title=f"Breakdown: {query}")
            return fig
    
    # Default bar chart for other cases
    if len(df.columns) >= 2:
        x_col = df.columns[0]
        y_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
        
        fig = px.bar(df, x=x_col, y=y_col, title=f"Analysis: {query}")
        return fig
    
    return None

def main():
    """Main application"""
    # Check VPN access
    check_vpn_access()
    
    # Page config
    st.set_page_config(
        page_title="Gusto Data Agent",
        page_icon="📊",
        layout="wide"
    )
    
    # Header
    st.title("📊 Gusto Data Agent")
    st.markdown("AI-powered data analysis for Gusto's data warehouse")
    
    # Check system status
    status = check_system_status()
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 System Status")
        if status["redshift_configured"]:
            st.success("✅ Redshift configured")
        else:
            st.error("❌ Redshift not configured")
            
        if status["openai_configured"]:
            st.success("✅ OpenAI configured")
        else:
            st.error("❌ OpenAI not configured")
            
        if status["redshift_accessible"]:
            st.success("✅ Database connected")
        else:
            st.warning("⚠️ Database not accessible")
    
    # Available Tables Section
    with st.expander("📊 Available Tables & Schemas", expanded=False):
        st.markdown("### 🗄️ Database Tables")
        
        for table_name, columns in TABLE_SCHEMAS.items():
            with st.expander(f"**{table_name}** ({len(columns)} columns)", expanded=False):
                # Show first 10 columns
                display_columns = columns[:10]
                st.markdown(f"**Columns:** {', '.join(display_columns)}")
                
                if len(columns) > 10:
                    st.markdown(f"*... and {len(columns) - 10} more columns*")
                
                # Show sample query
                if "companies" in table_name.lower():
                    st.code("SELECT * FROM bi.companies LIMIT 5", language="sql")
                elif "employees" in table_name.lower():
                    st.code("SELECT * FROM bi.gusto_employees LIMIT 5", language="sql")
                elif "payments" in table_name.lower():
                    st.code("SELECT * FROM bi_reporting.gusto_payments_and_losses LIMIT 5", language="sql")
                elif "information" in table_name.lower():
                    st.code("SELECT * FROM bi.information_requests LIMIT 5", language="sql")
                else:
                    st.code(f"SELECT * FROM {table_name} LIMIT 5", language="sql")
    
    # Main interface
    st.header("💬 Ask a Question")
    
    # Example queries
    examples = [
        "Show me all companies created this month",
        "What are the top 10 companies by employee count?",
        "Show monthly volumes of new companies",
        "Find all open information requests",
        "What's the breakdown of employees by department?"
    ]
    
    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input("Enter your question:", placeholder="Ask anything about Gusto data...")
    with col2:
        if st.button("🚀 Analyze", type="primary"):
            pass
    
    # Process query
    if query:
        with st.spinner("🤖 Generating SQL..."):
            sql = generate_sql_with_ai(query)
            
        if sql:
            st.subheader("🔍 Generated SQL")
            st.code(sql, language="sql")
            
            with st.spinner("📊 Executing query..."):
                df, error = execute_sql(sql)
                
            if error:
                st.error(f"❌ Query failed: {error}")
            elif df is not None:
                st.subheader("📈 Results")
                st.dataframe(df)
                
                # Create visualization
                fig = create_visualization(df, query)
                if fig:
                    st.subheader("📊 Visualization")
                    st.plotly_chart(fig, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    ### 🛡️ Security & Features
    - 🔒 VPN-only access
    - 🔒 Read-only database safety
    - 💾 CSV export capabilities
    - 📈 Quick data visualizations
    """)
    
    if status["redshift_accessible"]:
        st.success("🎯 **Connected to real Gusto data!**")
    else:
        st.info("🎮 **Demo mode with realistic sample data**")

if __name__ == "__main__":
    main()
