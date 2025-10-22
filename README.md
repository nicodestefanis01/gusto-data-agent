# GAIA - Gusto AI Analyst (Production Version)

🚀 **AI-powered SQL generation for Gusto data warehouse with real database connectivity**

This production version connects to actual Gusto Redshift data and uses OpenAI for intelligent SQL generation.

## 🎯 Features

- **🧠 AI-powered SQL generation** via OpenAI GPT-3.5-turbo
- **🔗 Direct Redshift connectivity** to Gusto data warehouse
- **📊 Access to all Gusto warehouse tables** (bi.companies, credit_delinquencies, etc.)
- **🔒 Read-only database safety** with connection validation
- **💾 CSV export capabilities** for analysis results
- **📈 Quick data visualizations** with interactive charts
- **🎮 Demo mode fallback** when credentials aren't available
- **⚡ Real-time status monitoring** for all connected systems

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Credentials

Run the interactive setup script:

```bash
python setup_production.py
```

This will guide you through setting up:
- **OpenAI API Key** for SQL generation
- **Redshift credentials** for database access

### 3. Run the Application

```bash
python -m streamlit run app.py
```

### 4. Test Configuration (Optional)

```bash
python setup_production.py test
```

## 🔐 Configuration

The app requires two sets of credentials:

### OpenAI API Key
```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### Redshift Database
```bash
REDSHIFT_HOST=your-cluster.redshift.amazonaws.com
REDSHIFT_DATABASE=warehouse
REDSHIFT_USERNAME=your_username
REDSHIFT_PASSWORD=your_password
REDSHIFT_PORT=5439
```

## 📊 Getting Redshift Credentials

Contact the **Gusto Data Team** to request:
- Read-only access to the main data warehouse
- Connection details for the Redshift cluster
- Mention you're building a SQL agent for ad-hoc data analysis

**What to ask for:**
1. Redshift cluster endpoint
2. Database name (likely `warehouse` or similar)
3. Read-only username and password
4. Port (usually 5439)

## 🎮 Operating Modes

The app automatically detects available credentials and operates in different modes:

### ✅ Production Mode
- **OpenAI**: ✅ Configured
- **Redshift**: ✅ Configured
- **Result**: Full AI-powered SQL generation with real Gusto data

### ⚠️ Partial Mode - AI Only
- **OpenAI**: ✅ Configured  
- **Redshift**: ❌ Not configured
- **Result**: AI-generated SQL with mock data for testing

### ⚠️ Partial Mode - Database Only
- **OpenAI**: ❌ Not configured
- **Redshift**: ✅ Configured  
- **Result**: Template SQL with real Gusto data

### 🎮 Demo Mode
- **OpenAI**: ❌ Not configured
- **Redshift**: ❌ Not configured
- **Result**: Template SQL with mock data (same as demo version)

## 🗄️ Available Tables

The agent understands these Gusto warehouse tables:

### Core Tables
- `bi.companies` - Company information and employee counts
- `bi.credit_delinquencies` - Credit delinquency records
- `bi.gusto_employees` - Employee data across all companies

### Financial Tables  
- `bi_reporting.gusto_payments_and_losses` - Payment processing data
- `bi.nacha_entries` - ACH/NACHA payment entries

### Compliance Tables
- `bi.penalty_cases` - Penalty cases and compliance issues
- `bi.penalty_groups` - Types and categories of penalties

### Risk Tables
- `zenpayroll_production_no_pii.customer_risk_tiers` - Customer risk tier classifications (fraud, credit, combined)
- `zenpayroll_production_no_pii.onboarding_risk_scores` - Onboarding risk assessment scores
- `bi.risk_onboarding` - Risk and compliance data during onboarding
- `zenpayroll_production_no_pii.risk_onboarding_ai_agent_decisions` - AI-powered risk decisions during onboarding
- `zenpayroll_production_no_pii.cached_payroll_blockers` - Payroll processing blockers
- `bi.company_approval_details` - Company approval status and blockers

### Activity Tables
- `zenpayroll_production_no.session_events` - User session events

## 💬 Example Queries

Try these natural language queries:

```
"Show me all companies with credit delinquencies in the last 30 days"
"List top 20 companies by employee count"
"Find companies in California with high risk scores"
"Show recent payment activity by company"
"List penalty cases from the last quarter"
"Show fraud loss transactions from last month"
"Show credit loss transactions with amounts over $1000"
"Show me ATO transactions from the last quarter"
"Find ATO-related payments with losses greater than $500"
"Show total payments for fiscal year 2024"
"What were the losses in the current fiscal year?"
"Show companies with high onboarding risk scores"
"List AI agent decisions for company approvals this month"
"Find companies with payroll blockers"
"Show approval details for pending companies"
"What are the risk states for companies created this week?"
```

## 📋 Important Data Rules

### Loss Transaction Types
When querying loss transactions in `bi_reporting.gusto_payments_and_losses` or `bi.credit_delinquencies`:

- **Fraud Loss Transactions**: Use `credit_loss_flag = false` (or `is_credit_loss = false` for credit_delinquencies table)
- **Credit Loss Transactions**: Use `credit_loss_flag = true` (or `is_credit_loss = true` for credit_delinquencies table)

Example:
```sql
-- Get fraud losses
SELECT * FROM bi_reporting.gusto_payments_and_losses 
WHERE credit_loss_flag = false 
LIMIT 100;

-- Get credit losses  
SELECT * FROM bi_reporting.gusto_payments_and_losses
WHERE credit_loss_flag = true
LIMIT 100;
```

### State Data Format (bi.companies)
The `filing_state` column in `bi.companies` always contains 2-letter state abbreviations (e.g., 'CA', 'NY', 'TX').

Example:
```sql
-- Get companies in California
SELECT * FROM bi.companies 
WHERE filing_state = 'CA' 
LIMIT 100;

-- Get companies in New York or Texas
SELECT * FROM bi.companies
WHERE filing_state IN ('NY', 'TX')
LIMIT 100;
```

### ATO (Account Takeover) Transactions
For all ATO-related payment information in `bi_reporting.gusto_payments_and_losses`, use the `ato_flag` column.

Example:
```sql
-- Get ATO transactions
SELECT * FROM bi_reporting.gusto_payments_and_losses 
WHERE ato_flag = true 
LIMIT 100;

-- Get non-ATO transactions
SELECT * FROM bi_reporting.gusto_payments_and_losses
WHERE ato_flag = false
LIMIT 100;

-- Get ATO transactions with losses
SELECT * FROM bi_reporting.gusto_payments_and_losses
WHERE ato_flag = true 
  AND net_loss_amount > 0
LIMIT 100;
```

### Fiscal Year at Gusto
Gusto's fiscal year starts in **May** (May 1st).

- **FY2024** = May 2023 through April 2024
- **FY2025** = May 2024 through April 2025
- **Current FY** = May of previous calendar year through April of current calendar year

Example:
```sql
-- Get payments for FY2024 (May 2023 - April 2024)
SELECT * FROM bi_reporting.gusto_payments_and_losses 
WHERE event_debit_date >= '2023-05-01' 
  AND event_debit_date < '2024-05-01'
LIMIT 100;

-- Get current fiscal year data (if today is in 2024)
SELECT * FROM bi_reporting.gusto_payments_and_losses
WHERE event_debit_date >= '2023-05-01'
  AND event_debit_date < '2024-05-01'
LIMIT 100;
```

### Fraud Company Identification
When querying fraud companies or fraud-related information, **only consider companies with specific risk states**.

**Fraud Risk States:** `2, 3, 7, 9, 12, 13, 14, 15, 17, 20, 22`

These risk states are available in:
- `bi.risk_onboarding` table
- `bi.company_approval_details` table

Example:
```sql
-- Get fraud companies
SELECT company_id, risk_state, risk_state_description
FROM bi.risk_onboarding
WHERE risk_state IN (2,3,7,9,12,13,14,15,17,20,22)
LIMIT 100;

-- Get fraud companies with approval details
SELECT company_id, risk_state, approval_status, auto_approval_blockers
FROM bi.company_approval_details
WHERE risk_state IN (2,3,7,9,12,13,14,15,17,20,22)
LIMIT 100;

-- Join with companies table for full details
SELECT c.id, c.name, ro.risk_state, ro.risk_state_description, ro.is_fraud
FROM bi.companies c
JOIN bi.risk_onboarding ro ON c.id = ro.company_id
WHERE ro.risk_state IN (2,3,7,9,12,13,14,15,17,20,22)
LIMIT 100;
```

## 🛠️ Development

### Project Structure
```
gusto-data-agent-production/
├── app.py                 # Main Streamlit application
├── setup_production.py    # Interactive configuration setup
├── requirements.txt       # Python dependencies
├── .env.template         # Environment variable template
├── .env                  # Your actual credentials (created by setup)
└── README.md            # This file
```

### Testing
```bash
# Test current configuration
python setup_production.py test

# Run app locally
python -m streamlit run app.py

# Check connection status in the sidebar
```

## 🚨 Security Notes

- Keep your `.env` file secure and never commit it to version control
- The app uses read-only database access for safety
- All queries include LIMIT clauses to prevent large result sets
- OpenAI API calls are logged for monitoring

## 🆘 Troubleshooting

### "Redshift connection failed"
1. Verify credentials with your data team
2. Check if your IP is whitelisted for Redshift access
3. Test connection with `python setup_production.py test`

### "OpenAI API error"
1. Verify your API key starts with `sk-`
2. Check if you have sufficient credits
3. Ensure the key has access to `gpt-3.5-turbo`

### "No results returned"
1. Check if the generated SQL is valid
2. Verify the table names exist in your schema
3. Try simpler queries first

## 📞 Support

For Gusto-specific issues:
- **Data access**: Contact the Gusto Data Team
- **Table schemas**: Check internal data documentation
- **Warehouse connectivity**: Work with your infrastructure team

For technical issues:
- Check the Streamlit sidebar for system status
- Run the test script: `python setup_production.py test`
- Review the console logs for detailed error messages

---

**🏢 Built for Gusto Data Team** | Production Version with Real Data Connectivity 