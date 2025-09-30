#!/bin/bash
# Setup script for real data access

echo "🚀 Setting up Gusto Data Agent for Real Data Access"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the project directory."
    exit 1
fi

echo "📋 To access real data, you need to set up your database credentials:"
echo ""
echo "1. 🔐 Connect to your company VPN"
echo "2. 🔧 Set your database credentials:"
echo ""
echo "   export REDSHIFT_HOST=\"dataeng-prod.cqyxh8rl6vlx.us-west-2.redshift.amazonaws.com\""
echo "   export REDSHIFT_DATABASE=\"your_database_name\""
echo "   export REDSHIFT_USERNAME=\"your_username\""
echo "   export REDSHIFT_PASSWORD=\"your_password\""
echo "   export REDSHIFT_PORT=\"5439\""
echo "   export OPENAI_API_KEY=\"your_openai_api_key\""
echo ""
echo "3. 🚀 Start the app:"
echo "   ./start_production.sh"
echo ""
echo "💡 The app will now use real data instead of demo mode!"
echo ""

# Check if credentials are already set
if [ -n "$REDSHIFT_HOST" ] && [ -n "$REDSHIFT_USERNAME" ] && [ -n "$OPENAI_API_KEY" ]; then
    echo "✅ Database credentials detected!"
    echo "�� Starting app with real data access..."
    ./start_production.sh
else
    echo "⚠️  Please set your database credentials first"
    echo "💡 You can create a .env file with your credentials:"
    echo ""
    echo "   REDSHIFT_HOST=dataeng-prod.cqyxh8rl6vlx.us-west-2.redshift.amazonaws.com"
    echo "   REDSHIFT_DATABASE=your_database_name"
    echo "   REDSHIFT_USERNAME=your_username"
    echo "   REDSHIFT_PASSWORD=your_password"
    echo "   REDSHIFT_PORT=5439"
    echo "   OPENAI_API_KEY=your_openai_api_key"
    echo ""
    echo "Then run: source .env && ./start_production.sh"
fi
