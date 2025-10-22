"""
Validated SQL Query Examples for GAIA Training

Add your validated, production-tested queries here. The AI will learn from these patterns
to generate better queries with accurate joins, field values, and business logic.

Format: (natural_language_query, sql_query)
"""

VALIDATED_QUERIES = [
    # Fraud Companies
    (
        "Show me fraud companies created in the last 30 days",
        """SELECT c.id, c.name, ro.risk_state, ro.risk_state_description, c.created_at
FROM bi.companies c
JOIN bi.risk_onboarding ro ON c.id = ro.company_id
WHERE ro.risk_state IN (2,3,7,9,12,13,14,15,17,20,22)
  AND c.created_at >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY c.created_at DESC
LIMIT 100;"""
    ),
    
    # Fraud Loss Transactions
    (
        "Get fraud loss transactions from last month",
        """SELECT company_id, event_id, event_debit_date, event_gross_amount, 
       recovered_amount, net_loss_amount
FROM bi_reporting.gusto_payments_and_losses
WHERE credit_loss_flag = false
  AND event_debit_date >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
  AND event_debit_date < DATE_TRUNC('month', CURRENT_DATE)
ORDER BY event_debit_date DESC
LIMIT 100;"""
    ),
    
    # Risk Tiers by State
    (
        "Show companies with high risk tiers in California",
        """SELECT c.id, c.name, c.filing_state, t.combined_risk_tier, t.fraud_risk_tier
FROM bi.companies c
JOIN zenpayroll_production_no_pii.customer_risk_tiers t ON t.company_id = c.id
WHERE c.filing_state = 'CA'
  AND t.combined_risk_tier IN ('Tier C', 'Tier D', 'Tier E')
ORDER BY t.fraud_risk_tier DESC
LIMIT 100;"""
    ),
    
    # AI Agent Decisions
    (
        "Get recent AI agent decisions with company details",
        """SELECT d.company_id, c.name, d.decision, d.status,
       d.trust_analyst_decision, d.trust_analyst_confidence,
       d.risk_analyst_decision, d.risk_analyst_confidence,
       d.created_at
FROM zenpayroll_production_no_pii.risk_onboarding_ai_agent_decisions d
JOIN bi.companies c ON d.company_id = c.id
WHERE d.created_at >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY d.created_at DESC
LIMIT 100;"""
    ),
    
    # ATO Transactions
    (
        "Show ATO transactions with losses greater than $1000",
        """SELECT company_id, event_id, event_debit_date, event_gross_amount,
       recovered_amount, net_loss_amount, ato_flag
FROM bi_reporting.gusto_payments_and_losses
WHERE ato_flag = true
  AND net_loss_amount > 1000
  AND failed_payment_flag = true
ORDER BY net_loss_amount DESC
LIMIT 100;"""
    ),
    
    # Add more validated queries here...
    # Format: (question, sql_query)
]

def get_example_queries_text():
    """Convert validated queries into formatted text for AI prompt"""
    examples_text = "EXAMPLE VALIDATED QUERIES (learn from these patterns):\n\n"
    
    for idx, (question, sql) in enumerate(VALIDATED_QUERIES, 1):
        examples_text += f"{idx}. Query: \"{question}\"\n"
        examples_text += f"   SQL: {sql}\n\n"
    
    examples_text += "Learn from these patterns: date ranges, proper joins, boolean flags, risk_state values, tier formats.\n"
    
    return examples_text

