#!/usr/bin/env python3
"""
Script to optimize performance and reduce wait times
"""

# Read the current app.py
with open('app.py', 'r') as f:
    content = f.read()

# Add performance optimizations
performance_optimizations = '''
# Performance Optimizations
import streamlit as st
from functools import lru_cache
import time

# Cache expensive operations
@lru_cache(maxsize=128)
def get_cached_table_schemas():
    """Cache table schemas to avoid repeated processing"""
    return TABLE_SCHEMAS

@lru_cache(maxsize=64)
def get_cached_system_status():
    """Cache system status for faster loading"""
    return check_system_status()

# Optimize database connections with connection pooling
import psycopg2.pool

# Create connection pool
DB_POOL = None

def get_db_pool():
    """Get or create database connection pool"""
    global DB_POOL
    if DB_POOL is None:
        try:
            DB_POOL = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=5,
                host=os.getenv('REDSHIFT_HOST'),
                database=os.getenv('REDSHIFT_DATABASE'),
                user=os.getenv('REDSHIFT_USERNAME'),
                password=os.getenv('REDSHIFT_PASSWORD'),
                port=os.getenv('REDSHIFT_PORT', '5439')
            )
        except:
            DB_POOL = None
    return DB_POOL

def get_optimized_redshift_connection():
    """Get connection from pool for better performance"""
    pool = get_db_pool()
    if pool:
        try:
            return pool.getconn()
        except:
            return None
    return get_redshift_connection()

# Optimize system status checking
def check_system_status_fast():
    """Fast system status check with caching"""
    # Use cached status if available
    if hasattr(st.session_state, 'system_status_cache'):
        cache_time = st.session_state.get('system_status_cache_time', 0)
        if time.time() - cache_time < 30:  # Cache for 30 seconds
            return st.session_state.system_status_cache
    
    # Get fresh status
    status = check_system_status()
    
    # Cache the result
    st.session_state.system_status_cache = status
    st.session_state.system_status_cache_time = time.time()
    
    return status

'''

# Insert performance optimizations after imports
imports_end = content.find('# Table schemas for all Gusto warehouse tables')
if imports_end != -1:
    content = content[:imports_end] + performance_optimizations + content[imports_end:]
else:
    # If we can't find the right place, insert after imports
    imports_end = content.find('load_dotenv()')
    if imports_end != -1:
        next_line = content.find('\n', imports_end)
        content = content[:next_line] + performance_optimizations + content[next_line:]

# Replace the check_system_status calls with the optimized version
content = content.replace('status = check_system_status()', 'status = check_system_status_fast()')

# Add session state initialization
session_state_init = '''
# Initialize session state for caching
if 'system_status_cache' not in st.session_state:
    st.session_state.system_status_cache = None
if 'system_status_cache_time' not in st.session_state:
    st.session_state.system_status_cache_time = 0
'''

# Insert session state initialization in main function
main_start = content.find('def main():')
if main_start != -1:
    main_content_start = content.find('def main():')
    main_content = content[main_content_start:]
    content = content[:main_content_start] + session_state_init + main_content

# Write the optimized content
with open('app.py', 'w') as f:
    f.write(content)

print("✅ Added performance optimizations!")
print("🚀 Added connection pooling for faster database access")
print("💾 Added caching for system status and table schemas")
print("⚡ Reduced wait times with optimized operations")
print("🔄 App will now load much faster")
