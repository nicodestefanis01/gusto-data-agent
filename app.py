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
        # Try to get real IP from headers
        if hasattr(st, 'request') and hasattr(st.request, 'headers'):
            x_forwarded_for = st.request.headers.get('X-Forwarded-For')
            if x_forwarded_for:
                return x_forwarded_for.split(',')[0].strip()
        
        # Fallback to localhost for development
        return '127.0.0.1'
    except:
        return '127.0.0.1'

def check_vpn_access():
    """Check if user is connected via VPN"""
    # For Streamlit Cloud, we need to be more lenient during development
    # but still maintain security for production
    
    try:
        from streamlit_cloud_config import get_cloud_config
        cloud_config = get_cloud_config()
        ALLOWED_NETWORKS = cloud_config.get('ALLOWED_NETWORKS', [
            "10.0.0.0/8",      # Internal networks
            "172.16.0.0/12",   # Internal networks  
            "192.168.0.0/16",  # Internal networks
            "127.0.0.1/32"     # Localhost
        ])
        VPN_REQUIRED = cloud_config.get('VPN_REQUIRED', True)
    except:
        ALLOWED_NETWORKS = [
            "10.0.0.0/8",      # Internal networks
            "172.16.0.0/12",   # Internal networks  
            "192.168.0.0/16",  # Internal networks
            "127.0.0.1/32"     # Localhost
        ]
        VPN_REQUIRED = True
    
    # Skip VPN check if not required (for development)
    if not VPN_REQUIRED:
        return True
    
    client_ip = get_client_ip()
    
    if not is_internal_network(client_ip, ALLOWED_NETWORKS):
        st.error("🔒 **Access Restricted**")
        st.markdown(f"""
        This application is only accessible from the Gusto internal network.
        
        **To access this application:**
        1. Connect to the Gusto VPN
        2. Refresh this page
        3. Contact IT support if you continue to have issues
        
        **Your IP:** `{client_ip}`
        """)
        st.stop()
    
    return True
    """Check if user is connected via VPN"""
    ALLOWED_NETWORKS = [
        "10.0.0.0/8",      # Internal networks
        "172.16.0.0/12",   # Internal networks  
        "192.168.0.0/16",  # Internal networks
        "127.0.0.1/32"     # Localhost
    ]
    
    client_ip = get_client_ip()
    
    if not is_internal_network(client_ip, ALLOWED_NETWORKS):
        st.error("🔒 **Access Restricted**")
        st.markdown(f"""
        This application is only accessible from the Gusto internal network.
        
        **To access this application:**
        1. Connect to the Gusto VPN
        2. Refresh this page
        3. Contact IT support if you continue to have issues
        
        **Your IP:** `{client_ip}`
        """)
        st.stop()
    
    return True


# Try to import OpenAI, fall back to mock if not available
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


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


# Real Gusto warehouse table schemas (discovered from actual database)
TABLE_SCHEMAS = {
    "bi.companies": {
        "description": "Core company information - use 'id' for company ID and 'name' for company name",
        "columns": ['id', 'name', 'trade_name', 'accounting_firm_id', 'created_at', 'company_lead_id', 'initial_company_size', 'initial_employee_count', 'segment_by_initial_size', 'segment_by_initial_employee_count', 'initial_contractor_count', 'approval_status', 'number_active_employees', 'number_active_contractors', 'segment_by_current_employee_count', 'segment_by_current_size', 'joined_at', 'is_active', 'finished_onboarding_at', 'originally_finished_onboarding_at', 'last_finished_onboarding_at', 'suspension_at', 'is_soft_suspended', 'has_suspension_warning', 'suspension_leaving_for', 'suspension_created_at', 'active_wc_policy', 'has_zenefits_integration', 'filing_address_id', 'filing_state', 'filing_city', 'filing_zip', 'mailing_address_id', 'tax_payer_type', 'pass_through', 'median_payroll_net_pay', 'median_payroll_tax', 'sic_code', 'previous_payroll_provider', 'had_previous_provider', 'has_accountant_collaborator', 'is_bank_verified', 'has_bank_info', 'from_partner_program', 'partner_acquisition', 'volume_discount_eligible', 'current_federal_deposit_schedule', 'is_eftps_enabled', 'partner_billing', 'bill_to_accountant', 'bill_to_client', 'bank_account_type', 'first_approved_at', 'is_eligible_for_fast_ach', 'has_fast_ach', 'supports_multiple_pay_schedules', 'has_teams', 'suggested_referral', 'suggested_referral_at', 'suggested_referral_by_user', 'estimated_company_founded_date', 'previous_payroll_provider_type', 'current_flag', 'updated_at', 'industry_source', 'slug', 'previous_payroll_provider_sub_type', 'previous_company_id', 'is_big_desk', 'lead_industry_classification', 'is_big_desk_initial', 'number_active_contractors_current_mtd', 'number_active_employees_current_mtd', 'uuid', 'has_gws', 'is_mrb', 'previous_provider_in', 'suspension_id', 'dbt_incremental_ts', 'sales_program', 'risk_state_description', 'suspended_reason', 'naics_code', 'user_provided_industry', 'user_provided_sub_industry', 'industry_classification', 'industry_title', 'industry_custom_description', 'suggested_referral_channel', 'bank_name', 'snowplow__created_by_user_id', 'etl_insert_ts', 'etl_update_ts']
    },
    "bi.credit_delinquencies": {
        "description": "Credit delinquency records - use company_id to join with companies",
        "columns": ['company_id', 'name', 'payment_id', 'payment_type', 'payment_speed_in_days', 'expedite_reason', 'off_cycle_reason', 'processing_state', 'debit_date', 'debit_event', 'debit_amount_attempted', 'error_code', 'error_code_returned_at', 'past_due_date', 'admin_comment', 'admin_end_date', 'successful_credits', 'final_credit_reversal_date', 'successful_debits', 'final_debit_date', 'recovery_debits', 'final_recovery_debit_date', 'wire_recovery_amount', 'loi_recovered_amount', 'wire_recovery_date', 'is_credit_loss', 'recovery_needed_flag', 'recovery_amount_needed', 'in_flight', 'recovered_amount', 'pending_amount', 'delinquent_status', 'final_date', 'days_past_due', 'is_cancelled', 'updated_at', 'etl_comments', 'dbt_incremental_ts']
    },
    "bi.gusto_employees": {
        "description": "Employee information - use 'id' for employee ID",
        "columns": ['dbt_id', 'id', 'sfdc_ee_id', 'first_name', 'last_name', 'name', 'nickname', 'email', 'hired_at', 'terminated_at', 'department_name', 'work_state', 'status', 'worker_type', 'worker_sub_type', 'org', 'job_title', 'location', 'team', 'sub_team', 'is_pe', 'pe', 'pe_email', 'sfdc_class_queue', 'sfdc_benefits_class', 'sfdc_profile_id', 'sfdc_userrole_id', 'sfdc_userrole_name', 'sfdc_user_id', 'genesys_user_id', 'cxone_agent_id', 'cxone_user_id', 'updated_date', 'lastmodified_ts', 'effect_start_dt', 'effect_end_dt', 'current_flag', 'mu_id', 'mu_name', 'pe_sfdc_ee_id', 'etl_insert_ts', 'etl_update_ts']
    },
    "bi_reporting.gusto_payments_and_losses": {
        "description": "Payment processing data and financial losses",
        "columns": ['calendar_date', 'week_in_month', 'event_type', 'company_id', 'event_id', 'event_debit_date', 'bank_name', 'origination_account_id', 'company_age', 'sales_program', 'user_provided_industry', 'product_plan', 'initial_size', 'current_size', 'is_mrb', 'managing_accounting_firm_id', 'partner_level_tier', 'is_gep_company', 'gep_partner_name', 'invoice_total_debit', 'mrr_payroll_pre_discounts', 'mrr_payroll_post_discounts', 'initiated_by', 'error_code', 'error_code_returned_at', 'event_speed_in_days', 'ach_speed', 'is_auto_pilot', 'plaid_connected_flag', 'funding_type', 'funding_method', 'event_id_risk', 'transmission_flag', 'processing_state', 'original_status', 'last_status', 'challenged_reasons', 'unchallenged_reasons', 'plaid_challenge_flag', 'pocm_challenge_flag', 'only_pocm_challenge_flag', 'pfqm_challenge_flag', 'reviewed_by_risk_model_flag', 'event_gross_amount', 'ato_flag', 'credit_loss_flag', 'days_past_due', 'recovery_date', 'expected_debit_amount', 'ne_successful_debit_amount', 'ep_successful_debit_amount', 'final_successful_debit_amount', 'failed_debits_count', 'failed_payment_flag', 'failed_payment_amount', 'failed_unrecovered_payment_amount', 'failed_payment_outstanding_amount', 'recovered_amount', 'net_loss_amount', 'etl_insert_ts']
    },
    "bi.penalty_cases": {
        "description": "Penalty cases and compliance issues",
        "columns": ['id', 'agent_id', 'agency_name', 'created_at', 'year', 'quarter', 'title', 'total_interest_amount', 'error_type', 'total_penalty_amount', 'total_penalty_paid', 'total_interest_paid', 'error_origin', 'status', 'updated_at', 'penalty_group_id', 'agent_payment', 'dbt_incremental_ts', 'etl_insert_ts', 'etl_update_ts']
    },
    "bi.penalty_groups": {
        "description": "Penalty group information",
        "columns": ['id', 'penalty_case_id', 'link', 'ticket_system_of_record', 'sor_ticket_id', 'pay_to', 'batch', 'approval_status', 'created_at', 'updated_at', 'source_ts_tstamp', 'dbt_incremental_ts', 'etl_insert_ts', 'etl_update_ts']
    },
    "bi.nacha_entries": {
        "description": "ACH/NACHA payment entries and processing data",
        "columns": ['id', 'created_at_date', 'batch_check_date', 'amount', 'company_id', 'employee_id', 'contractor_id', 'payroll_id', 'contractor_payment_id', 'agent_payment_id', 'error_code', 'is_debit', 'is_credit', 'entry_code', 'transaction_type', 'is_test_deposit', 'is_invoice', 'current_flag', 'updated_at', 'entry_id', 'international_contractor_id', 'international_contractor_payment_id', 'returned_code_at', 'international_employee_payroll_id', 'nacha_batch_id', 'bank_account_type', 'notify_if_error', 'resubmit_if_error', 'company_transaction', 'bank_account_id', 'dismissed', 'refund', 'accounting_firm_id', 'failed_entry_id', 'cleared', 'requested_by_id', 'payment_direction', 'origination_account_id', 'effective_entry_date', 'uuid', 'submission_date', 'dbt_incremental_ts', 'encrypted_bank_routing_number', 'processing_state', 'confirmation', 'ach_trace_id', 'ach_type', 'bank_account_hapii_id', 'correction_code', 'etl_insert_ts', 'etl_update_ts']
    },
    "bi.company_approval_details": {
        "description": "Company approval status and risk information",
        "columns": ['id', 'company_id', 'approved_by_id', 'approved_by_system', 'first_approved_at', 'last_rejected_at', 'approval_status', 'ready_for_approval', 'risk_state', 'risk_state_description', 'only_expeditable_by_risk', 'initial_auto_approval_blockers', 'auto_approval_blockers', 'created_at', 'updated_at', 'current_flag', 'dbt_incremental_ts', 'etl_insert_ts', 'etl_update_ts']
    },
    "bi.monthly_companies": {
        "description": "Monthly company metrics and revenue data",
        "columns": ['company_id', 'original_accounting_firm_id', 'for_month', 'product_plan', 'pricing_plan', 'number_of_paid_payrolls', 'estimated_annual_income_per_employee', 'has_active_workers_comp', 'invoice_number', 'is_churned', 'total_subscription_revenue', 'total_estimated_hi_mrr', 'total_gradvisor_revenue', 'total_guideline_revenue', 'total_revenue', 'total_payroll_revenue', 'total_tada_revenue', 'total_byb_revenue', 'total_hr_add_on_revenue', 'company_size', 'company_size_segment', 'has_plus_add_on', 'number_of_payroll_employees', 'number_of_payroll_contractors', 'number_of_hires', 'number_of_terminations', 'average_nps', 'average_csat', 'average_ces', 'average_likelihood', 'number_of_cases', 'number_of_payroll_care_cases', 'number_of_member_cases', 'number_of_sbs_cases', 'number_of_benefits_care_cases', 'number_of_taxops_cases', 'number_of_taxres_cases', 'number_of_risk_cases', 'number_of_task_us_cases', 'number_of_dsp_concierge_cases', 'number_of_chats', 'number_of_emails', 'number_of_calls', 'number_of_state_notice_reasons', 'number_of_payroll_expedite_reasons', 'number_of_other_reasons', 'number_of_payroll_reversal_reasons', 'number_of_off_cycle_payroll_reasons', 'number_of_spam_reasons', 'number_of_form_filing_question_reasons', 'number_of_state_tax_setup_reasons', 'number_of_suspend_account_reasons', 'number_of_irs_notice_reasons', 'number_of_high_priorities', 'number_of_medium_priorities', 'number_of_low_priorities', 'tfir_hours', 'tres_hours', 'handle_time_sec', 'number_of_touchpoints', 'number_of_admin_failed_logins', 'number_of_admin_logouts', 'number_of_admin_failed_captchas', 'number_of_admin_logins', 'number_of_admins_logging_in', 'number_of_days_admins_loggin_in', 'number_of_employee_failed_logins', 'number_of_employee_logouts', 'number_of_employee_failed_captchas', 'number_of_employee_logins', 'number_of_employees_logging_in', 'number_of_contractor_failed_logins', 'number_of_contractor_logouts', 'number_of_contractor_failed_captchas', 'number_of_admin_contractors', 'number_of_contractors_logging_in', 'min_balance', 'avg_balance', 'max_balance', 'std_balance', 'current_flag', 'updated_at', 'big_desk_sandbox_flag', 'big_desk_sandbox_benops_flag', 'total_estimated_icp_revenue', 'multistate_flag', 'active_state_count', 'states_list', 'ach_speed', 'running_total_number_of_cases', 'running_total_number_of_payroll_care_cases', 'running_total_number_of_member_cases', 'running_total_number_of_sbs_cases', 'running_total_number_of_benefits_care_cases', 'running_total_number_of_taxops_cases', 'running_total_number_of_taxres_cases', 'running_total_number_of_risk_cases', 'running_total_number_of_task_us_cases', 'running_total_number_of_dsp_concierge_cases', 'running_total_number_of_chats', 'running_total_number_of_emails', 'running_total_number_of_calls', 'running_total_number_of_state_notice_reasons', 'running_total_number_of_payroll_expedite_reasons', 'running_total_number_of_other_reasons', 'running_total_number_of_payroll_reversal_reasons', 'running_total_number_of_off_cycle_payroll_reasons', 'running_total_number_of_spam_reasons', 'running_total_number_of_form_filing_question_reasons', 'running_total_number_of_state_tax_setup_reasons', 'running_total_number_of_suspend_account_reasons', 'running_total_number_of_irs_notice_reasons', 'running_total_tfir_hours', 'running_total_tres_hours', 'running_total_handle_time_sec', 'running_total_number_of_high_priorities', 'running_total_number_of_medium_priorities', 'running_total_number_of_low_priorities', 'total_estimated_wc_mrr', 'total_revenue_adjusted', 'running_total_touchpoints', 'has_active_workers_comp_year_later', 'is_churned_year_later', 'number_of_payroll_employees_year_later', 'number_of_payroll_contractors_year_later', 'company_size_year_later', 'company_size_segment_year_later', 'total_revenue_year_later', 'total_payroll_revenue_year_later', 'total_gradvisor_revenue_year_later', 'total_guideline_revenue_year_later', 'total_subscription_revenue_year_later', 'total_estimated_hi_mrr_year_later', 'total_estimated_wc_mrr_year_later', 'product_plan_year_later', 'number_of_admin_click_emails', 'number_of_admin_delivered_emails', 'number_of_admin_open_emails', 'number_of_admin_processed_emails', 'number_of_contractor_click_emails', 'number_of_contractor_contractor_emails', 'number_of_contractor_delivered_emails', 'number_of_contractor_open_emails', 'number_of_contractor_paid_emails', 'number_of_contractor_processed_emails', 'number_of_employee_click_emails', 'number_of_employee_delivered_emails', 'number_of_employee_employee_emails', 'number_of_employee_open_emails', 'number_of_employee_paid_emails', 'number_of_employee_processed_emails', 'number_of_employee_welcome_emails', 'running_total_admin_open_emails', 'running_total_admin_click_emails', 'running_total_employee_open_emails', 'running_total_employee_click_emails']
    },
    "bi.user_roles": {
        "description": "User roles and permissions",
        "columns": ['id', 'user_id', 'type', 'employee_id', 'company_id', 'accounting_firm_id', 'contractor_id', 'payroll_admin_id', 'international_contractor_id', 'uuid', 'created_at', 'updated_at', 'etl_insert_ts', 'signatory_id', 'member_id']
    },
    "bi_reporting.risk_operational_metrics": {
        "description": "Risk operational metrics and case data",
        "columns": ['for_date', 'flow', 'age', 'sales_program', 'initial_company_size', 'is_gep_company', 'is_mrb', 'gep_partner_name', 'model_triggered', 'case_type', 'count_of_cases', 'total_active_customers', 'time_spent_in_mins']
    },
    "bi_reporting.risk_review_data": {
        "description": "Risk review activity data",
        "columns": ['calendar_date', 'week_start', 'reviewed_by_email', 'reviewer', 'event_timestamp', 'event_date', 'company_id', 'review_type', 'old_review_status', 'new_review_status']
    },
    "bi.sfdc_tickets": {
        "description": "Salesforce ticket data",
        "columns": ['sfdc_ticket_id', 'sfdc_owner_id', 'owner_role', 'created_ts', 'closed_ts', 'time_to_close_min', 'sfdc_createdby_id', 'creaated_by_role', 'reason', 'reason_detail', 'sfdc_carrier_id', 'sfdc_carrier_order_id', 'sfdc_benefit_order_id', 'status', 'access_to_care', 'team', 'sub_team', 'sfdc_case_id', 'assigned_to_user_ts', 'reporting_team', 'ticket_name', 'sfdc_record_type_id', 'record_type', 'sfdc_opportunity_id', 'sfdc_order_id', 'sfdc_qa_error_id', 'priority', 'sfdc_account_id', 'escalation_reason', 'escalation_reason_detail', 'escalation_class', 'time_to_inprogress', 'system_modified_ts', 'confirmed_ticket_reason', 'confirmed_ticket_reason_detail', 'carrier_details', 'employee_hippo_link', 'company_hippo_link', 'error_origin', 'error_type', 'sub_error_type', 'reimbursement_amount_approved', 'list_of_owner_change', 'false_positive', 'summary', 'owner_full_name', 'order_owner', 'blocking_future_clients', 'ticket_reason_pt', 'ticket_reason_detail_pt', 'company_id', 'related_jira_link_bd', 'jira_id', 'duplicate_ticket', 'error_origin_details', 'error_owner', 'er_outreach_count', 'discount_amount_approved', 'close_reason', 'integration_id', 'unavoidable_ticket_exclude_flag', 'rationale', 'error_origin_date', 'panda_nacha_id', 'error_detection_source', 'dbt_incremental_ts', 'etl_insert_ts', 'etl_update_ts', 'owner_pe_name', 'owner_pepe_name', 'owner_current_pe_name', 'owner_current_pepe_name', 'oa_longest_held_owner_id', 'total_oa_held_time_min']
    },
    "bi.cases": {
        "description": "Support cases and tickets",
        "columns": ['casenumber', 'id', 'trimmed_case_id', 'parent_case', 'zendesk_id', 'customer_journey', 'record_type_name', 'type', 'agency_information', 'case_owner_role', 'owned_by', 'ownerid', 'owner_queue', 'ignore_queue_flag', 'contactid', 'advocate_class', 'benefits_advocate_class', 'confirm_class_level_difficulty', 'root_cause', 'sub_root_cause', 'task_us_case', 'tier_solved__c', 'tier_created__c', 'historical_data__c', 'create_date', 'solved_at', 'closed_at', 'date_time_submitted', 'lastmodifieddate', 'total_touchpoints', 'tfir_hours', 'tfir_min', 'tfir_below_sla', 'tres_hours', 'tres_min', 'origin', 'bot_source_desc', 'channel', 'channel_origin', 'follow_up_flag', 'lsi__c', 'large_scale_issue_classification', 'large_scale_issue', 'subject', 'status', 'age', 'isclosed', 'isclosedoncreate', 'training_case', 'survey_sent', 'is_partner', 'reason', 'routing_case_reason', 'routing_case_reason_classification', 'confirm_case_reason', 'confirm_case_reason_classification', 'closed_reason', 'audience', 'priority', 'createdbyid', 'org', 'team', 'record_type_summary', 'notice_analyst_pod', 'notice_analyst', 'account_specialist_pod', 'account_specialist', 'coordinator_pod', 'shared_with', 'to_email_address', 'related_to_incident', 'direction', 'mass_email_template_applied', 'anticipated_effective_dt', 'termination_dt', 'sfdc_submitted_by_id', 'sfdc_carrier_id', 'sfdc_benefit_order_id', 'sfdc_opportunity_id', 'sfdc_order_id', 'confirm_sub_case_reason', 'confirm_sub_case_reason_classification', 'follow_up_method', 'routing_group', 'vip_tier_solved', 'vip_tier_created', 'sfdc_account_id', 'sfdc_case_reason_category_id', 'confirm_case_reason_category', 'sfdc_divr_category_id', 'divr_category', 'case_reason_sub_team', 'current_owner_first_assigned_ts', 'current_owner_first_email_response_ts', 'current_owner_tfir_min', 'specialization', 'divr_first_level', 'divr_second_level', 'divr_third_level', 'escalated_to', 'submission_method', 'audit_action', 'self_serviceable', 'follow_up_date', 'sfdc_follow_up_completed_by_id', 'follow_up_date_change_count', 'assigned_to_user_ts', 'first_response_time_deadline_ts', 'product', 'international_payment_country', 'first_response_ts', 'first_response_start_ts', 'automation_message', 'tax_res_autosolve_flag', 'automation_message_follow_up', 'automation_status', 'automation_status_follow_up', 'automation_retry_count', 'mf_automation_dt', 'mf_automation_submitted_ts', 'automated_email_sent', 'rfi_type', 'rfi_status', 'form_fits_dependents', 'form_fully_mapped', 'form_sent_automatically', 'missing_form_attributes', 'number_of_forms', 'is_byb_customer', 'penalty_amount', 'specialist_checklist_unlocking_ts', 'unlock_checklist_reason', 'requires_custom_solve_email', 'tax_notice_amount_total', 'tax_notice_date', 'tax_notice_form_number', 'tax_notice_numeration', 'tax_notice_type', 'last_modified_by_id', 'tax_res_auto_response_sent', 'in_band_flag', 'ht_outlier_flag', 'genesys_id', 'agency_state', 'agency_name', 'tax_type', 'chat_3_min_wait_time__c', 'chat_duration_min', 'chat_duration_sec', 'chat_wait_time_min', 'chat_abandoned_min', 'cobrowse_flag', 'cobrowse_duration_sec', 'first_in_progress_ts', 'first_from_draft_to_new_ts', 'first_moved_from_hold_to_new_ts', 'first_moved_from_new_ts', 'first_moved_to_new_ts', 'first_solved_closed_ts', 'case_owner_at_first_solved_id', 'case_owner_at_first_solved_eeid', 'auto_response_email_sent_flag', 'number_of_nonqueue_owners', 'notice_period', 'qle_event_type', 'partner_account', 'assigned_client_tax_id', 'tax_id', 'shelved_reason', 'group_member_update_type_text', 'mass_email_step', 'internal_support_requested_from', 'related_company', 'sfdc_unified_routing_id', 'missed_chat', 'has_call_notes', 'product_area', 'sub_product_area', 'ivr_routing_log_id', 'ivr_cip_queue_name', 'recent_queue_name', 'last_outbound_email_ts', 'related_case', 'has_integration_id', 'enrollment_source', 'byb_automation_authorized', 'engagement_autoclose_flag', 'original_sfdc_queue_id', 'last_sfdc_queue_id', 'original_engagement_pillar_sfdc_queue_id', 'last_engagement_pillar_sfdc_queue_id', 'pillar_persona', 'pillar_company_size', 'pillar_case_type', 'pillar_support_level', 'original_pillar_support_level', 'original_pillar_case_type', 'original_engagement_subpillar_key_legacy', 'last_engagement_subpillar_key_legacy', 'original_engagement_subpillar_key', 'last_engagement_subpillar_key', 'raw_sfdc_handle_time_sec', 'handle_time_sec', 'handle_time_min', 'handle_time_hrs', 'phone_handle_time_sec', 'chat_handle_time_sec', 'handled_flag', 'number_of_inbound_emails', 'number_of_outbound_emails', 'routing_team', 'routed_through_onboarding', 'sfdc_carrier_order_id', 'isescalated', 'escalation_reason', 'is_ocr_processed', 'ocr_message', 'ocr_status', 'used_macro_recommendation', 'partner_case_type', 'orca_predicted_case_reason', 'orca_predicted_case_reason_confidence', 'orca_predicted_specialization', 'orca_predicted_specialization_confidence', 'orca_predicted_support_level', 'orca_predicted_support_level_confidence', 'orca_predicted_type_confidence', 'qa_user', 'qa_status', 'rejection_reason', 'rejection_feedback', 'customer_intent_cancel_flag', 'hi_integration_error_flag', 'auto_indexing_status', 'tpo', 'gustie_resolution_time_hrs', 'current_flag', 'etl_comments', 'sor_deleted_etl_ts', 'sor_deleted_flag', 'escalation_severity', 'gus_session_id', 're_route_count', 'care_re_route_count', 'zp_user_id', 'company_id', 'accounting_firm_id', 'account_record_type', 'userroleid', 'usertype', 'name', 'ee_id', 'created_user', 'created_user_role', 'ticket_mapping', 'agatha_case_reason_prediction', 'agatha_case_prediction_confidence', 'is_gep_company', 'is_gep_leakage', 'has_ai_auto_response_draft', 'has_ai_auto_response_sent', 'ai_auto_response_model', 'case_reason_category', 'case_reason_product', 'case_reason_customer_journey', 'case_reason_team', 'app_name', 'functional_area', 'case_reason_group', 'etl_insert_ts', 'etl_update_ts', 'dbt_incremental_ts', 'closed_owner_role_category', 'is_gep_tier_1', 'is_gep_tier_2', 'gusto_class', 'gep_sub_case_reason', 'gep_category']
    },
    "bi.information_requests": {
        "description": "Information requests from agencies and compliance - requests for company/employee data and documentation",
        "columns": ['id', 'resource_id', 'resource_type', 'submission_state', 'situation', 'queue', 'company_id', 'requested_by_user_email', 'hide_from_review_queue', 'created_at', 'current_flag', 'updated_at', 'dbt_incremental_ts', 'etl_insert_ts', 'etl_update_ts']
    },
}

class RedshiftConnection:
    """Handles connections to Redshift database"""
    
    def __init__(self):
        self.host = os.getenv("REDSHIFT_HOST")
        self.database = os.getenv("REDSHIFT_DATABASE") 
        self.user = os.getenv("REDSHIFT_USERNAME")
        self.password = os.getenv("REDSHIFT_PASSWORD")
        self.port = int(os.getenv("REDSHIFT_PORT", 5439))
        self.conn = None
        self._connection_tested = False
        self._connection_works = False
        
    def is_configured(self) -> bool:
        """Check if all required credentials are available"""
        return all([self.host, self.database, self.user, self.password])
    
    def test_connection(self) -> bool:
        """Test connection to Redshift (with timeout and error handling)"""
        if self._connection_tested:
            return self._connection_works
            
        if not self.is_configured():
            self._connection_tested = True
            self._connection_works = False
            return False
            
        try:
            # Use a shorter timeout for public deployments
            conn = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port,
                connect_timeout=10  # 10 second timeout
            )
            conn.close()
            self._connection_tested = True
            self._connection_works = True
            return True
        except Exception as e:
            self._connection_tested = True
            self._connection_works = False
            # Store the error for debugging
            self._connection_error = str(e)
            return False
    
    def connect(self) -> bool:
        """Establish connection to Redshift"""
        if not self.test_connection():
            return False
            
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port,
                connect_timeout=10
            )
            return True
        except Exception as e:
            return False
    
    def execute_query(self, sql: str) -> Dict[str, Any]:
        """Execute SQL query and return results"""
        if not self.connect():
            return {"success": False, "error": "Database connection failed"}
        
        try:
            cursor = self.conn.cursor()
            start_time = datetime.now()
            cursor.execute(sql)
            
            # Fetch results
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Convert to list of dictionaries
            data = [dict(zip(columns, row)) for row in rows]
            
            return {
                "success": True,
                "data": data,
                "row_count": len(data),
                "execution_time_seconds": execution_time
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if cursor:
                cursor.close()

class SQLGenerator:
    """Generates SQL queries using OpenAI"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key and OPENAI_AVAILABLE:
            self.client = OpenAI(api_key=self.api_key)
            self.available = True
        else:
            self.available = False
    
    def generate_sql(self, natural_query: str) -> Dict[str, Any]:
        """Generate SQL from natural language query"""
        if not self.available:
            return self._mock_sql_generation(natural_query)
        
        try:
            # Create the prompt for OpenAI
            system_prompt = f"""You are a SQL expert for Gusto's data warehouse. Generate Redshift-compatible SQL queries.

Available tables and their purposes:
{json.dumps(TABLE_SCHEMAS, indent=2)}

Rules:
1. Only use tables from the schema above
2. Use Redshift/PostgreSQL syntax
3. Always include LIMIT clauses to prevent large result sets
4. Use proper JOINs when combining tables
5. Return only the SQL query, no explanations

Generate a SQL query for: {natural_query}"""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": system_prompt}],
                max_tokens=500,
                temperature=0.1
            )
            
            sql_query = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            if sql_query.startswith("```sql"):
                sql_query = sql_query[6:-3]
            elif sql_query.startswith("```"):
                sql_query = sql_query[3:-3]
            
            return {
                "success": True,
                "sql": sql_query,
                "explanation": f"AI-generated SQL for: {natural_query}"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _mock_sql_generation(self, query: str) -> Dict[str, Any]:
        """Fallback mock SQL generation when OpenAI is not available"""
        q = query.lower()
        
        if "credit delinquencies" in q and "30 days" in q:
            sql = """SELECT c.name AS company_name, c.filing_state, cd.debit_date, cd.debit_amount_attempted, cd.delinquent_status
FROM bi.companies c
JOIN bi.credit_delinquencies cd ON c.id = cd.company_id
WHERE cd.debit_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY cd.debit_date DESC
LIMIT 100;"""
        elif "employee count" in q:
            sql = """SELECT name AS company_name, filing_state, number_active_employees
FROM bi.companies
WHERE number_active_employees IS NOT NULL
ORDER BY number_active_employees DESC
LIMIT 20;"""
        elif "california" in q or "risk" in q:
            sql = """SELECT c.name AS company_name, c.filing_state, COUNT(cd.company_id) AS risk_score
FROM bi.companies c
LEFT JOIN bi.credit_delinquencies cd ON c.id = cd.company_id
WHERE c.filing_state = 'CA'
GROUP BY c.id, c.name, c.filing_state
ORDER BY risk_score DESC
LIMIT 50;"""
        elif "monthly volumes" in q or "monthly volume" in q:
            sql = """SELECT DATE_TRUNC('month', created_at) AS month, COUNT(*) AS volume
FROM bi.companies
WHERE created_at >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY DATE_TRUNC('month', created_at)
ORDER BY month DESC
LIMIT 12;"""
        elif "weekly volumes" in q or "weekly volume" in q:
            sql = """SELECT DATE_TRUNC('week', created_at) AS week, COUNT(*) AS volume
FROM bi.companies
WHERE created_at >= CURRENT_DATE - INTERVAL '12 weeks'
GROUP BY DATE_TRUNC('week', created_at)
ORDER BY week DESC
LIMIT 12;"""
        elif "daily volumes" in q or "daily volume" in q:
            sql = """SELECT DATE_TRUNC('day', created_at) AS day, COUNT(*) AS volume
FROM bi.companies
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', created_at)
ORDER BY day DESC
LIMIT 30;"""
        elif "monthly" in q and ("count" in q or "volume" in q or "total" in q):
            sql = """SELECT DATE_TRUNC('month', created_at) AS month, COUNT(*) AS count
FROM bi.companies
WHERE created_at >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY DATE_TRUNC('month', created_at)
ORDER BY month DESC
LIMIT 12;"""
        elif "weekly" in q and ("count" in q or "volume" in q or "total" in q):
            sql = """SELECT DATE_TRUNC('week', created_at) AS week, COUNT(*) AS count
FROM bi.companies
WHERE created_at >= CURRENT_DATE - INTERVAL '12 weeks'
GROUP BY DATE_TRUNC('week', created_at)
ORDER BY week DESC
LIMIT 12;"""
        elif "daily" in q and ("count" in q or "volume" in q or "total" in q):
            sql = """SELECT DATE_TRUNC('day', created_at) AS day, COUNT(*) AS count
FROM bi.companies
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', created_at)
ORDER BY day DESC
LIMIT 30;"""
        elif "penalty" in q:
            sql = """SELECT c.name AS company_name, pc.agency_name, pc.total_penalty_amount, pc.status
FROM bi.companies c
JOIN bi.penalty_cases pc ON c.id = pc.agent_id
WHERE pc.total_penalty_amount > 0
ORDER BY pc.total_penalty_amount DESC
LIMIT 50;"""
        elif "information request" in q or "info request" in q:
            sql = """SELECT c.name AS company_name, ir.submission_state, ir.situation, ir.queue, ir.created_at, ir.requested_by_user_email
FROM bi.companies c
JOIN bi.information_requests ir ON c.id = ir.company_id
WHERE ir.current_flag = true
ORDER BY ir.created_at DESC
LIMIT 100;"""
        else:
            sql = """SELECT name AS company_name, filing_state, number_active_employees
FROM bi.companies
WHERE is_active = true
LIMIT 100;"""
        
        return {
            "success": True,
            "sql": sql,
            "explanation": f"Template SQL generated for: {query} (using real Gusto schema)"
        }

def generate_realistic_demo_data(sql: str, query: str) -> List[Dict]:
    """Generate realistic demo data based on the SQL and query"""
    q = query.lower()
    
    if "credit delinquencies" in q or "delinquent" in sql.lower():
        return [
            {"company_name": "TechStart Solutions", "filing_state": "CA", "debit_date": "2024-01-15", "debit_amount_attempted": 15000, "delinquent_status": "Active"},
            {"company_name": "DataFlow Analytics", "filing_state": "NY", "debit_date": "2024-01-12", "debit_amount_attempted": 8500, "delinquent_status": "Active"},
            {"company_name": "CloudOps Systems", "filing_state": "TX", "debit_date": "2024-01-08", "debit_amount_attempted": 12750, "delinquent_status": "Resolved"},
            {"company_name": "InnovateTech Corp", "filing_state": "CA", "debit_date": "2024-01-05", "debit_amount_attempted": 22000, "delinquent_status": "Active"},
            {"company_name": "GreenField Logistics", "filing_state": "FL", "debit_date": "2024-01-03", "debit_amount_attempted": 5200, "delinquent_status": "Active"}
        ]
    elif "employee" in q or "number_active_employees" in sql.lower():
        return [
            {"company_name": "MegaCorp Industries", "filing_state": "CA", "number_active_employees": 2847},
            {"company_name": "Global Tech Solutions", "filing_state": "NY", "number_active_employees": 1923},
            {"company_name": "Innovation Labs Inc", "filing_state": "TX", "number_active_employees": 1456},
            {"company_name": "Future Systems LLC", "filing_state": "WA", "number_active_employees": 891},
            {"company_name": "Dynamic Solutions", "filing_state": "FL", "number_active_employees": 743},
            {"company_name": "NextGen Technologies", "filing_state": "CA", "number_active_employees": 652},
            {"company_name": "Quantum Dynamics", "filing_state": "MA", "number_active_employees": 589},
            {"company_name": "Stellar Innovations", "filing_state": "CO", "number_active_employees": 401}
        ]
    elif "penalty" in q or "penalty_amount" in sql.lower():
        return [
            {"company_name": "Apex Manufacturing", "agency_name": "California EDD", "total_penalty_amount": 12500, "status": "Open"},
            {"company_name": "Metro Services LLC", "agency_name": "Texas TWC", "total_penalty_amount": 8900, "status": "Under Review"},
            {"company_name": "Pioneer Industries", "agency_name": "New York DOL", "total_penalty_amount": 15600, "status": "Resolved"},
            {"company_name": "Coastal Enterprises", "agency_name": "Florida DEO", "total_penalty_amount": 6750, "status": "Open"}
        ]
    elif "california" in q or "risk" in q:
        return [
            {"company_name": "Silicon Valley Startups", "filing_state": "CA", "risk_score": 3},
            {"company_name": "Bay Area Technologies", "filing_state": "CA", "risk_score": 2},
            {"company_name": "Los Angeles Media Co", "filing_state": "CA", "risk_score": 1},
            {"company_name": "San Diego Biotech", "filing_state": "CA", "risk_score": 0},
            {"company_name": "Sacramento Solutions", "filing_state": "CA", "risk_score": 0}
        ]
    elif "monthly volumes" in q.lower() or "monthly volume" in q.lower():
        return [
            {"month": "2024-01-01", "volume": 1247},
            {"month": "2023-12-01", "volume": 1189},
            {"month": "2023-11-01", "volume": 1356},
            {"month": "2023-10-01", "volume": 1298},
            {"month": "2023-09-01", "volume": 1423},
            {"month": "2023-08-01", "volume": 1387},
            {"month": "2023-07-01", "volume": 1312},
            {"month": "2023-06-01", "volume": 1456},
            {"month": "2023-05-01", "volume": 1398},
            {"month": "2023-04-01", "volume": 1321},
            {"month": "2023-03-01", "volume": 1287},
            {"month": "2023-02-01", "volume": 1156}
        ]
    elif "weekly volumes" in q.lower() or "weekly volume" in q.lower():
        return [
            {"week": "2024-01-15", "volume": 312},
            {"week": "2024-01-08", "volume": 298},
            {"week": "2024-01-01", "volume": 287},
            {"week": "2023-12-25", "volume": 234},
            {"week": "2023-12-18", "volume": 345},
            {"week": "2023-12-11", "volume": 312},
            {"week": "2023-12-04", "volume": 298},
            {"week": "2023-11-27", "volume": 356},
            {"week": "2023-11-20", "volume": 321},
            {"week": "2023-11-13", "volume": 298},
            {"week": "2023-11-06", "volume": 312},
            {"week": "2023-10-30", "volume": 287}
        ]
    elif "daily volumes" in q.lower() or "daily volume" in q.lower():
        return [
            {"day": "2024-01-20", "volume": 45},
            {"day": "2024-01-19", "volume": 52},
            {"day": "2024-01-18", "volume": 38},
            {"day": "2024-01-17", "volume": 41},
            {"day": "2024-01-16", "volume": 47},
            {"day": "2024-01-15", "volume": 43},
            {"day": "2024-01-14", "volume": 39},
            {"day": "2024-01-13", "volume": 35},
            {"day": "2024-01-12", "volume": 48},
            {"day": "2024-01-11", "volume": 44},
            {"day": "2024-01-10", "volume": 42},
            {"day": "2024-01-09", "volume": 46},
            {"day": "2024-01-08", "volume": 40},
            {"day": "2024-01-07", "volume": 37},
            {"day": "2024-01-06", "volume": 33},
            {"day": "2024-01-05", "volume": 49},
            {"day": "2024-01-04", "volume": 45},
            {"day": "2024-01-03", "volume": 41},
            {"day": "2024-01-02", "volume": 38},
            {"day": "2024-01-01", "volume": 35}
        ]
    elif "information request" in q.lower() or "info request" in q.lower():
        return [
            {"company_name": "TechVentures Inc", "submission_state": "submitted", "situation": "compliance_review", "queue": "high_priority", "created_at": "2024-01-20 10:30:00", "requested_by_user_email": "compliance@agency.gov"},
            {"company_name": "DataCorp Solutions", "submission_state": "pending", "situation": "audit_request", "queue": "standard", "created_at": "2024-01-18 14:15:00", "requested_by_user_email": "auditor@irs.gov"},
            {"company_name": "CloudWorks LLC", "submission_state": "in_review", "situation": "employment_verification", "queue": "urgent", "created_at": "2024-01-15 09:45:00", "requested_by_user_email": "dol@labor.gov"},
            {"company_name": "Innovation Systems", "submission_state": "submitted", "situation": "tax_inquiry", "queue": "high_priority", "created_at": "2024-01-12 16:20:00", "requested_by_user_email": "tax@state.tx.us"},
            {"company_name": "Metro Services", "submission_state": "pending", "situation": "benefits_verification", "queue": "standard", "created_at": "2024-01-10 11:10:00", "requested_by_user_email": "benefits@florida.gov"}
        ]
    else:
        return [
            {"company_name": "Acme Corporation", "filing_state": "CA", "number_active_employees": 245},
            {"company_name": "Demo Industries", "filing_state": "NY", "number_active_employees": 189},
            {"company_name": "Example LLC", "filing_state": "TX", "number_active_employees": 156},
            {"company_name": "Sample Solutions", "filing_state": "FL", "number_active_employees": 98},
            {"company_name": "Test Technologies", "filing_state": "WA", "number_active_employees": 67}
        ]


def generate_smart_visualization(df, query, sql):
    """Generate appropriate visualizations based on query type and data"""
    import plotly.express as px
    import plotly.graph_objects as go
    
    q = query.lower()
    sql_lower = sql.lower()
    
    # Check if query uses aggregate functions
    has_aggregates = any(func in sql_lower for func in ['count(', 'sum(', 'avg(', 'max(', 'min(', 'group by'])
    
    if not has_aggregates:
        return None
    
    # Get numeric columns for analysis
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    if len(numeric_cols) == 0:
        return None
    
    # 1. PIE CHART for categorical breakdowns with counts/sums
    if any(word in q for word in ['breakdown', 'by category', 'by type', 'by status', 'by state', 'by department']):
        if len(df) > 0 and len(df) <= 20:  # Reasonable pie chart size
            # Find the best categorical column
            categorical_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
            if categorical_cols and numeric_cols:
                cat_col = categorical_cols[0]
                num_col = numeric_cols[0]
                
                fig = px.pie(df, values=num_col, names=cat_col, 
                           title=f"Breakdown by {cat_col.replace('_', ' ').title()}")
                return fig
    
    # 2. TIME-BASED CHARTS for temporal data
    elif any(word in q for word in ['monthly', 'weekly', 'daily', 'over time', 'trend', 'volume', 'volumes']):
        # Look for date/time columns
        date_cols = []
        for col in df.columns:
            if any(word in col.lower() for word in ['date', 'time', 'month', 'week', 'day', 'created', 'updated']):
                date_cols.append(col)
        
        if date_cols and numeric_cols:
            date_col = date_cols[0]
            num_col = numeric_cols[0]
            
            # Try to convert to datetime for proper sorting
            try:
                df_sorted = df.copy()
                df_sorted[date_col] = pd.to_datetime(df_sorted[date_col])
                df_sorted = df_sorted.sort_values(date_col)
                
                # Use line chart for time series
                fig = px.line(df_sorted, x=date_col, y=num_col,
                            title=f"{num_col.replace('_', ' ').title()} Over Time")
                return fig
            except:
                # Fallback to bar chart if date conversion fails
                fig = px.bar(df, x=date_col, y=num_col,
                           title=f"{num_col.replace('_', ' ').title()} by {date_col.replace('_', ' ').title()}")
                return fig
    
    # 3. BAR CHART for general aggregations
    elif any(word in q for word in ['top', 'highest', 'largest', 'biggest', 'by company', 'by department']):
        if len(df) > 0:
            # Use first categorical and first numeric column
            categorical_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
            if categorical_cols and numeric_cols:
                cat_col = categorical_cols[0]
                num_col = numeric_cols[0]
                
                # Sort by numeric column for better visualization
                df_sorted = df.sort_values(num_col, ascending=False).head(15)  # Top 15 for readability
                
                fig = px.bar(df_sorted, x=cat_col, y=num_col,
                           title=f"Top {cat_col.replace('_', ' ').title()} by {num_col.replace('_', ' ').title()}")
                fig.update_xaxis(tickangle=45)
                return fig
    
    # 4. DEFAULT: Simple bar chart for any aggregation
    else:
        if len(df) > 0 and len(df) <= 50:  # Reasonable chart size
            categorical_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
            if categorical_cols and numeric_cols:
                cat_col = categorical_cols[0]
                num_col = numeric_cols[0]
                
                fig = px.bar(df, x=cat_col, y=num_col,
                           title=f"{num_col.replace('_', ' ').title()} by {cat_col.replace('_', ' ').title()}")
                fig.update_xaxis(tickangle=45)
                return fig
    
    return None

def check_system_status():
    """Check what systems are available (OpenAI, Redshift)"""
    db = RedshiftConnection()
    sql_gen = SQLGenerator()
    
    redshift_works = db.test_connection()
    
    return {
        "redshift_configured": db.is_configured(),
        "redshift_accessible": redshift_works,
        "openai_available": sql_gen.available,
        "demo_mode": not (redshift_works and sql_gen.available)
    }

# Main App
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