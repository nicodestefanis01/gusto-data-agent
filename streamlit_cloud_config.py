"""
Streamlit Cloud Configuration for Gusto Data Agent
Handles environment variables and secrets for cloud deployment
"""

import os
import streamlit as st
from dotenv import load_dotenv

def get_cloud_config():
    """Get configuration for Streamlit Cloud deployment"""
    
    # Try to load from .env first (local development)
    load_dotenv()
    
    # For Streamlit Cloud, use secrets
    if hasattr(st, 'secrets'):
        # Handle VPN_REQUIRED safely
        vpn_required = st.secrets.get('VPN_REQUIRED', 'true')
        if isinstance(vpn_required, bool):
            vpn_required_bool = vpn_required
        else:
            vpn_required_bool = str(vpn_required).lower() == 'true'
            
        return {
            'REDSHIFT_HOST': st.secrets.get('REDSHIFT_HOST', os.getenv('REDSHIFT_HOST')),
            'REDSHIFT_DATABASE': st.secrets.get('REDSHIFT_DATABASE', os.getenv('REDSHIFT_DATABASE')),
            'REDSHIFT_USERNAME': st.secrets.get('REDSHIFT_USERNAME', os.getenv('REDSHIFT_USERNAME')),
            'REDSHIFT_PASSWORD': st.secrets.get('REDSHIFT_PASSWORD', os.getenv('REDSHIFT_PASSWORD')),
            'REDSHIFT_PORT': st.secrets.get('REDSHIFT_PORT', os.getenv('REDSHIFT_PORT', '5439')),
            'OPENAI_API_KEY': st.secrets.get('OPENAI_API_KEY', os.getenv('OPENAI_API_KEY')),
            'VPN_REQUIRED': vpn_required_bool,
            'ALLOWED_NETWORKS': st.secrets.get('ALLOWED_NETWORKS', ['10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16'])
        }
    else:
        # Fallback to environment variables
        # Handle VPN_REQUIRED safely
        vpn_required = os.getenv('VPN_REQUIRED', 'true')
        if isinstance(vpn_required, bool):
            vpn_required_bool = vpn_required
        else:
            vpn_required_bool = str(vpn_required).lower() == 'true'
            
        return {
            'REDSHIFT_HOST': os.getenv('REDSHIFT_HOST'),
            'REDSHIFT_DATABASE': os.getenv('REDSHIFT_DATABASE'),
            'REDSHIFT_USERNAME': os.getenv('REDSHIFT_USERNAME'),
            'REDSHIFT_PASSWORD': os.getenv('REDSHIFT_PASSWORD'),
            'REDSHIFT_PORT': os.getenv('REDSHIFT_PORT', '5439'),
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
            'VPN_REQUIRED': vpn_required_bool,
            'ALLOWED_NETWORKS': os.getenv('ALLOWED_NETWORKS', '10.0.0.0/8,172.16.0.0/12,192.168.0.0/16').split(',')
        }
