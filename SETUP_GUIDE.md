# 🚀 Setup Guide

Complete step-by-step guide to set up the Sales Analytics Dashboard.

## Prerequisites

- Python 3.9 or higher
- Google account
- Sales data in Excel format
- Basic command line knowledge

## Part 1: Local Development Setup

### Step 1: Install Python

**Check if Python is installed:**
```bash
python --version
```

**If not installed:**
- **Windows**: Download from [python.org](https://www.python.org/downloads/)
- **Mac**: `brew install python3`
- **Linux**: `sudo apt install python3 python3-pip`

### Step 2: Clone Repository

```bash
# Clone the repo
git clone https://github.com/yourusername/sales-analytics-dashboard.git

# Navigate to directory
cd sales-analytics-dashboard
```

### Step 3: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected output:**
```
Installing collected packages: streamlit, pandas, plotly, google-api-python-client...
Successfully installed streamlit-1.31.0 pandas-2.1.4 ...
```

## Part 2: Google Drive Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. **Project Name**: "Sales Dashboard" (or your choice)
4. Click **Create**
5. Wait for project creation (~30 seconds)

### Step 2: Enable Google Drive API

1. In Google Cloud Console, select your new project
2. Go to **APIs & Services** → **Library**
3. Search for "Google Drive API"
4. Click on it
5. Click **Enable**
6. Wait for activation (~10 seconds)

### Step 3: Create Service Account

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **Service Account**
3. **Service account name**: "sales-dashboard"
4. **Service account ID**: (auto-generated)
5. Click **Create and Continue**
6. **Role**: Select "Basic" → "Viewer" (read-only)
7. Click **Continue**
8. Click **Done**

### Step 4: Download Service Account Key

1. In **Credentials** page, click on your service account email
2. Go to **Keys** tab
3. Click **Add Key** → **Create new key**
4. Choose **JSON** format
5. Click **Create**
6. **Important**: Save the downloaded JSON file
7. Rename it to `service_account.json`
8. Move it to your project root folder

**Example service_account.json:**
```json
{
  "type": "service_account",
  "project_id": "your-project-12345",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "sales-dashboard@your-project.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
}
```

### Step 5: Prepare Google Drive Folder

1. Open [Google Drive](https://drive.google.com)
2. Create a new folder (e.g., "Sales Data")
3. Upload your sales Excel files to this folder
4. **Get Folder ID**:
   - Open the folder
   - Look at URL: `https://drive.google.com/drive/folders/1ABC123xyz...`
   - Copy the ID: `1ABC123xyz...`

### Step 6: Share Folder with Service Account

1. In Google Drive, right-click your folder
2. Click **Share**
3. In "Add people and groups":
   - Paste the service account email: `sales-dashboard@your-project.iam.gserviceaccount.com`
   - Role: **Viewer**
4. **Uncheck** "Notify people"
5. Click **Share**

**✅ You should see the service account in "People with access"**

## Part 3: Configure Application

### Step 1: Update Folder ID

Edit `sales_dashboard.py` (around line 483):

```python
# Replace this line:
SALES_FOLDER_ID = "YOUR_GOOGLE_DRIVE_FOLDER_ID_HERE"

# With your actual folder ID:
SALES_FOLDER_ID = "1ABC123xyz..."  # Your folder ID from Step 5
```

### Step 2: Customize Categories (Optional)

Edit the `get_product_category()` function (line 290):

```python
def get_product_category(item):
    """Categorize your products"""
    item = str(item).upper().strip()
    
    # Add your business logic
    if "BREAD" in item: return "Bakery"
    if "COFFEE" in item: return "Beverages"
    # ... etc
```

### Step 3: Verify File Structure

Your folder should look like:
```
sales-analytics-dashboard/
├── sales_dashboard.py          ✅
├── requirements.txt            ✅
├── .gitignore                  ✅
├── README.md                   ✅
├── service_account.json        ✅ (NOT in git)
└── venv/                       ✅
```

## Part 4: First Run

### Step 1: Start the App

```bash
streamlit run sales_dashboard.py
```

**Expected output:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.x:8501
```

### Step 2: Open Browser

Navigate to `http://localhost:8501`

### Step 3: Load Data

1. You should see the welcome screen
2. Click **📅 Select Date Range to Load Data**
3. Choose start and end dates
4. Click **🔄 Load Data from Drive**
5. Wait for data to load (~5-30 seconds depending on data size)

**✅ Success!** You should see the dashboard with your data!

## Part 5: Production Deployment (Streamlit Cloud)

### Step 1: Prepare for Deployment

1. Create a **private** GitHub repository
2. Push your code (WITHOUT `service_account.json`)

```bash
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/sales-dashboard.git
git push -u origin main
```

### Step 2: Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **New app**
3. **Repository**: Select your GitHub repo
4. **Branch**: `main`
5. **Main file path**: `sales_dashboard.py`
6. Click **Advanced settings**

### Step 3: Add Secrets

In the "Secrets" box, paste your service account JSON:

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-12345"
private_key_id = "abc123..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "sales-dashboard@your-project.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```

### Step 4: Set Email Whitelist (Optional)

1. After deployment, go to app settings
2. **Sharing** → **Manage viewers**
3. Add allowed email addresses
4. Only these emails can access the app

### Step 5: Deploy!

1. Click **Deploy!**
2. Wait 2-3 minutes for deployment
3. Your app will be live at: `https://your-app-name.streamlit.app`

## Troubleshooting

### "No credentials found"

**Solution**:
- Ensure `service_account.json` is in project root
- Check file is valid JSON
- Verify file permissions

### "Authentication failed"

**Solution**:
- Verify service account email is correct
- Check Google Drive folder is shared with service account
- Re-download service account key if needed

### "No data found"

**Solution**:
- Verify folder ID is correct
- Check files are in Excel format (.xlsx)
- Ensure date range includes available data
- Verify file naming pattern matches (YYYYMMDD)

### "Module not found"

**Solution**:
```bash
pip install -r requirements.txt
```

### "Port already in use"

**Solution**:
```bash
# Use different port
streamlit run sales_dashboard.py --server.port 8502
```

### Streamlit Cloud Issues

**"Failed to build"**:
- Check requirements.txt has all dependencies
- Verify Python version compatibility
- Check logs for specific error

**"Secrets not loading"**:
- Ensure TOML format is correct
- No extra quotes or formatting
- Each field on new line

## Data File Requirements

### File Naming

Files must follow this pattern:
```
YourBusinessName_YYYYMMDD.xlsx
```

Examples:
- `SalesData_20241215.xlsx` ✅
- `Sales_20241215.xlsx` ✅
- `sales-data-15-12-2024.xlsx` ❌ (wrong format)

### Required Columns

| Column Name | Type | Description | Example |
|-------------|------|-------------|---------|
| Date or TransactionDate | Date | Sale date | 2024-12-15 |
| Description | Text | Product name | House Sourdough |
| Quantity | Number | Units sold | 5 |
| ExtendedNetAmount | Number | Revenue | 45.50 |
| SequenceNumber | Text | Transaction ID | TXN001 |
| Hour_ID | Number | Hour (0-23) | 14 |

### Sample Data

See [sample_data/sample_sales.xlsx](sample_data/sample_sales.xlsx) for example.

## Security Checklist

- [ ] Service account has read-only access
- [ ] `service_account.json` is in .gitignore
- [ ] Never commit credentials to git
- [ ] GitHub repo is private (for production)
- [ ] Email whitelist enabled (Streamlit Cloud)
- [ ] Service account only shared with necessary folders

## Next Steps

1. ✅ **Customize**: Adapt categories and branding
2. ✅ **Test**: Load different date ranges
3. ✅ **Share**: Deploy and share with team
4. ✅ **Monitor**: Check usage and performance
5. ✅ **Iterate**: Add features based on feedback

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/yourusername/sales-dashboard/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/sales-dashboard/discussions)
- **Streamlit Docs**: [docs.streamlit.io](https://docs.streamlit.io)
- **Google Drive API**: [developers.google.com/drive](https://developers.google.com/drive)

---

**Setup complete!** 🎉

You now have a fully functional sales analytics dashboard!
