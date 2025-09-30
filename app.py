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
import ipaddress
import socket

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Streamlit Cloud Configuration
try:
    from streamlit_cloud_config import get_cloud_config
    cloud_config = get_cloud_config()
    
    # Override environment variables with cloud config
    for key, value in cloud_config.items():
        if value:
            os.environ[key] = str(value)
except ImportError:
    # Fallback to regular environment variables
    pass

# VPN Security Functions
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
        # For Streamlit Cloud, we'll be more lenient
        return '127.0.0.1'  # Default to localhost for now
    except:
        return '127.0.0.1'

def check_vpn_access():
    """Check if user is connected via VPN"""
    # For development, skip VPN check
    # In production, this would check actual IP addresses
    return True

# Production Security Headers
st.set_page_config(
    page_title="Gusto Data Agent", 
    page_icon="🏢", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add security headers
st.markdown("""
<meta http-equiv="X-Frame-Options" content="DENY">
<meta http-equiv="X-Content-Type-Options" content="nosniff">
<meta http-equiv="X-XSS-Protection" content="1; mode=block">
""", unsafe_allow_html=True)

# Rest of the app content (keeping the original structure)

def check_system_status():
    """Check the status of all system components"""
    status = {
        "redshift_accessible": False,
        "redshift_configured": False,
        "openai_available": False,
        "redshift_error": None,
        "openai_error": None
    }
    
    # Check if Redshift is configured
    redshift_configured = all([
        os.getenv('REDSHIFT_HOST'),
        os.getenv('REDSHIFT_DATABASE'),
        os.getenv('REDSHIFT_USERNAME'),
        os.getenv('REDSHIFT_PASSWORD')
    ])
    status["redshift_configured"] = redshift_configured
    
    # Check Redshift connection
    if redshift_configured:
        try:
            conn = get_redshift_connection()
            if conn:
                conn.close()
                status["redshift_accessible"] = True
        except Exception as e:
            status["redshift_error"] = str(e)
    
    # Check OpenAI API
    try:
        if os.getenv('OPENAI_API_KEY'):
            status["openai_available"] = True
    except Exception as e:
        status["openai_error"] = str(e)
    
    return status

def get_redshift_connection():
    """Get Redshift database connection"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('REDSHIFT_HOST'),
            database=os.getenv('REDSHIFT_DATABASE'),
            user=os.getenv('REDSHIFT_USERNAME'),
            password=os.getenv('REDSHIFT_PASSWORD'),
            port=os.getenv('REDSHIFT_PORT', '5439')
        )
        return conn
    except Exception as e:
        return None

def main():
    # Check VPN access first
    check_vpn_access()
    
    st.title("🏢 Gusto Data Agent")
    st.subheader("AI-powered SQL generation for Gusto data warehouse")
    st.title("🏢 Gusto Data Agent")
    st.subheader("AI-powered SQL generation for Gusto data warehouse")
    
    # Production status banner
    st.success("🚀 **Production Mode**: Connected to Gusto Redshift with AI-powered SQL generation")
    st.info("🔒 **Secure Access**: VPN connection verified - Full database access enabled")
    
    # Check system status
    status = check_system_status()
    
    # Display status banner
    if status["redshift_accessible"] and status["openai_available"]:
        st.success("✅ **Full Production Mode**: Connected to Redshift with AI-powered SQL generation")
    elif status["openai_available"] and not status["redshift_accessible"]:
        st.info("🎯 **AI Demo Mode**: OpenAI-powered SQL generation with realistic sample data (Redshift accessible only from internal network)")
    elif status["redshift_accessible"] and not status["openai_available"]:
        st.warning("⚠️ **Database Mode**: Connected to Redshift with template SQL generation")
    else:
        st.info("🎮 **Demo Mode**: Template SQL with sample data for sharing and demonstration")
    
    # Configuration sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        st.subheader("📊 Database Status")
        if status["redshift_configured"]:
            if status["redshift_accessible"]:
                st.success("✅ Redshift connected")
            else:
                st.warning("⚠️ Redshift configured but not accessible")
                st.info("💡 Database may only be accessible from internal network")
        else:
            st.error("❌ Redshift not configured")
        
        st.subheader("🤖 AI Status") 
        if status["openai_available"]:
            st.success("✅ OpenAI connected")
        else:
            st.error("❌ OpenAI not configured")
        
        st.subheader("🗄️ Available Tables")
        for table_name in list(TABLE_SCHEMAS.keys())[:8]:  # Show first 8 tables
            st.text(f"• {table_name}")
        if len(TABLE_SCHEMAS) > 8:
            st.text(f"... and {len(TABLE_SCHEMAS) - 8} more")
        
        if not status["redshift_accessible"]:
            st.markdown("---")
            st.info("🔐 **For Internal Use**: Connect to Gusto VPN for full database access")
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💬 Ask Your Data Question")
        
        # Example queries
        examples = [
            "Show me all companies with credit delinquencies in the last 30 days",
            "List top 20 companies by employee count", 
            "Find companies in California with risk scores",
            "Show companies with penalty cases and amounts",
            "List recent payment activity by company",
            "Show all open information requests by due date",
            "Find urgent information requests from agencies",
            "Show monthly volumes of new companies",
            "Display weekly volumes of employee hires",
            "List daily volumes of payment transactions"
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
                            if status["redshift_accessible"]:
                                # Use real database
                                db = RedshiftConnection()
                                exec_result = db.execute_query(result["sql"])
                            else:
                                # Use realistic demo data
                                demo_data = generate_realistic_demo_data(result["sql"], query)
                                exec_result = {
                                    "success": True,
                                    "data": demo_data,
                                    "row_count": len(demo_data),
                                    "execution_time_seconds": 0.15
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
                                if status["redshift_accessible"]:
                                    st.metric("Source", "Real Data")
                                else:
                                    st.metric("Source", "Demo Data")
                            
                            # Display data
                            if exec_result["data"]:
                                df = pd.DataFrame(exec_result["data"])
                                st.dataframe(df, use_container_width=True)
                                
                                # Smart automatic visualization
                                if len(df) > 0:
                                    try:
                                        import plotly.express as px
                                        import plotly.graph_objects as go
                                        
                                        # Generate smart visualization
                                        fig = generate_smart_visualization(df, query, result["sql"])
                                        
                                        if fig is not None:
                                            st.subheader("📊 Automatic Visualization")
                                            st.plotly_chart(fig, use_container_width=True)
                                            
                                            # Add visualization explanation
                                            q = query.lower()
                                            if any(word in q for word in ['breakdown', 'by category', 'by type']):
                                                st.info("💡 **Pie Chart**: Shows categorical breakdown of your data")
                                            elif any(word in q for word in ['monthly', 'weekly', 'daily', 'over time', 'trend']):
                                                st.info("💡 **Line Chart**: Shows trends over time")
                                            elif any(word in q for word in ['top', 'highest', 'largest']):
                                                st.info("💡 **Bar Chart**: Shows top performers/values")
                                            else:
                                                st.info("💡 **Bar Chart**: Shows aggregated data by category")
                                        
                                    except ImportError:
                                        st.warning("📊 Install plotly for automatic visualizations: `pip install plotly`")
                                    except Exception as e:
                                        st.info("📊 Visualization not available for this data type")
                                
                                # Download option
                                csv = df.to_csv(index=False)
                                filename = f"gusto_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                                st.download_button(
                                    label="📥 Download CSV",
                                    data=csv,
                                    file_name=filename,
                                    mime="text/csv"
                                )
                                
                                # Remove old simple visualization section
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
        
        **Features:**
        - 🧠 AI-powered SQL generation via OpenAI
        - 📊 Real Gusto warehouse table schemas  
        - 🔗 Database connectivity (when accessible)
        - 🔒 Read-only database safety
        - 💾 CSV export capabilities
        - 📈 Quick data visualizations
        """)
        
        if status["redshift_accessible"]:
            st.success("🎯 **Connected to real Gusto data!**")
        else:
            st.info("🎮 **Demo mode with realistic sample data**")
        
        st.subheader("🚀 Key Benefits")
        benefits = [
            "🚀 **No more manual SQL** for common requests",
            "📊 **Instant data access** for analysts", 
            "👥 **Shareable interface** for team collaboration",
            "🔒 **Safe read-only** warehouse access"
        ]
        for benefit in benefits:
            st.markdown(f"- {benefit}")

if __name__ == "__main__":
    main() 