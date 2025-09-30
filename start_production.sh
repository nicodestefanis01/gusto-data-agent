#!/bin/bash
# Gusto Data Agent - Production Startup Script

echo "🚀 Starting Gusto Data Agent Production Server..."

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run from the project directory."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found. Please ensure credentials are configured."
    exit 1
fi

# Set production environment variables
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_SERVER_ENABLE_CORS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Start the application
echo "🌐 Starting server on http://0.0.0.0:8501"
echo "📊 Access the application at: http://localhost:8501"
echo "🔒 VPN connection required for external access"

python3 -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0
