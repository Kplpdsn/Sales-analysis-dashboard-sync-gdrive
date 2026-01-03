# 🏗️ Architecture Documentation

## System Overview

The Sales Analytics Dashboard is a Streamlit-based web application that provides real-time business intelligence through automated data loading from Google Drive and interactive visualizations.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                           │
│                      (Web Browser)                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │  Daily View │  │ Weekly View │  │Monthly View │           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
│  ┌──────────────────────────────────────────────────┐          │
│  │         Period Comparison Mode                   │          │
│  └──────────────────────────────────────────────────┘          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   STREAMLIT APPLICATION                         │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐  │
│  │  Data Loader   │  │  Processor     │  │  Visualizer    │  │
│  │  Module        │  │  Module        │  │  Module        │  │
│  └────────┬───────┘  └────────┬───────┘  └────────┬───────┘  │
│           │                   │                    │           │
└───────────┼───────────────────┼────────────────────┼───────────┘
            │                   │                    │
            ▼                   ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Google Drive   │  │     Pandas      │  │     Plotly      │
│      API        │  │  Data Processing│  │  Visualization  │
└─────────────────┘  └─────────────────┘  └─────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   GOOGLE DRIVE STORAGE                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Sales Data Files (Excel)                                │  │
│  │  • ThreeMillsDailyIncrementalSales_20241215.xlsx        │  │
│  │  • ThreeMillsDailyIncrementalSales_20241216.xlsx        │  │
│  │  • ...                                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. User Interface Layer

**Technology**: Streamlit + HTML/CSS

**Components**:
- **Header**: Branding, title, navigation
- **Sidebar**: Filters (category, product), date selection
- **Main Content**: Dynamic based on selected view
- **Footer**: Credits and metadata

**Key Features**:
- Responsive layout
- Custom CSS styling
- Session state management
- Real-time updates

### 2. Application Layer

**Technology**: Python 3.9+, Streamlit 1.31.0

#### 2.1 Data Loader Module

**Purpose**: Fetch and load sales data from Google Drive

**Functions**:
```python
get_google_drive_service()
    → Authenticates with Google Drive API
    → Returns: service object or error

list_files_in_folder(service, folder_id, file_pattern)
    → Lists Excel files matching pattern
    → Returns: List of file metadata

download_file_from_drive(service, file_id)
    → Downloads file content
    → Returns: BytesIO buffer

process_gdrive_files(service, folder_id, start_date, end_date)
    → Main data loading function
    → Filters by date range
    → Combines multiple files
    → Returns: Pandas DataFrame
```

**Flow**:
1. User selects date range
2. System lists files in Google Drive folder
3. Filter files by date pattern (YYYYMMDD)
4. Download matching files
5. Parse Excel to DataFrame
6. Combine and return

#### 2.2 Data Processor Module

**Purpose**: Clean, transform, and aggregate data

**Functions**:
```python
extract_date_from_filename(filename)
    → Extracts date from filename pattern
    → Returns: datetime object

get_bakery_category(item)
    → Categorizes products
    → Returns: Category string

clean_product_name(name)
    → Removes prefixes, cleans text
    → Returns: Clean string
```

**Processing Pipeline**:
1. Extract dates from filenames
2. Clean product names
3. Categorize products
4. Add derived columns (Hour, DayName, etc.)
5. Handle missing values
6. Aggregate data

#### 2.3 Visualization Module

**Purpose**: Create interactive charts and displays

**Chart Types**:
- **Bar Charts**: Top products, comparisons
- **Line Charts**: Hourly patterns, trends
- **Donut Charts**: Category mix
- **Metric Cards**: KPIs

**Plotly Configuration**:
```python
# Example bar chart
go.Bar(
    x=data.index,
    y=data.values,
    marker_color='#7D8570',
    hovertemplate='<b>%{x}</b><br>$%{y:,.0f}<extra></extra>'
)
```

### 3. Data Storage Layer

**Technology**: Google Drive + Google Drive API v3

**Structure**:
```
Sales Data Folder/
├── ThreeMillsDailyIncrementalSales_20240529.xlsx
├── ThreeMillsDailyIncrementalSales_20240530.xlsx
├── ThreeMillsDailyIncrementalSales_20240531.xlsx
└── ... (one file per day)
```

**File Format**: Excel (.xlsx)

**Required Columns**:
- Date/TransactionDate
- Description
- Quantity
- ExtendedNetAmount
- SequenceNumber
- Hour_ID (optional)

## Data Flow

### 1. Initial Load

```
User Opens App
    ↓
Check for Service Account Credentials
    ↓
Display Welcome Screen or Date Picker
    ↓
User Selects Date Range
    ↓
User Clicks "Load Data"
    ↓
Query Google Drive API
    ↓
Filter Files by Date Pattern
    ↓
Download Matching Files
    ↓
Parse Excel Files
    ↓
Combine DataFrames
    ↓
Process & Clean Data
    ↓
Store in Session State
    ↓
Display Dashboard
```

### 2. View Selection

```
User Selects View (Daily/Weekly/Monthly)
    ↓
Filter Data by View Requirements
    ↓
Calculate View-Specific Metrics
    ↓
Generate Charts
    ↓
Render UI
```

### 3. Filter Application

```
User Changes Category/Product Filter
    ↓
Reload Data from Session State
    ↓
Apply Filters
    ↓
Recalculate Metrics
    ↓
Update Charts
    ↓
Re-render UI
```

### 4. Period Comparison

```
User Loads Period 1
    ↓
Store in session_state.comparison_period1
    ↓
User Loads Period 2
    ↓
Store in session_state.comparison_period2
    ↓
Calculate Deltas
    ↓
Generate Comparison Charts
    ↓
Display Side-by-Side
```

## State Management

**Streamlit Session State Variables**:

```python
st.session_state = {
    'folder_id': str,              # Google Drive folder ID
    'df': DataFrame,               # Current loaded data
    'comparison_period1': dict,    # Period 1 data + metadata
    'comparison_period2': dict,    # Period 2 data + metadata
    'preset_start': date,          # Quick select start
    'preset_end': date,            # Quick select end
}
```

**State Lifecycle**:
1. Initialize on app load
2. Persist across reruns
3. Update on user actions
4. Clear on date change

## Security Architecture

### Authentication Flow

```
App Startup
    ↓
Check for Service Account JSON
    ↓
    ├─ Local: Load from service_account.json
    └─ Cloud: Load from st.secrets
    ↓
Create Credentials Object
    ↓
Authenticate with Google Drive API
    ↓
Return Service Object (Read-Only)
```

### Access Control

**Layers**:
1. **Streamlit Cloud**: Email whitelist
2. **Google Drive**: Service account with Viewer role only
3. **Data**: Read-only, no write access

**Credentials Storage**:
- **Local Dev**: `service_account.json` (gitignored)
- **Production**: Streamlit Cloud Secrets (encrypted)

## Performance Optimization

### Caching Strategy

```python
@st.cache_data(ttl=3600)  # 1 hour cache
def load_data(folder_id, start_date, end_date):
    # Expensive operation cached
    return data
```

**Cached Operations**:
- Google Drive file listings
- Excel file parsing
- Data aggregations

### Data Loading

**Optimization Techniques**:
- Only load files in selected date range
- Download files in parallel (future enhancement)
- Parse only required columns
- Use efficient pandas operations

### UI Rendering

**Techniques**:
- Lazy load charts (only render visible view)
- Use plotly's built-in optimization
- Limit data points in charts
- Responsive container widths

## Scalability Considerations

### Current Limits

- **Files**: ~1000 files (daily for 3 years)
- **File Size**: Up to 10MB per file
- **Total Data**: ~100,000 rows per load
- **Concurrent Users**: 5-10 (Streamlit Cloud free tier)

### Scaling Strategies

**For More Data**:
1. Add database layer (PostgreSQL, MongoDB)
2. Implement data warehouse (BigQuery)
3. Use incremental loading
4. Add pagination

**For More Users**:
1. Upgrade Streamlit Cloud tier
2. Deploy on AWS/GCP with load balancer
3. Use Redis for caching
4. Implement CDN for static assets

## Error Handling

### Error Types

1. **Authentication Errors**: Service account issues
2. **Data Errors**: Missing files, corrupt data
3. **Processing Errors**: Invalid formats
4. **Display Errors**: Chart rendering issues

### Error Strategy

```python
try:
    data = load_data()
except AuthenticationError:
    st.error("❌ Could not authenticate with Google Drive")
except DataNotFoundError:
    st.warning("⚠️ No data found for selected dates")
except Exception as e:
    st.error(f"Error: {str(e)}")
```

## Deployment Architecture

### Streamlit Cloud

```
GitHub Repo (Private)
    ↓
Streamlit Cloud Monitors Repo
    ↓
Detects Changes on Push
    ↓
Pulls Latest Code
    ↓
Installs Dependencies (requirements.txt)
    ↓
Loads Secrets
    ↓
Starts Streamlit Server
    ↓
Exposes HTTPS Endpoint
```

### Alternative: Docker

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "sales_dashboard.py"]
```

## Monitoring & Logging

**Metrics to Monitor**:
- Page load time
- Data refresh frequency
- User active sessions
- Error rates
- API quota usage

**Logging**:
```python
import logging

logging.info(f"Loaded {len(df)} records")
logging.warning(f"Missing data for {date}")
logging.error(f"Failed to load file: {e}")
```

## Future Enhancements

### Planned Features

1. **Real-time Updates**: WebSocket connection to Drive
2. **Predictive Analytics**: ML-based forecasting
3. **Export Functionality**: PDF/Excel reports
4. **User Accounts**: Multi-tenant support
5. **Custom Alerts**: Email/Slack notifications
6. **Mobile App**: React Native companion

### Technical Debt

- Add comprehensive unit tests
- Implement CI/CD pipeline
- Add API documentation
- Improve error messages
- Add data validation layer

## Technology Stack Summary

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Frontend | Streamlit | 1.31.0 | Web UI framework |
| Charts | Plotly | 5.18.0 | Interactive visualizations |
| Data | Pandas | 2.1.4 | Data processing |
| API | Google Drive API | v3 | Cloud storage access |
| Auth | google-auth | 2.27.0 | Authentication |
| Language | Python | 3.9+ | Application logic |
| Deployment | Streamlit Cloud | - | Hosting |

## API Reference

See [API.md](API.md) for detailed function documentation.

---

**Last Updated**: 2026-01-03  
**Version**: 1.0.0  
**Author**: KAz
