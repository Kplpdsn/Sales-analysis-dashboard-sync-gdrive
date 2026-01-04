# 📊 Sales Analytics Dashboard

A professional, production-ready sales analytics dashboard built with Streamlit and Google Drive integration. Perfect for retail stores, bakeries, cafes, restaurants, or any business that tracks sales data.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31.0-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Features

### 📈 Multi-View Analysis
- **Daily View**: Hourly sales patterns (8 AM - 10 PM)
- **Weekly View**: Day-by-day breakdown with trends
- **Monthly View**: Week-by-week performance tracking

### 🔄 Interactive Controls
- Toggle between Revenue and Quantity metrics
- Filter by product category or specific product
- Compare any two time periods side-by-side

### 🚀 Smart Automation
- Automatic data loading from Google Drive
- Intelligent product categorization
- Real-time chart updates
- Clean, professional UI

### 📊 Advanced Analytics
- Top performing products
- Category performance breakdowns
- Rank change indicators in comparisons
- Sales pattern analysis

## 🎯 Perfect For

- ✅ Retail stores
- ✅ Bakeries & cafes
- ✅ Restaurants
- ✅ E-commerce businesses
- ✅ Any transaction-based business

## 🏗️ Architecture

```
┌─────────────────┐
│  Google Drive   │
│  (Sales Files)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Service Acct   │
│  (Read Only)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Streamlit     │
│   Dashboard     │
├─────────────────┤
│  • Data Load    │
│  • Processing   │
│  • Viz (Plotly) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Web Browser   │
│  (User Access)  │
└─────────────────┘
```

**Tech Stack:**
- **Frontend**: Streamlit (Python web framework)
- **Charts**: Plotly (interactive visualizations)
- **Data Processing**: Pandas
- **Cloud Storage**: Google Drive API
- **Deployment**: Streamlit Cloud (or any Python host)

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- Google Cloud account (free tier works!)
- Google Drive with sales data

### Installation

1. **Clone the repository**
```bash
https://github.com/Kplpdsn/Sales-analysis-dashboard-sync-gdrive
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up Google Drive API**

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed instructions on:
- Creating a Google Cloud project
- Enabling Drive API
- Creating a service account
- Downloading credentials

4. **Configure the app**

Edit `sales_dashboard.py` line 483:
```python
SALES_FOLDER_ID = "YOUR_GOOGLE_DRIVE_FOLDER_ID_HERE"
```

5. **Add credentials**

Place your `service_account.json` in the project root (it's in .gitignore)

6. **Run the app**
```bash
streamlit run sales_dashboard.py
```

7. **Open in browser**

Navigate to `http://localhost:8501`

## 📊 Data Format

Your sales data should be Excel files (.xlsx) with these columns:

| Column | Description | Example |
|--------|-------------|---------|
| `Date` or `TransactionDate` | Sale date | 2024-12-15 |
| `Description` | Product name | House Sourdough |
| `Quantity` | Units sold | 5 |
| `ExtendedNetAmount` | Revenue | 45.50 |
| `SequenceNumber` | Transaction ID | TXN001 |
| `Hour_ID` | Hour of day (optional) | 14 |

**Sample Data:**

See [sample_data/sample_sales.xlsx](sample_data/sample_sales.xlsx)

## 🎨 Customization

### Change Branding

Edit the header section (lines 465-475):
```python
st.markdown("""
<div class="main-header">
    <h1 class="main-title">🏪 Your Business Name</h1>
    <p class="main-subtitle">YOUR TAGLINE</p>
</div>
""", unsafe_allow_html=True)
```

### Modify Product Categories

Edit the `get_bakery_category()` function (lines 290-325):
```python
def get_product_category(item):
    """Categorize products based on your business logic"""
    item = str(item).upper().strip()
    
    # Add your categories here
    if "KEYWORD1" in item: return "Category A"
    if "KEYWORD2" in item: return "Category B"
    # ... etc
```

### Change Color Scheme

Colors are defined in the CSS (lines 21-230). Main colors:
- Primary: `#7D8570` (olive/khaki)
- Accent: `#10b981` (green)
- Text: `#5A6B5E` (dark olive)

### Add New Metrics

Add custom calculations in each view section:
```python
# Example: Add profit margin metric
profit_margin = (revenue - cost) / revenue * 100
st.metric("💰 Profit Margin", f"{profit_margin:.1f}%")
```

## 🔒 Security Best Practices

### Local Development
- ✅ Use `service_account.json` (in .gitignore)
- ✅ Never commit credentials
- ✅ Use read-only service account

### Production Deployment (Streamlit Cloud)
- ✅ Store credentials in Streamlit Secrets
- ✅ Enable email whitelist
- ✅ Use private GitHub repo
- ✅ Monitor access logs

### Service Account Permissions
- ✅ Grant only "Viewer" access to Drive folder
- ✅ Don't use personal account
- ✅ Rotate credentials periodically

## 📦 Deployment

### Deploy to Streamlit Cloud

1. Push code to GitHub (private or public repo)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Select `sales_dashboard.py` as main file
5. Add secrets in "Advanced settings":

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project"
private_key_id = "key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "service-account@project.iam.gserviceaccount.com"
client_id = "123456789"
# ... rest of service account JSON
```

6. Click Deploy!

### Other Deployment Options

- **Heroku**: See [DEPLOY_HEROKU.md](docs/DEPLOY_HEROKU.md)
- **AWS EC2**: See [DEPLOY_AWS.md](docs/DEPLOY_AWS.md)
- **Docker**: See [DEPLOY_DOCKER.md](docs/DEPLOY_DOCKER.md)

## 📸 Screenshots

### Daily View
*Hourly sales patterns with product breakdowns*

### Weekly View
*Day-by-day analysis with top performers*

### Monthly View
*Week-by-week trends and insights*

### Comparison Mode
*Side-by-side period comparison*

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/sales-analytics-dashboard.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black sales_dashboard.py

# Lint
flake8 sales_dashboard.py
```

## 📝 Changelog

### Version 1.0.0 (2026-01-03)
- Initial public release
- Daily, Weekly, Monthly views
- Period comparison
- Google Drive integration
- Interactive toggles
- Clean minimal UI

## 🐛 Troubleshooting

### "No credentials found"
- Ensure `service_account.json` is in project root
- Check file permissions
- Verify JSON is valid

### "No data found"
- Confirm Drive folder is shared with service account email
- Check folder ID is correct
- Verify date range includes available data

### Charts not loading
- Check browser console for errors
- Verify all dependencies installed
- Clear browser cache

See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for more solutions.

## 📚 Documentation

- [Setup Guide](SETUP_GUIDE.md) - Detailed setup instructions
- [Architecture](ARCHITECTURE.md) - System design and data flow
- [API Reference](docs/API.md) - Function documentation
- [Customization Guide](docs/CUSTOMIZATION.md) - How to adapt for your needs

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2026 KAz

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software...
```

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Charts powered by [Plotly](https://plotly.com/)
- Icons from [Emoji](https://emojipedia.org/)
- Inspired by real-world business needs

## 💡 About

Originally created for TMB Harris Farm retail analytics, now open-sourced to help the community build better business intelligence tools.

**Built by**: KAz  
**Contact**: [Your GitHub Profile]

## ⭐ Support

If this project helped you, please consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs
- 💡 Suggesting new features
- 🤝 Contributing code

---

**Made with ❤️ for the business analytics community**
