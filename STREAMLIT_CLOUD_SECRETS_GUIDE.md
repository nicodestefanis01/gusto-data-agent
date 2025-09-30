# Streamlit Cloud Secrets Setup Guide

## 🔧 **TOML Format for Streamlit Cloud Secrets**

When setting up secrets in Streamlit Cloud, you need to use TOML format. Here's the correct format:

### **Step 1: Go to Streamlit Cloud**
1. Visit [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Connect your repository: `https://github.com/nicodestefanis01/gusto-data-agent`

### **Step 2: Configure Secrets**
In the "Secrets" section, paste this TOML format:

```toml
# Database Configuration
REDSHIFT_HOST = "dataeng-prod.cqyxh8rl6vlx.us-west-2.redshift.amazonaws.com"
REDSHIFT_DATABASE = "your_database_name"
REDSHIFT_USERNAME = "your_username"
REDSHIFT_PASSWORD = "your_password"
REDSHIFT_PORT = "5439"

# API Configuration
OPENAI_API_KEY = "your_openai_api_key_here"

# VPN and Network Configuration
VPN_REQUIRED = false
ALLOWED_NETWORKS = ["0.0.0.0/0"]

# Production Configuration
PRODUCTION_MODE = true
STREAMLIT_CLOUD = true
```

### **Step 3: Replace Values**
Replace the placeholder values with your actual credentials:

- `your_database_name` → Your actual database name
- `your_username` → Your actual Redshift username
- `your_password` → Your actual Redshift password
- `your_openai_api_key_here` → Your actual OpenAI API key

### **Step 4: Deploy**
Click "Deploy" and your app will be deployed to Streamlit Cloud!

## 🚨 **Common TOML Format Errors**

### ❌ **Wrong Format (Key-Value Pairs):**
```
REDSHIFT_HOST=dataeng-prod.cqyxh8rl6vlx.us-west-2.redshift.amazonaws.com
REDSHIFT_DATABASE=your_database_name
```

### ✅ **Correct Format (TOML):**
```toml
REDSHIFT_HOST = "dataeng-prod.cqyxh8rl6vlx.us-west-2.redshift.amazonaws.com"
REDSHIFT_DATABASE = "your_database_name"
```

## 🔑 **Key TOML Rules:**

1. **Use quotes** around string values: `"value"`
2. **Use equals sign with spaces**: `KEY = "value"`
3. **No quotes for booleans**: `VPN_REQUIRED = false`
4. **Arrays use brackets**: `ALLOWED_NETWORKS = ["0.0.0.0/0"]`
5. **Comments use #**: `# This is a comment`

## 📊 **Expected Behavior:**

- ✅ **Cloud Mode**: App detects Streamlit Cloud environment
- ✅ **Demo Data**: Uses sample data when database unavailable
- ✅ **Full UI**: All features work with demo data
- ✅ **No Errors**: Graceful handling of connection issues

## 🚀 **Deployment Steps:**

1. **Copy the TOML format above**
2. **Replace placeholder values with real credentials**
3. **Paste into Streamlit Cloud secrets section**
4. **Click Deploy**
5. **Access your app at the provided URL**

## 🔧 **Troubleshooting:**

### **"Invalid format: please enter valid TOML"**
- Make sure you're using TOML format, not key-value pairs
- Check that all strings are in quotes
- Verify boolean values don't have quotes

### **Database Connection Issues**
- This is expected in cloud environment
- App will automatically use demo mode
- All features will work with sample data

### **App Not Loading**
- Check that all required secrets are set
- Verify TOML syntax is correct
- Check the deployment logs for errors
