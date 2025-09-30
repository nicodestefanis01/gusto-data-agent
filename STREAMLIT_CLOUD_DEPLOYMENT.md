
# Gusto Data Agent - Streamlit Cloud Deployment Guide

## 🚀 Deploy to Streamlit Cloud

### Step 1: Prepare Your Repository
1. **Push to GitHub**: Ensure your code is in a GitHub repository
2. **Set up secrets**: Configure your credentials in Streamlit Cloud
3. **Deploy**: Connect your GitHub repo to Streamlit Cloud

### Step 2: Configure Secrets in Streamlit Cloud
Go to your Streamlit Cloud dashboard and add these secrets:

```toml
[secrets]
REDSHIFT_HOST = "your-redshift-host.amazonaws.com"
REDSHIFT_DATABASE = "your-database-name"
REDSHIFT_USERNAME = "your-username"
REDSHIFT_PASSWORD = "your-password"
REDSHIFT_PORT = "5439"
OPENAI_API_KEY = "your-openai-api-key"
VPN_REQUIRED = true
ALLOWED_NETWORKS = ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
```

### Step 3: Deploy
1. **Visit**: https://share.streamlit.io
2. **Connect GitHub**: Link your repository
3. **Configure**: Set main file to `app.py`
4. **Deploy**: Click "Deploy!"

### Step 4: Access Your App
- **Public URL**: `https://your-app-name.streamlit.app`
- **VPN Required**: Only accessible when connected to Gusto VPN
- **Team Sharing**: Share the URL with your team

## 🔒 Security Features

### VPN-Only Access
- ✅ **Network Filtering**: Only allows internal network access
- ✅ **IP Validation**: Automatically detects and validates client IP
- ✅ **External Blocking**: Completely blocks internet access without VPN
- ✅ **Clear Messaging**: Shows helpful error messages for unauthorized access

### Production Security
- ✅ **Secure Headers**: Production-grade security headers
- ✅ **Error Hiding**: Sensitive database errors are hidden
- ✅ **Credential Protection**: All credentials stored securely in Streamlit secrets

## 📊 Features Available

- **Real Database Access**: Connected to Gusto Redshift warehouse
- **AI-Powered SQL**: Natural language to SQL conversion
- **Smart Visualizations**: Automatic charts for aggregations
- **Time-Based Analysis**: Monthly, weekly, daily volume queries
- **Information Requests**: Full support for compliance queries
- **CSV Export**: Download results for further analysis

## 🛠️ Troubleshooting

### "Access Restricted" Error
- Ensure you're connected to Gusto VPN
- Check with IT if VPN connection is working
- Try refreshing the page

### "Database Connection Failed"
- Check if credentials are correctly set in Streamlit secrets
- Verify VPN connection to database
- Contact administrator if issues persist

## 📞 Support

For technical issues:
- **Database Issues**: Data Engineering Team
- **VPN Issues**: IT Support  
- **Application Issues**: [Your Name/Team]

## 🎉 Benefits of Streamlit Cloud

- ✅ **No Server Management**: Streamlit handles all infrastructure
- ✅ **Automatic Updates**: Deploy updates by pushing to GitHub
- ✅ **Team Access**: Share URL with your entire team
- ✅ **Secure**: VPN-only access with network filtering
- ✅ **Scalable**: Handles multiple concurrent users
- ✅ **Free**: No hosting costs for public apps

---
*Generated on: 2025-09-30 13:56:17*
