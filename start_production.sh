#!/bin/bash
# Production startup script for Gusto Data Agent

echo "🚀 Starting Gusto Data Agent in Production Mode..."

# Set production environment variables
export PRODUCTION_MODE=true
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Start the application
python3 -m streamlit run app.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false

echo "✅ Production server started on port 8501"
