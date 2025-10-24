# GAIA - Gusto AI Analyst (Production Version)

### Risk Tables
- `zenpayroll_production_no_pii.customer_risk_tiers` - Customer risk tier classifications (fraud, credit, combined)
- `zenpayroll_production_no_pii.onboarding_risk_scores` - Onboarding risk assessment scores
- `bi.risk_onboarding` - Risk and compliance data during onboarding
- `zenpayroll_production_no_pii.risk_onboarding_ai_agent_decisions` - AI-powered risk decisions during onboarding
- `zenpayroll_production_no_pii.cached_payroll_blockers` - Payroll processing blockers
- `bi.company_approval_details` - Company approval status and blockers
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

### ⚠️ No Value Hallucination
The AI is configured to **never make up or assume specific field values**. It will only use:
- Date ranges and time periods (e.g., `created_at >= '2024-01-01'`)
- Boolean flags (e.g., `is_active = true`, `ato_flag = false`)
- Specific values you provide (e.g., `filing_state = 'CA'` if you ask for California)
- Wildcards for pattern matching (e.g., `name LIKE '%search%'`)

**The AI will NOT:**
- Invent company IDs (e.g., `WHERE company_id = 12345`)
- Make up company names (e.g., `WHERE name = 'Acme Corp'`)
- Guess at specific values unless you provide them

This ensures all queries return real data based on actual patterns, not fictitious values.

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

### Risk Onboarding Agent Decisions
For queries about **agent decisions**, **AI decisions**, **risk analyst decisions**, or **trust analyst decisions** during onboarding, always use the `zenpayroll_production_no_pii.risk_onboarding_ai_agent_decisions` table.

**Key columns:**
- `decision` - Overall decision
- `status` - Decision status
- `trust_analyst_decision` - Trust analyst's decision
- `trust_analyst_confidence` - Confidence level for trust decision
- `risk_analyst_decision` - Risk analyst's decision
- `risk_analyst_confidence` - Confidence level for risk decision
- `version` - Model version
- `company_id` - Company identifier

Example:
```sql
-- Get recent AI agent decisions
SELECT company_id, decision, status, 
       trust_analyst_decision, trust_analyst_confidence,
       risk_analyst_decision, risk_analyst_confidence,
       created_at
FROM zenpayroll_production_no_pii.risk_onboarding_ai_agent_decisions
ORDER BY created_at DESC
LIMIT 100;

-- Get decisions with company details
SELECT d.company_id, c.name, d.decision, d.status,
       d.trust_analyst_decision, d.risk_analyst_decision
FROM zenpayroll_production_no_pii.risk_onboarding_ai_agent_decisions d
JOIN bi.companies c ON d.company_id = c.id
WHERE d.created_at >= CURRENT_DATE - INTERVAL '30 days'
LIMIT 100;
├── validated_queries.py   # Validated SQL examples for AI training

### Adding Validated Queries for AI Training

GAIA uses **few-shot learning** - it learns from validated query examples you provide. This dramatically improves accuracy by teaching the AI:
- Real field values (not hallucinated ones)
- Common join patterns
- Business logic specific to Gusto
- Proper filtering conditions

**To add new training examples:**

1. Open `validated_queries.py`
2. Add your validated query to the `VALIDATED_QUERIES` list:

```python
VALIDATED_QUERIES = [
    # ... existing queries ...
    
    # Your new query
    (
        "Natural language description",
        """SELECT your, validated, sql
FROM your_tables
WHERE your_conditions
LIMIT 100;"""
    ),
]
```

**Best practices:**
- Only add queries that have been tested and validated in production
- Include queries that demonstrate common patterns your team uses
- Cover different table combinations and join patterns
- Include examples with specific field values (risk_state values, tier formats, etc.)
- More examples = better AI performance

The AI will automatically learn from these patterns when generating new queries!