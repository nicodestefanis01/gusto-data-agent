# Production Deployment Guide

## 🚀 Production Mode Features

### ✅ **Optimized Performance**
- Cached data and functions
- Reduced logging in production
- Headless mode for servers
- Optimized memory usage

### 🔧 **Production Configuration**
- Environment variable detection
- Cloud deployment support
- Error handling and recovery
- Health checks and monitoring

## 📦 **Deployment Options**

### 1. **Streamlit Cloud (Recommended)**
```bash
# Push to GitHub
git add .
git commit -m "Production deployment"
git push

# Deploy on Streamlit Cloud
# - Connect your GitHub repo
# - Set environment variables
# - Deploy automatically
```

### 2. **Docker Deployment**
```bash
# Build and run with Docker
docker build -t gusto-data-agent .
docker run -p 8501:8501 --env-file .env gusto-data-agent

# Or use docker-compose
docker-compose up -d
```

### 3. **Direct Server Deployment**
```bash
# Install dependencies
pip install -r requirements.txt

# Set production mode
export PRODUCTION_MODE=true

# Start production server
./start_production.sh
```

## 🔧 **Environment Variables**

### **Required for Production:**
```
PRODUCTION_MODE=true
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

### **Database Configuration:**
```
REDSHIFT_HOST=your_host
REDSHIFT_DATABASE=your_database
REDSHIFT_USERNAME=your_username
REDSHIFT_PASSWORD=your_password
REDSHIFT_PORT=5439
```

### **API Configuration:**
```
OPENAI_API_KEY=your_api_key
```

## 📊 **Production Monitoring**

### **Health Checks:**
- Application health: `http://localhost:8501/_stcore/health`
- Database connectivity: Automatic detection
- API connectivity: Automatic detection

### **Performance:**
- Cached functions for faster loading
- Optimized memory usage
- Reduced logging overhead
- Headless mode for servers

## 🚀 **Quick Start**

1. **Set Environment Variables:**
   ```bash
   export PRODUCTION_MODE=true
   ```

2. **Start Production Server:**
   ```bash
   ./start_production.sh
   ```

3. **Access Application:**
   - Local: `http://localhost:8501`
   - Network: `http://your-server-ip:8501`

## 🔒 **Security Features**

- VPN access control (local only)
- Environment variable protection
- Error message sanitization
- Production logging levels
