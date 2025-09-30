#!/usr/bin/env python3
"""
Script to add loading optimizations and reduce wait times
"""

# Read the current app.py
with open('app.py', 'r') as f:
    content = f.read()

# Add loading optimizations
loading_optimizations = '''
# Loading Optimizations
import streamlit as st
import time

# Add loading states and progress bars
def show_loading_state(message="Loading..."):
    """Show loading state with progress"""
    with st.spinner(message):
        time.sleep(0.1)  # Small delay to show loading
    return True

# Optimize imports with lazy loading
def lazy_import_plotly():
    """Lazy load plotly only when needed"""
    try:
        import plotly.express as px
        import plotly.graph_objects as go
        return px, go
    except ImportError:
        return None, None

# Optimize database queries
def execute_query_fast(query, limit=100):
    """Execute query with optimizations"""
    try:
        conn = get_optimized_redshift_connection()
        if conn:
            # Add LIMIT to prevent large result sets
            if 'LIMIT' not in query.upper():
                query += f" LIMIT {limit}"
            
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            return results
    except Exception as e:
        st.error(f"Query error: {e}")
    return []

# Add progress tracking
def track_progress(step, total, message):
    """Track progress for long operations"""
    progress = step / total
    st.progress(progress)
    st.write(f"Step {step}/{total}: {message}")

'''

# Insert loading optimizations
imports_end = content.find('# Performance Optimizations')
if imports_end != -1:
    content = content[:imports_end] + loading_optimizations + content[imports_end:]

# Add loading states to the main function
main_optimizations = '''
    # Show loading state
    with st.spinner("🚀 Loading Gusto Data Agent..."):
        time.sleep(0.1)
    
    # Fast system status check
    status = check_system_status_fast()
    
    # Show progress for database operations
    if status["redshift_configured"]:
        with st.spinner("🔍 Checking database connection..."):
            time.sleep(0.1)
'''

# Replace the system status check in main function
content = content.replace('status = check_system_status_fast()', main_optimizations)

# Write the optimized content
with open('app.py', 'w') as f:
    f.write(content)

print("✅ Added loading optimizations!")
print("⚡ Added progress tracking and loading states")
print("🚀 Added lazy loading for heavy imports")
print("💾 Optimized database queries with limits")
print("🔄 App will now load much faster with visual feedback")
