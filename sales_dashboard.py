import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import re
from io import BytesIO
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# --- PAGE CONFIG ---
st.set_page_config(page_title="Three Mills Analytics Pro", layout="wide", page_icon="🥖")

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    /* Your Business Brand Colors - Khaki/Olive Palette - Enhanced Saturation */
    :root {
        --tmb-cream: #F5F2ED;
        --tmb-khaki: #A58A6F;
        --tmb-sage: #B5C99A;
        --tmb-olive: #7D8570;
        --tmb-light: #FAF9F6;
        --tmb-gold: #E0B589;
        --tmb-darkgreen: #5A6B5E;
        --tmb-green: #10b981;
        --tmb-red: #ef4444;
    }
    
    /* Main Background */
    .stApp { 
        background: linear-gradient(135deg, #FAF9F6 0%, #F0EDE6 100%);
    }
    
    /* Header Styling */
    .main-header {
        background: linear-gradient(135deg, #6B705C 0%, #8B7355 100%);
        padding: 30px 40px;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(107, 112, 92, 0.2);
    }
    
    .main-title {
        font-size: 48px;
        font-weight: 900;
        color: #FAF9F6;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        font-family: 'Georgia', serif;
    }
    
    .main-subtitle {
        font-size: 18px;
        color: #D4A574;
        margin: 5px 0 0 0;
        font-weight: 300;
        letter-spacing: 2px;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] { 
        font-size: 32px; 
        color: #495650; 
        font-weight: 800;
        font-family: 'Georgia', serif;
    }
    
    [data-testid="stMetricLabel"] { 
        font-size: 13px; 
        color: #6B705C; 
        text-transform: uppercase; 
        letter-spacing: 1.5px;
        font-weight: 600;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #9DAB86 0%, #6B705C 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(107, 112, 92, 0.2);
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #6B705C 0%, #495650 100%);
        box-shadow: 0 4px 12px rgba(73, 86, 80, 0.3);
        transform: translateY(-2px);
    }
    
    /* Section Headers */
    h2, h3 {
        color: #495650;
        font-family: 'Georgia', serif;
        font-weight: 700;
    }
    
    /* Cards/Containers */
    div[data-testid="stHorizontalBlock"] { 
        gap: 1.5rem; 
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #8B9A7A 0%, #A4B494 100%);
    }
    
    /* Sidebar text - white for labels */
    [data-testid="stSidebar"] > div:first-child {
        color: #FFFFFF;
    }
    
    [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #FFFFFF !important;
    }
    
    /* Input boxes and select boxes - BLACK text on WHITE background */
    [data-testid="stSidebar"] input {
        color: #000000 !important;
        background-color: #FFFFFF !important;
    }
    
    [data-testid="stSidebar"] .st-emotion-cache-16txtl3 {
        color: #000000 !important;
    }
    
    [data-testid="stSidebar"] [data-baseweb="select"] {
        color: #000000 !important;
    }
    
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        color: #000000 !important;
        background-color: #FFFFFF !important;
    }
    
    /* Info boxes */
    .stInfo {
        background-color: rgba(157, 171, 134, 0.15);
        border-left: 4px solid #9DAB86;
    }
    
    /* Success messages */
    .stSuccess {
        background-color: rgba(157, 171, 134, 0.15);
        border-left: 4px solid #9DAB86;
    }
    
    /* Metric deltas */
    .metric-delta-positive { color: #10b981 !important; }
    .metric-delta-negative { color: #ef4444 !important; }
    
    /* Delta arrows with better visibility */
    [data-testid="stMetricDelta"] svg {
        fill: currentColor;
    }
    
    [data-testid="stMetricDelta"][data-trend="positive"] {
        color: #10b981 !important;
    }
    
    [data-testid="stMetricDelta"][data-trend="negative"] {
        color: #ef4444 !important;
    }
    
    /* Selectbox and inputs */
    .stSelectbox, .stDateInput {
        border-radius: 8px;
    }
    
    /* Dividers */
    hr {
        border-color: rgba(107, 112, 92, 0.15);
    }
    
    /* Download button special styling */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #D4A574 0%, #C4A77D 100%);
        color: #495650;
        font-weight: 700;
    }
    
    .stDownloadButton>button:hover {
        background: linear-gradient(135deg, #C4A77D 0%, #9DAB86 100%);
        color: white;
    }
    
    /* Breadcrumb/Caption styling */
    .stCaption {
        color: #6B705C !important;
        font-style: italic;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GOOGLE DRIVE SERVICE ACCOUNT SETUP ---
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def get_google_drive_service():
    """Get authenticated Google Drive service using Streamlit secrets or local file"""
    try:
        # Try Streamlit secrets first (for deployment)
        try:
            if hasattr(st, 'secrets') and "gcp_service_account" in st.secrets:
                credentials = service_account.Credentials.from_service_account_info(
                    st.secrets["gcp_service_account"],
                    scopes=SCOPES
                )
                service = build('drive', 'v3', credentials=credentials)
                return service, None
        except:
            pass  # Secrets not available, try local file
        
        # Fallback to local file (for development)
        creds_file = 'service_account.json'
        if os.path.exists(creds_file):
            credentials = service_account.Credentials.from_service_account_file(
                creds_file, scopes=SCOPES)
            service = build('drive', 'v3', credentials=credentials)
            return service, None
        
        return None, "⚠️ No credentials found. Add 'service_account.json' to your app folder (D:\\Bakery_App\\)"
        
    except Exception as e:
        return None, f"Error connecting to Google Drive: {str(e)}"

def list_files_in_folder(service, folder_id, file_pattern=None):
    """List all Excel files in a Google Drive folder"""
    try:
        query = f"'{folder_id}' in parents and (mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or mimeType='application/vnd.ms-excel') and trashed=false"
        
        results = service.files().list(
            q=query,
            fields="files(id, name, createdTime, modifiedTime)",
            pageSize=1000,
            orderBy='name'
        ).execute()
        
        files = results.get('files', [])
        
        # Filter by pattern if provided
        if file_pattern:
            files = [f for f in files if re.search(file_pattern, f['name'])]
        
        return files
    except Exception as e:
        st.error(f"Error listing files: {str(e)}")
        return []

def download_file_from_drive(service, file_id):
    """Download a file from Google Drive"""
    try:
        request = service.files().get_media(fileId=file_id)
        file_buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(file_buffer, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
        
        file_buffer.seek(0)
        return file_buffer
    except Exception as e:
        st.error(f"Error downloading file: {str(e)}")
        return None

# --- HELPER FUNCTIONS ---
def extract_date_from_filename(filename):
    """Extract date from filename"""
    match = re.search(r'(\d{8})', filename)
    if match:
        try:
            return pd.to_datetime(match.group(1), format='%Y%m%d')
        except:
            return None
    return None

def get_bakery_category(item):
    """Categorize bakery items"""
    item = str(item).upper().strip()
    if not item or item in ["NAN", "BLANK"]: return "Ignore"
    
    # Bake at Home - check for BAH items first (must be before ESCARGOT check)
    if "BAKE AT HOME" in item or "BAH" in item or "S/ROLL" in item or "CHEESY VEG" in item or "SHARE PIE" in item: 
        return "Bake at Home"
    
    # Weekend Special
    if "STOLLEN" in item or "SALT & PEPPER BAGUETTE" in item or "SALT AND PEPPER BAGUETTE" in item: 
        return "Weekend Special"
    
    # XL Loaves vs Standard Loaves
    if any(x in item for x in ["SOURDOUGH", "BATARD", "BAGUETTE", "S/DOUGH"]): 
        return "XL Loaves" if "XL" in item else "Standard Loaves"
    
    # Pastries - including plain ESCARGOT (not BAH ESCARGOT which was caught above)
    if any(x in item for x in ["DANISH", "CROISSANT", "SCROLL", "PASTRY", "ESCARGOT"]): 
        return "Pastries"
    
    # FMT
    if any(x in item for x in ["FMT", "GINGER SNAP", "TART"]): 
        return "FMT"
    
    # Retail Items
    if any(x in item for x in ["COOKIE", "GRANOLA", "COFFEE", "REDBRICK", "HONEY", "BEYOND BREAD", "BAKERS OVEN"]) or "B&B" in item: 
        return "Retail Items"
    
    # Buns & Rolls
    if any(x in item for x in ["BUN", "ROLL"]): 
        return "Buns & Rolls"
    
    return "Other"

def clean_product_name(name):
    """Remove TMB prefix"""
    name = str(name).strip()
    if name.upper().startswith('TMB '):
        name = name[4:]
    return name.strip()

def process_gdrive_files(service, folder_id, start_date=None, end_date=None):
    """Process files from Google Drive within date range"""
    
    # List files
    files = list_files_in_folder(service, folder_id, file_pattern=r'\d{8}')
    
    if not files:
        return pd.DataFrame(), "No files found in the folder"
    
    # Filter by date range if provided
    if start_date or end_date:
        filtered_files = []
        for file in files:
            file_date = extract_date_from_filename(file['name'])
            if file_date:
                if start_date and file_date < start_date:
                    continue
                if end_date and file_date > end_date:
                    continue
                filtered_files.append(file)
        files = filtered_files
    
    if not files:
        return pd.DataFrame(), "No files found in the selected date range"
    
    # Download and process files
    all_data = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, file in enumerate(files):
        status_text.text(f"Loading {file['name']}... ({idx+1}/{len(files)})")
        
        file_buffer = download_file_from_drive(service, file['id'])
        if file_buffer:
            try:
                df = pd.read_excel(file_buffer)
                file_date = extract_date_from_filename(file['name'])
                if file_date:
                    df['FileDate'] = file_date
                
                if 'Saledate' in df.columns:
                    df['Date'] = pd.to_datetime(df['Saledate'])
                elif file_date:
                    df['Date'] = file_date
                else:
                    df['Date'] = pd.NaT
                
                all_data.append(df)
            except Exception as e:
                st.warning(f"Could not process {file['name']}: {str(e)}")
        
        progress_bar.progress((idx + 1) / len(files))
    
    progress_bar.empty()
    status_text.empty()
    
    if not all_data:
        return pd.DataFrame(), "Could not process any files"
    
    # Combine and clean
    combined_df = pd.concat(all_data, ignore_index=True)
    combined_df = combined_df[combined_df['Description'].notna()]
    combined_df['Description'] = combined_df['Description'].apply(clean_product_name)
    combined_df['Revenue'] = pd.to_numeric(combined_df['ExtendedNetAmount'], errors='coerce').fillna(0)
    combined_df['Quantity'] = pd.to_numeric(combined_df['Quantity'], errors='coerce').fillna(0)
    combined_df['Category'] = combined_df['Description'].apply(get_bakery_category)
    combined_df = combined_df[combined_df['Category'] != "Ignore"]
    combined_df['Hour'] = pd.to_numeric(combined_df['Hour_ID'], errors='coerce').fillna(0).astype(int)
    
    # Add time periods
    combined_df['Week'] = combined_df['Date'].dt.isocalendar().week
    combined_df['Month'] = combined_df['Date'].dt.month
    combined_df['Year'] = combined_df['Date'].dt.year
    combined_df['WeekYear'] = combined_df['Year'].astype(str) + '-W' + combined_df['Week'].astype(str).str.zfill(2)
    combined_df['MonthYear'] = combined_df['Date'].dt.strftime('%Y-%m')
    combined_df['DayName'] = combined_df['Date'].dt.day_name()
    
    return combined_df, None

def process_files(uploaded_files):
    """Process manually uploaded files (fallback)"""
    if not uploaded_files:
        return pd.DataFrame()
    
    all_data = []
    
    for file in uploaded_files:
        try:
            if file.name.endswith('.csv'):
                df = pd.read_csv(file, encoding='cp1252')
            else:
                df = pd.read_excel(file)
            
            file_date = extract_date_from_filename(file.name)
            if file_date:
                df['FileDate'] = file_date
            
            if 'Saledate' in df.columns:
                df['Date'] = pd.to_datetime(df['Saledate'])
            elif file_date:
                df['Date'] = file_date
            else:
                df['Date'] = pd.NaT
            
            all_data.append(df)
            
        except Exception as e:
            st.warning(f"⚠️ Could not process {file.name}: {str(e)}")
            continue
    
    if not all_data:
        return pd.DataFrame()
    
    combined_df = pd.concat(all_data, ignore_index=True)
    combined_df = combined_df[combined_df['Description'].notna()]
    combined_df['Description'] = combined_df['Description'].apply(clean_product_name)
    combined_df['Revenue'] = pd.to_numeric(combined_df['ExtendedNetAmount'], errors='coerce').fillna(0)
    combined_df['Quantity'] = pd.to_numeric(combined_df['Quantity'], errors='coerce').fillna(0)
    combined_df['Category'] = combined_df['Description'].apply(get_bakery_category)
    combined_df = combined_df[combined_df['Category'] != "Ignore"]
    combined_df['Hour'] = pd.to_numeric(combined_df['Hour_ID'], errors='coerce').fillna(0).astype(int)
    
    combined_df['Week'] = combined_df['Date'].dt.isocalendar().week
    combined_df['Month'] = combined_df['Date'].dt.month
    combined_df['Year'] = combined_df['Date'].dt.year
    combined_df['WeekYear'] = combined_df['Year'].astype(str) + '-W' + combined_df['Week'].astype(str).str.zfill(2)
    combined_df['MonthYear'] = combined_df['Date'].dt.strftime('%Y-%m')
    combined_df['DayName'] = combined_df['Date'].dt.day_name()
    
    return combined_df

# --- MAIN APP ---
st.markdown("""
<div class="main-header">
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <div>
            <h1 class="main-title">🌾 Your Business</h1>
            <p class="main-subtitle">SALES ANALYTICS DASHBOARD</p>
        </div>
        <div style="font-size: 80px; opacity: 0.3;">🥖</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR: DATA SOURCE ---
st.sidebar.header("📁 Data Source")

# Hardcoded Google Drive Folder ID for Your Business Sales Data
SALES_FOLDER_ID = "YOUR_GOOGLE_DRIVE_FOLDER_ID_HERE"

# Check for service account
service, error = get_google_drive_service()

if service:
    st.sidebar.success("✅ Google Drive Connected")
    
    # Use hardcoded folder ID
    st.session_state.folder_id = TMB_SALES_FOLDER_ID
    
    # Show folder location (read-only info)
    st.sidebar.info(f"📂 Data Folder: `{TMB_SALES_FOLDER_ID[:15]}...`")

else:
    # Service account not found
    st.sidebar.error("❌ Google Drive Not Connected")
    st.sidebar.markdown(error)
    
    with st.sidebar.expander("📖 How to set up"):
        st.markdown("""
        **Quick Setup (5 minutes):**
        
        1. Go to [Google Cloud Console](https://console.cloud.google.com/)
        2. Create a project
        3. Enable Google Drive API
        4. Create Service Account
        5. Download JSON key
        6. Rename it to `service_account.json`
        7. Put it in your app folder (same folder as this script)
        8. Share your Drive folder with the service account email
        
        **Need detailed instructions?** Check the setup guide!
        """)

# Manual upload fallback
st.sidebar.markdown("---")
st.sidebar.subheader("Or Upload Manually")
uploaded_files = st.sidebar.file_uploader(
    "📤 Upload Sales Files",
    accept_multiple_files=True,
    type=['csv', 'xlsx', 'xls'],
    help="Drag and drop or browse"
)

if uploaded_files:
    with st.spinner("Processing uploaded files..."):
        df = process_files(uploaded_files)
        if not df.empty:
            st.session_state.df = df
            st.session_state.data_loaded = True
            st.success(f"✅ Loaded {len(df):,} records")
            st.rerun()

# --- MAIN ANALYSIS ---
if 'df' in st.session_state and not st.session_state.df.empty:
    df = st.session_state.df
    
    # Calculate date range
    min_date = df['Date'].min()
    max_date = df['Date'].max()
    days_span = (max_date - min_date).days + 1
    
    # Prominent date range display at top with change button
    st.markdown(f"""
    <div style='background: linear-gradient(90deg, #7D8570 0%, #B5C99A 100%); 
                padding: 20px 30px; border-radius: 12px; margin-bottom: 25px;
                box-shadow: 0 4px 15px rgba(125, 133, 112, 0.25);'>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div>
                <h3 style='color: white; margin: 0; font-family: Georgia, serif; font-size: 24px;'>
                    📅 {min_date.strftime('%B %d, %Y')} — {max_date.strftime('%B %d, %Y')}
                </h3>
                <p style='color: #FAF9F6; margin: 5px 0 0 0; opacity: 0.95; font-size: 14px;'>
                    {days_span} day{'s' if days_span != 1 else ''} of data loaded
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Change Date Range button
    if st.button("🔄 Change Date Range", type="secondary", use_container_width=False):
        del st.session_state.df
        if 'data_loaded' in st.session_state:
            del st.session_state.data_loaded
        st.rerun()
    
    # Data info in sidebar
    st.sidebar.markdown("---")
    st.sidebar.metric("📊 Data Range", f"{min_date.strftime('%b %d')} - {max_date.strftime('%b %d')}")
    st.sidebar.metric("📝 Records", f"{len(df):,}")
    st.sidebar.metric("🗓️ Days", f"{days_span}")
    
    # Determine analysis mode based on days
    if days_span == 1:
        analysis_mode = "Daily"
    elif days_span <= 14:
        analysis_mode = "Weekly"
    else:
        analysis_mode = "Monthly"
    
    # Show mode indicator
    mode_emoji = {"Daily": "📆", "Weekly": "📊", "Monthly": "📑"}
    st.markdown(f"## {mode_emoji[analysis_mode]} {analysis_mode} Analysis")
    st.caption(f"Showing {analysis_mode.lower()} view for {days_span} day{'s' if days_span != 1 else ''} of data")
    
    # Category & Product Filters (Always shown)
    st.markdown("---")
    st.subheader("🔍 Quick Filters")
    filter_col1, filter_col2 = st.columns(2)
    
    with filter_col1:
        selected_category = st.selectbox(
            "📁 Filter by Category",
            options=["All Categories"] + sorted(df['Category'].unique()),
            index=0,
            key="main_category_filter"
        )
    
    with filter_col2:
        if selected_category != "All Categories":
            available_products = sorted(df[df['Category'] == selected_category]['Description'].unique())
        else:
            available_products = sorted(df['Description'].unique())
        
        selected_product = st.selectbox(
            "🏷️ Filter by Product",
            options=["All Products"] + available_products,
            index=0,
            key="main_product_filter"
        )
    
    # Apply filters
    filtered_df = df.copy()
    if selected_category != "All Categories":
        filtered_df = filtered_df[filtered_df['Category'] == selected_category]
    if selected_product != "All Products":
        filtered_df = filtered_df[filtered_df['Description'] == selected_product]
    
    # Show filtered metrics if filters applied
    if selected_category != "All Categories" or selected_product != "All Products":
        st.markdown("#### 📊 Filtered Results")
        fcol1, fcol2, fcol3 = st.columns(3)
        with fcol1:
            st.metric("Revenue", f"${filtered_df['Revenue'].sum():,.2f}")
        with fcol2:
            st.metric("Units", f"{int(filtered_df['Quantity'].sum()):,}")
        with fcol3:
            favg = filtered_df['Revenue'].sum() / filtered_df['Quantity'].sum() if filtered_df['Quantity'].sum() > 0 else 0
            st.metric("Avg Price", f"${favg:.2f}")
    
    st.markdown("---")
    
    # ==== DAILY VIEW (1 day) ====
    if analysis_mode == "Daily":
        # Show date in header
        st.caption(f"**Date:** {min_date.strftime('%A, %B %d, %Y')}")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 Revenue", f"${filtered_df['Revenue'].sum():,.2f}")
        with col2:
            st.metric("📦 Units Sold", f"{int(filtered_df['Quantity'].sum()):,}")
        with col3:
            avg_price = filtered_df['Revenue'].sum() / filtered_df['Quantity'].sum() if filtered_df['Quantity'].sum() > 0 else 0
            st.metric("💵 Avg Price", f"${avg_price:.2f}")
        with col4:
            st.metric("🛍️ Transactions", f"{int(filtered_df['SequenceNumber'].nunique()):,}")
        
        st.markdown("---")
        
        # Hourly Sales Pattern with Toggle
        st.subheader("📈 Hourly Sales Pattern")
        
        # Toggle between Revenue and Quantity at top right
        hourly_view_col1, hourly_view_col2 = st.columns([3, 1])
        with hourly_view_col2:
            hourly_metric = st.radio(
                "View:",
                ["Revenue ($)", "Quantity"],
                horizontal=True,
                key="daily_hourly_toggle",
                label_visibility="visible"
            )
        
        # Get hourly data
        hourly_data = filtered_df.groupby('Hour').agg({
            'Revenue': 'sum',
            'Quantity': 'sum'
        }).reset_index()
        
        # Filter to business hours (8 AM - 10 PM)
        hourly_data = hourly_data[(hourly_data['Hour'] >= 8) & (hourly_data['Hour'] <= 22)]
        
        # Create chart based on toggle
        fig = go.Figure()
        
        if hourly_metric == "Revenue ($)":
            y_data = hourly_data['Revenue']
            y_title = 'Revenue ($)'
            hover_template = 'Hour: %{x}<br>Revenue: $%{y:,.0f}<extra></extra>'
            color = '#10b981'
        else:  # Quantity
            y_data = hourly_data['Quantity']
            y_title = 'Quantity'
            hover_template = 'Hour: %{x}<br>Quantity: %{y:,.0f}<extra></extra>'
            color = '#7D8570'
        
        # Add line chart with gradient fill
        fig.add_trace(go.Scatter(
            x=hourly_data['Hour'],
            y=y_data,
            mode='lines+markers',
            line=dict(color=color, width=3),
            marker=dict(size=6, color=color),
            fill='tozeroy',
            fillcolor=f'rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.2)',
            hovertemplate=hover_template
        ))
        
        fig.update_layout(
            height=350,
            margin=dict(l=0, r=0, t=20, b=40),
            xaxis=dict(
                title='Hour of Day',
                tickmode='linear',
                tick0=8,
                dtick=2,
                showgrid=True,
                gridcolor='rgba(0,0,0,0.05)'
            ),
            yaxis=dict(
                title=y_title,
                tickformat=',.0f' if hourly_metric == "Quantity" else '$,.0f',
                showgrid=True,
                gridcolor='rgba(0,0,0,0.05)'
            ),
            plot_bgcolor='white',
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Charts
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("🏆 Top Products")
            if selected_category != "All Categories":
                st.caption(f"Top products in: **{selected_category}**")
            
            # Get top 7 products (reduced from 10 for less clutter)
            top_products_data = filtered_df.groupby('Description').agg({
                'Revenue': 'sum',
                'Quantity': 'sum'
            }).sort_values('Revenue', ascending=True).tail(7)
            
            fig = go.Figure()
            
            # Add revenue bars with units shown in hover only
            fig.add_trace(go.Bar(
                y=top_products_data.index,
                x=top_products_data['Revenue'],
                orientation='h',
                marker_color='#7D8570',
                text=[f"${rev:,.0f}" for rev in top_products_data['Revenue']],
                textposition='outside',
                textfont=dict(size=11, color='#5A6B5E'),
                name='Revenue',
                hovertemplate='<b>%{y}</b><br>$%{x:,.0f} • %{customdata} units<extra></extra>',
                customdata=top_products_data['Quantity'].astype(int)
            ))
            
            fig.update_layout(
                showlegend=False, 
                height=400, 
                margin=dict(l=0, r=80, t=40, b=0),  # Increased top margin from 20 to 40
                xaxis=dict(title='Revenue ($)', tickformat='$,.0f'),
                yaxis=dict(title='')
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col_right:
            st.subheader("🥧 Category Mix")
            if selected_category != "All Categories":
                st.caption(f"Product mix within: **{selected_category}**")
                product_data = filtered_df.groupby('Description')['Revenue'].sum().sort_values(ascending=False)
                
                # Show top 6 with legend
                top_6 = product_data.nlargest(6)
                other = product_data[~product_data.index.isin(top_6.index)].sum()
                if other > 0:
                    plot_data = pd.concat([top_6, pd.Series({'Others': other})])
                else:
                    plot_data = top_6
                
                fig = go.Figure(data=[go.Pie(
                    labels=plot_data.index,
                    values=plot_data.values,
                    hole=0.5,
                    marker=dict(colors=px.colors.qualitative.Pastel),
                    texttemplate='%{percent}',
                    textposition='inside',
                    textfont=dict(size=11, color='white'),
                    hovertemplate='<b>%{label}</b><br>$%{value:,.0f} • %{percent}<extra></extra>'
                )])
                fig.update_layout(
                    height=450, 
                    margin=dict(l=20, r=20, t=20, b=20), 
                    showlegend=True,
                    legend=dict(
                        orientation='v',
                        yanchor='middle',
                        y=0.5,
                        xanchor='left',
                        x=1.05,
                        font=dict(size=9)
                    )
                )
            else:
                cat_data = filtered_df.groupby('Category')['Revenue'].sum().sort_values(ascending=False)
                fig = go.Figure(data=[go.Pie(
                    labels=cat_data.index,
                    values=cat_data.values,
                    hole=0.5,
                    marker=dict(colors=px.colors.qualitative.Pastel),
                    texttemplate='%{percent}',
                    textposition='inside',
                    textfont=dict(size=11, color='white'),
                    hovertemplate='<b>%{label}</b><br>$%{value:,.0f} • %{percent}<extra></extra>'
                )])
                fig.update_layout(
                    height=450, 
                    margin=dict(l=20, r=20, t=20, b=20), 
                    showlegend=True,
                    legend=dict(
                        orientation='v',
                        yanchor='middle',
                        y=0.5,
                        xanchor='left',
                        x=1.05,
                        font=dict(size=10)
                    )
                )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # ==== WEEKLY VIEW (2-14 days) ====
    elif analysis_mode == "Weekly":
        # Show date range in header
        st.caption(f"**Period:** {min_date.strftime('%A, %B %d, %Y')} to {max_date.strftime('%A, %B %d, %Y')}")
        
        # Key metrics without sparklines
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 Total Revenue", f"${filtered_df['Revenue'].sum():,.2f}")
        with col2:
            st.metric("📦 Total Units", f"{int(filtered_df['Quantity'].sum()):,}")
        with col3:
            avg_daily = filtered_df.groupby('Date')['Revenue'].sum().mean()
            st.metric("📊 Avg Daily Rev", f"${avg_daily:,.2f}")
        with col4:
            st.metric("📅 Days Active", f"{filtered_df['Date'].nunique()}")
        
        st.markdown("---")
        
        # Daily breakdown with toggle
        daily_view_col1, daily_view_col2 = st.columns([3, 1])
        with daily_view_col1:
            st.subheader("📅 Day-by-Day Breakdown")
        with daily_view_col2:
            daily_metric = st.radio(
                "View:",
                ["Revenue ($)", "Quantity"],
                horizontal=True,
                key="weekly_daily_toggle"
            )
        
        daily_data = filtered_df.groupby('Date').agg({
            'Revenue': 'sum',
            'Quantity': 'sum'
        }).reset_index()
        daily_data['DayName'] = daily_data['Date'].dt.day_name()
        # Add date + day name for x-axis labels
        daily_data['DateLabel'] = daily_data['Date'].dt.strftime('%b %d') + ' (' + daily_data['DayName'] + ')'
        
        # Choose data based on toggle
        if daily_metric == "Revenue ($)":
            y_data = daily_data['Revenue']
            y_title = 'Revenue ($)'
            hover_template = '<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>'
            color = '#10b981'
            tick_format = '$,.0f'
        else:  # Quantity
            y_data = daily_data['Quantity']
            y_title = 'Quantity'
            hover_template = '<b>%{x}</b><br>Quantity: %{y:,.0f}<extra></extra>'
            color = '#7D8570'
            tick_format = ',.0f'
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=daily_data['DateLabel'],
            y=y_data,
            name=daily_metric,
            marker_color=color,
            hovertemplate=hover_template
        ))
        fig.update_layout(
            height=400,
            margin=dict(l=0, r=0, t=20, b=0),
            xaxis_title="Date",
            yaxis_title=y_title,  # Use dynamic title based on toggle
            yaxis=dict(tickformat=tick_format),
            xaxis=dict(tickangle=-45),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Two columns for additional analysis
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("🏆 Top Performers")
            top_items = filtered_df.groupby('Description').agg({
                'Revenue': 'sum',
                'Quantity': 'sum'
            }).sort_values('Revenue', ascending=False).head(5)  # Reduced to 5 for less overlap
            
            # Add rank badges
            rank_badges = {1: "🥇", 2: "🥈", 3: "🥉"}
            labels_with_rank = []
            for i, (prod, rev, qty) in enumerate(zip(top_items.index, top_items['Revenue'], top_items['Quantity'])):
                rank = i + 1
                badge = rank_badges.get(rank, f"#{rank}")
                # Shorten long product names
                short_prod = prod if len(prod) <= 25 else prod[:22] + "..."
                labels_with_rank.append(f"{badge} {short_prod}")
            
            fig = go.Figure()
            
            # Revenue bars with units in hover (no overlay dots)
            fig.add_trace(go.Bar(
                x=labels_with_rank,
                y=top_items['Revenue'],
                marker_color='#7D8570',
                text=[f"${rev:,.0f}" for rev in top_items['Revenue']],
                textposition='outside',
                textfont=dict(size=10, color='#5A6B5E'),
                name='Revenue',
                hovertemplate='<b>%{x}</b><br>$%{y:,.0f} • %{customdata} units<extra></extra>',
                customdata=top_items['Quantity'].astype(int)
            ))
            
            fig.update_layout(
                showlegend=False, 
                height=400, 
                margin=dict(l=0, r=0, t=50, b=100),
                xaxis=dict(tickangle=-45, title='', tickfont=dict(size=9)),
                yaxis=dict(tickformat='$,.0f', title='Revenue')
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col_right:
            st.subheader("📊 Category Performance")
            if selected_category == "All Categories":
                cat_data = filtered_df.groupby('Category')['Revenue'].sum().sort_values(ascending=False)
                
                # Create donut chart with legend instead of outside labels
                fig = go.Figure(data=[go.Pie(
                    labels=cat_data.index,
                    values=cat_data.values,
                    hole=0.5,
                    marker=dict(colors=px.colors.qualitative.Pastel),
                    texttemplate='%{percent}',
                    textposition='inside',
                    textfont=dict(size=12, color='white'),
                    hovertemplate='<b>%{label}</b><br>$%{value:,.0f} • %{percent}<extra></extra>'
                )])
                fig.update_layout(
                    height=450,
                    margin=dict(l=20, r=20, t=20, b=20),
                    showlegend=True,
                    legend=dict(
                        orientation='v',
                        yanchor='middle',
                        y=0.5,
                        xanchor='left',
                        x=1.05,
                        font=dict(size=10)
                    ),
                    annotations=[dict(
                        text=f'${cat_data.sum():,.0f}<br>Total',
                        x=0.5, y=0.5,
                        font_size=18,
                        showarrow=False
                    )]
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                prod_data = filtered_df.groupby('Description')['Revenue'].sum()
                
                # Show top 6 products + Others in donut (reduced from 8)
                top_6 = prod_data.nlargest(6)
                other = prod_data[~prod_data.index.isin(top_6.index)].sum()
                if other > 0:
                    plot_data = pd.concat([top_6, pd.Series({'Others': other})])
                else:
                    plot_data = top_6
                
                fig = go.Figure(data=[go.Pie(
                    labels=plot_data.index,
                    values=plot_data.values,
                    hole=0.5,
                    marker=dict(colors=px.colors.qualitative.Set2),
                    texttemplate='%{percent}',
                    textposition='inside',
                    textfont=dict(size=12, color='white'),
                    hovertemplate='<b>%{label}</b><br>$%{value:,.0f} • %{percent}<extra></extra>'
                )])
                fig.update_layout(
                    height=450,
                    margin=dict(l=20, r=20, t=20, b=20),
                    showlegend=True,
                    legend=dict(
                        orientation='v',
                        yanchor='middle',
                        y=0.5,
                        xanchor='left',
                        x=1.05,
                        font=dict(size=9)
                    ),
                    annotations=[dict(
                        text=f'${prod_data.sum():,.0f}<br>Total',
                        x=0.5, y=0.5,
                        font_size=18,
                        showarrow=False
                    )]
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # ==== MONTHLY VIEW (15+ days) ====
    else:  # Monthly
        # Show date range in header
        st.caption(f"**Period:** {min_date.strftime('%B %d, %Y')} to {max_date.strftime('%B %d, %Y')}")
        
        # Key metrics without sparklines
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 Total Revenue", f"${filtered_df['Revenue'].sum():,.2f}")
        with col2:
            st.metric("📦 Total Units", f"{int(filtered_df['Quantity'].sum()):,}")
        with col3:
            avg_daily = filtered_df.groupby('Date')['Revenue'].sum().mean()
            st.metric("📊 Avg Daily Rev", f"${avg_daily:,.0f}")
        with col4:
            st.metric("📅 Days Active", f"{filtered_df['Date'].nunique()}")
        
        st.markdown("---")
        
        # Weekly breakdown with toggle
        weekly_view_col1, weekly_view_col2 = st.columns([3, 1])
        with weekly_view_col1:
            st.subheader("📊 Weekly Performance")
            if selected_product != "All Products":
                st.caption(f"Showing trend for: **{selected_product}**")
            elif selected_category != "All Categories":
                st.caption(f"Showing trend for category: **{selected_category}**")
        with weekly_view_col2:
            weekly_metric = st.radio(
                "View:",
                ["Revenue ($)", "Quantity"],
                horizontal=True,
                key="monthly_weekly_toggle"
            )
        
        # Calculate week numbers (1-7 = Week 1, 8-14 = Week 2, etc.)
        weekly_data = filtered_df.copy()
        weekly_data['DayOfMonth'] = weekly_data['Date'].dt.day
        weekly_data['WeekNum'] = ((weekly_data['DayOfMonth'] - 1) // 7) + 1
        weekly_data['MonthName'] = weekly_data['Date'].dt.strftime('%b')
        
        # Group by week
        weekly_summary = weekly_data.groupby(['MonthName', 'WeekNum']).agg({
            'Revenue': 'sum',
            'Quantity': 'sum',
            'Date': ['min', 'max']
        }).reset_index()
        
        # Create week labels with date ranges (e.g., "Dec 1-7")
        week_labels = []
        for _, row in weekly_summary.iterrows():
            month = row[('MonthName', '')]
            start_day = row[('Date', 'min')].day
            end_day = row[('Date', 'max')].day
            week_labels.append(f"{month} {start_day}-{end_day}")
        
        weekly_summary['WeekLabel'] = week_labels
        
        # Choose data based on toggle
        if weekly_metric == "Revenue ($)":
            y_data = weekly_summary[('Revenue', 'sum')]
            y_title = 'Revenue ($)'
            hover_template = '<b>%{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>'
            color = '#10b981'
            tick_format = '$,.0f'
        else:  # Quantity
            y_data = weekly_summary[('Quantity', 'sum')]
            y_title = 'Quantity'
            hover_template = '<b>%{x}</b><br>Quantity: %{y:,.0f}<extra></extra>'
            color = '#7D8570'
            tick_format = ',.0f'
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=weekly_summary['WeekLabel'],
            y=y_data,
            marker_color=color,
            text=[f"{v:,.0f}" for v in y_data],
            textposition='outside',
            textfont=dict(size=10),
            hovertemplate=hover_template
        ))
        fig.update_layout(
            height=400,
            margin=dict(l=0, r=0, t=20, b=40),
            xaxis=dict(title='Week', showgrid=False),
            yaxis=dict(title=y_title, tickformat=tick_format, showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            plot_bgcolor='white',
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("🏆 Top 10 Products")
            if selected_category != "All Categories":
                st.caption(f"Top products in: **{selected_category}**")
            
            # Use horizontal bars for better readability
            top_products = filtered_df.groupby('Description')['Revenue'].sum().sort_values(ascending=True).tail(10)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=top_products.index,
                x=top_products.values,
                orientation='h',
                marker_color='#7D8570',
                text=[f"${rev:,.0f}" for rev in top_products.values],
                textposition='outside',
                textfont=dict(size=10),
                hovertemplate='<b>%{y}</b><br>Revenue: $%{x:,.2f}<extra></extra>'
            ))
            fig.update_layout(
                showlegend=False,
                height=450,
                margin=dict(l=0, r=60, t=20, b=40),
                xaxis=dict(title='Revenue ($)', tickformat='$,.0f'),
                yaxis=dict(title='', tickfont=dict(size=9))
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col_right:
            st.subheader("📊 Performance Summary")
            if selected_category == "All Categories":
                cat_data = filtered_df.groupby('Category').agg({
                    'Revenue': 'sum',
                    'Quantity': 'sum'
                }).sort_values('Revenue', ascending=False)
                cat_data['% of Total'] = (cat_data['Revenue'] / cat_data['Revenue'].sum() * 100).round(1)
                
                st.dataframe(cat_data.style.format({
                    'Revenue': "${:,.2f}",
                    'Quantity': "{:,.0f}",
                    '% of Total': "{:.1f}%"
                }), use_container_width=True)
            else:
                prod_data = filtered_df.groupby('Description').agg({
                    'Revenue': 'sum',
                    'Quantity': 'sum'
                }).sort_values('Revenue', ascending=False)
                prod_data['Avg Price'] = (prod_data['Revenue'] / prod_data['Quantity']).round(2)
                
                st.dataframe(prod_data.style.format({
                    'Revenue': "${:,.2f}",
                    'Quantity': "{:,.0f}",
                    'Avg Price': "${:.2f}"
                }), use_container_width=True, height=400)
    
    # Compare Periods button
    st.markdown("---")
    st.subheader("📊 Compare Periods")
    if st.button("➕ Compare with Another Period", type="primary", use_container_width=True):
        st.session_state.show_comparison = True
        st.rerun()
    
    # === COMPARISON MODE ===
    if st.session_state.get('show_comparison', False):
        st.markdown("---")
        st.markdown("## 🔄 Period Comparison")
        st.caption("Compare two time periods side-by-side with the same filters applied")
        
        # Store Period 1 data
        if 'comparison_period1' not in st.session_state:
            st.session_state.comparison_period1 = {
                'df': filtered_df.copy(),
                'date_range': f"{min_date.strftime('%b %d')} - {max_date.strftime('%b %d, %Y')}",
                'days': days_span,
                'category': selected_category,
                'product': selected_product
            }
        
        # Check if filters changed - update both periods
        if (st.session_state.comparison_period1.get('category') != selected_category or 
            st.session_state.comparison_period1.get('product') != selected_product):
            
            # Update Period 1
            st.session_state.comparison_period1 = {
                'df': filtered_df.copy(),
                'date_range': f"{min_date.strftime('%b %d')} - {max_date.strftime('%b %d, %Y')}",
                'days': days_span,
                'category': selected_category,
                'product': selected_product
            }
            
            # If Period 2 exists, reapply filters (keep dates, update data)
            if 'comparison_period2' in st.session_state and 'comparison_period2_dates' in st.session_state:
                p2_dates = st.session_state.comparison_period2_dates
                comp_df, error = process_gdrive_files(
                    service,
                    st.session_state.folder_id,
                    p2_dates['start'],
                    p2_dates['end']
                )
                
                # Apply new filters
                if selected_category != "All Categories":
                    comp_df = comp_df[comp_df['Category'] == selected_category]
                if selected_product != "All Products":
                    comp_df = comp_df[comp_df['Description'] == selected_product]
                
                if not error and not comp_df.empty:
                    st.session_state.comparison_period2 = {
                        'df': comp_df,
                        'date_range': st.session_state.comparison_period2['date_range'],
                        'days': st.session_state.comparison_period2['days'],
                        'category': selected_category,
                        'product': selected_product
                    }
        
        # Period 2 date selector
        st.markdown("### 📅 Select Period 2 to Compare")
        
        comp_col1, comp_col2, comp_col3, comp_col4 = st.columns(4)
        
        today = datetime.now().date()
        
        with comp_col1:
            if st.button("⏮️ Previous Period", use_container_width=True):
                days_back = (max_date - min_date).days + 1
                st.session_state.comp_preset_start = (min_date - timedelta(days=days_back)).date()
                st.session_state.comp_preset_end = (min_date - timedelta(days=1)).date()
        
        with comp_col2:
            if st.button("📅 Last Week", use_container_width=True):
                st.session_state.comp_preset_start = today - timedelta(days=13)
                st.session_state.comp_preset_end = today - timedelta(days=7)
        
        with comp_col3:
            if st.button("📆 Last Month", use_container_width=True):
                last_month = today.replace(day=1) - timedelta(days=1)
                st.session_state.comp_preset_start = last_month.replace(day=1)
                st.session_state.comp_preset_end = last_month
        
        with comp_col4:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.show_comparison = False
                if 'comparison_period1' in st.session_state:
                    del st.session_state.comparison_period1
                if 'comparison_period2' in st.session_state:
                    del st.session_state.comparison_period2
                if 'comparison_period2_dates' in st.session_state:
                    del st.session_state.comparison_period2_dates
                st.rerun()
        
        st.markdown("---")
        
        # Date pickers for Period 2
        comp_date_col1, comp_date_col2, comp_date_col3 = st.columns([2, 2, 1])
        
        default_comp_start = st.session_state.get('comp_preset_start', today - timedelta(days=6))
        default_comp_end = st.session_state.get('comp_preset_end', today)
        
        with comp_date_col1:
            comp_start_date = st.date_input(
                "📅 Period 2: From Date",
                value=default_comp_start,
                max_value=today,
                key="comp_start"
            )
        
        with comp_date_col2:
            comp_end_date = st.date_input(
                "📅 Period 2: To Date",
                value=default_comp_end,
                min_value=comp_start_date,
                max_value=today,
                key="comp_end"
            )
        
        with comp_date_col3:
            st.markdown("<br>", unsafe_allow_html=True)
            comp_load_button = st.button("🔄 Load Period 2", type="primary", use_container_width=True)
        
        # Load Period 2 data
        if comp_load_button and service and st.session_state.get('folder_id'):
            with st.spinner("📥 Loading comparison data..."):
                comp_df, error = process_gdrive_files(
                    service,
                    st.session_state.folder_id,
                    pd.Timestamp(comp_start_date),
                    pd.Timestamp(comp_end_date)
                )
                
                # Apply same filters as Period 1
                if selected_category != "All Categories":
                    comp_df = comp_df[comp_df['Category'] == selected_category]
                if selected_product != "All Products":
                    comp_df = comp_df[comp_df['Description'] == selected_product]
                
                if not error and not comp_df.empty:
                    # Store the dates so we can reload with new filters
                    st.session_state.comparison_period2_dates = {
                        'start': pd.Timestamp(comp_start_date),
                        'end': pd.Timestamp(comp_end_date)
                    }
                    st.session_state.comparison_period2 = {
                        'df': comp_df,
                        'date_range': f"{comp_start_date.strftime('%b %d')} - {comp_end_date.strftime('%b %d, %Y')}",
                        'days': (comp_end_date - comp_start_date).days + 1
                    }
                    st.success(f"✅ Loaded Period 2: {len(comp_df):,} records")
                elif error:
                    st.error(error)
                else:
                    st.warning("No data found for Period 2")
        
        # Show comparison if both periods loaded
        if 'comparison_period2' in st.session_state:
            st.markdown("---")
            
            p1 = st.session_state.comparison_period1
            p2 = st.session_state.comparison_period2
            
            # Debug: Show data info
            st.caption(f"Period 1: {len(p1['df'])} records | Period 2: {len(p2['df'])} records")
            
            # Comparison metrics
            p1_rev = p1['df']['Revenue'].sum()
            p2_rev = p2['df']['Revenue'].sum()
            rev_change = p2_rev - p1_rev
            rev_change_pct = (rev_change / p1_rev * 100) if p1_rev > 0 else 0
            
            p1_units = p1['df']['Quantity'].sum()
            p2_units = p2['df']['Quantity'].sum()
            units_change = p2_units - p1_units
            units_change_pct = (units_change / p1_units * 100) if p1_units > 0 else 0
            
            # Enhanced comparison header
            st.markdown(f"""
            <div style='background: linear-gradient(90deg, #6B705C 0%, #9DAB86 100%); 
                        padding: 25px; border-radius: 12px; margin-bottom: 20px;
                        box-shadow: 0 4px 15px rgba(107, 112, 92, 0.2);'>
                <h3 style='color: white; margin: 0; font-family: Georgia, serif;'>📊 Period Comparison</h3>
                <p style='color: #FAF9F6; margin: 8px 0 0 0; opacity: 0.95; font-size: 15px;'>
                    {p1['date_range']} vs {p2['date_range']}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Comparison metrics with 3-column layout: Period 1 | Delta | Period 2
            st.markdown("### 📊 Key Metrics Comparison")
            
            # Revenue comparison
            rev_col1, rev_col2, rev_col3 = st.columns([2, 1.5, 2])
            with rev_col1:
                st.metric(f"💰 {p1['date_range']}", f"${p1_rev:,.2f}")
            with rev_col2:
                arrow = "↑" if rev_change > 0 else "↓" if rev_change < 0 else "→"
                color = "#10b981" if rev_change > 0 else "#ef4444" if rev_change < 0 else "#6b7280"
                st.markdown(f"""
                <div style='text-align: center; padding: 20px; background: rgba(255,255,255,0.5); border-radius: 8px; margin-top: 8px;'>
                    <div style='font-size: 36px; color: {color}; font-weight: bold;'>{arrow}</div>
                    <div style='font-size: 20px; color: {color}; font-weight: bold; margin-top: 5px;'>{rev_change_pct:+.1f}%</div>
                    <div style='font-size: 14px; color: {color}; margin-top: 5px;'>${rev_change:+,.0f}</div>
                </div>
                """, unsafe_allow_html=True)
            with rev_col3:
                st.metric(f"💰 {p2['date_range']}", f"${p2_rev:,.2f}")
            
            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
            
            # Units comparison
            units_col1, units_col2, units_col3 = st.columns([2, 1.5, 2])
            with units_col1:
                st.metric(f"📦 {p1['date_range']}", f"{int(p1_units):,}")
            with units_col2:
                arrow = "↑" if units_change > 0 else "↓" if units_change < 0 else "→"
                color = "#10b981" if units_change > 0 else "#ef4444" if units_change < 0 else "#6b7280"
                st.markdown(f"""
                <div style='text-align: center; padding: 20px; background: rgba(255,255,255,0.5); border-radius: 8px; margin-top: 8px;'>
                    <div style='font-size: 36px; color: {color}; font-weight: bold;'>{arrow}</div>
                    <div style='font-size: 20px; color: {color}; font-weight: bold; margin-top: 5px;'>{units_change_pct:+.1f}%</div>
                    <div style='font-size: 14px; color: {color}; margin-top: 5px;'>{units_change:+,.0f} units</div>
                </div>
                """, unsafe_allow_html=True)
            with units_col3:
                st.metric(f"📦 {p2['date_range']}", f"{int(p2_units):,}")
            
            st.markdown("---")
            
            # Pattern Comparison Charts (Hourly/Daily/Weekly based on period length)
            st.markdown("### 📊 Sales Pattern Comparison")
            
            # Determine what type of pattern chart to show based on period length
            p1_days = p1['days']
            p2_days = p2['days']
            
            # Add toggle for metric
            pattern_toggle_col1, pattern_toggle_col2 = st.columns([3, 1])
            with pattern_toggle_col2:
                pattern_metric = st.radio(
                    "View:",
                    ["Revenue ($)", "Quantity"],
                    horizontal=True,
                    key="comparison_pattern_toggle"
                )
            
            # Determine chart type based on period lengths
            if p1_days == 1 and p2_days == 1:
                # Both are single days - show hourly comparison
                with pattern_toggle_col1:
                    st.caption("Hourly Pattern Comparison")
                
                # Get hourly data for both periods
                p1_hourly = p1['df'].groupby('Hour').agg({
                    'Revenue': 'sum',
                    'Quantity': 'sum'
                }).reset_index()
                p1_hourly = p1_hourly[(p1_hourly['Hour'] >= 8) & (p1_hourly['Hour'] <= 22)]
                
                p2_hourly = p2['df'].groupby('Hour').agg({
                    'Revenue': 'sum',
                    'Quantity': 'sum'
                }).reset_index()
                p2_hourly = p2_hourly[(p2_hourly['Hour'] >= 8) & (p2_hourly['Hour'] <= 22)]
                
                # Choose data based on toggle
                if pattern_metric == "Revenue ($)":
                    p1_y = p1_hourly['Revenue']
                    p2_y = p2_hourly['Revenue']
                    y_title = 'Revenue ($)'
                    tick_format = '$,.0f'
                    color1 = '#7D8570'
                    color2 = '#B5C99A'
                else:
                    p1_y = p1_hourly['Quantity']
                    p2_y = p2_hourly['Quantity']
                    y_title = 'Quantity'
                    tick_format = ',.0f'
                    color1 = '#7D8570'
                    color2 = '#B5C99A'
                
                # Side-by-side hourly charts
                hourly_col1, hourly_col2 = st.columns(2)
                
                with hourly_col1:
                    st.caption(f"📊 {p1['date_range']}")
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=p1_hourly['Hour'],
                        y=p1_y,
                        mode='lines+markers',
                        line=dict(color=color1, width=3),
                        marker=dict(size=6),
                        fill='tozeroy',
                        fillcolor=f'rgba(125, 133, 112, 0.2)',
                        hovertemplate=f'Hour: %{{x}}<br>{y_title}: %{{y:,.0f}}<extra></extra>'
                    ))
                    fig.update_layout(
                        height=350,
                        margin=dict(l=0, r=0, t=10, b=40),
                        xaxis=dict(title='Hour', dtick=2, showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
                        yaxis=dict(title=y_title, tickformat=tick_format, showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
                        plot_bgcolor='white',
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with hourly_col2:
                    st.caption(f"📊 {p2['date_range']}")
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=p2_hourly['Hour'],
                        y=p2_y,
                        mode='lines+markers',
                        line=dict(color=color2, width=3),
                        marker=dict(size=6),
                        fill='tozeroy',
                        fillcolor=f'rgba(181, 201, 154, 0.2)',
                        hovertemplate=f'Hour: %{{x}}<br>{y_title}: %{{y:,.0f}}<extra></extra>'
                    ))
                    fig.update_layout(
                        height=350,
                        margin=dict(l=0, r=0, t=10, b=40),
                        xaxis=dict(title='Hour', dtick=2, showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
                        yaxis=dict(title=y_title, tickformat=tick_format, showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
                        plot_bgcolor='white',
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            elif p1_days <= 14 and p2_days <= 14:
                # Weekly periods - show daily comparison
                with pattern_toggle_col1:
                    st.caption("Day-by-Day Pattern Comparison")
                
                # Get daily data
                p1_daily = p1['df'].groupby('Date').agg({
                    'Revenue': 'sum',
                    'Quantity': 'sum'
                }).reset_index()
                p1_daily['DateLabel'] = p1_daily['Date'].dt.strftime('%b %d')
                
                p2_daily = p2['df'].groupby('Date').agg({
                    'Revenue': 'sum',
                    'Quantity': 'sum'
                }).reset_index()
                p2_daily['DateLabel'] = p2_daily['Date'].dt.strftime('%b %d')
                
                # Choose data
                if pattern_metric == "Revenue ($)":
                    p1_y = p1_daily['Revenue']
                    p2_y = p2_daily['Revenue']
                    y_title = 'Revenue ($)'
                    tick_format = '$,.0f'
                    color1 = '#10b981'
                    color2 = '#7D8570'
                else:
                    p1_y = p1_daily['Quantity']
                    p2_y = p2_daily['Quantity']
                    y_title = 'Quantity'
                    tick_format = ',.0f'
                    color1 = '#10b981'
                    color2 = '#7D8570'
                
                # Side-by-side daily charts
                daily_comp_col1, daily_comp_col2 = st.columns(2)
                
                with daily_comp_col1:
                    st.caption(f"📊 {p1['date_range']}")
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=p1_daily['DateLabel'],
                        y=p1_y,
                        marker_color=color1,
                        hovertemplate=f'<b>%{{x}}</b><br>{y_title}: %{{y:,.0f}}<extra></extra>'
                    ))
                    fig.update_layout(
                        height=350,
                        margin=dict(l=0, r=0, t=10, b=40),
                        xaxis=dict(title='Date', tickangle=-45),
                        yaxis=dict(title=y_title, tickformat=tick_format),
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with daily_comp_col2:
                    st.caption(f"📊 {p2['date_range']}")
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=p2_daily['DateLabel'],
                        y=p2_y,
                        marker_color=color2,
                        hovertemplate=f'<b>%{{x}}</b><br>{y_title}: %{{y:,.0f}}<extra></extra>'
                    ))
                    fig.update_layout(
                        height=350,
                        margin=dict(l=0, r=0, t=10, b=40),
                        xaxis=dict(title='Date', tickangle=-45),
                        yaxis=dict(title=y_title, tickformat=tick_format),
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            else:
                # Monthly periods - show weekly comparison
                with pattern_toggle_col1:
                    st.caption("Week-by-Week Pattern Comparison")
                
                # Calculate weekly data for both periods
                def get_weekly_data(df):
                    weekly_df = df.copy()
                    weekly_df['DayOfMonth'] = weekly_df['Date'].dt.day
                    weekly_df['WeekNum'] = ((weekly_df['DayOfMonth'] - 1) // 7) + 1
                    weekly_df['MonthName'] = weekly_df['Date'].dt.strftime('%b')
                    
                    weekly_summary = weekly_df.groupby(['MonthName', 'WeekNum']).agg({
                        'Revenue': 'sum',
                        'Quantity': 'sum',
                        'Date': ['min', 'max']
                    }).reset_index()
                    
                    week_labels = []
                    for _, row in weekly_summary.iterrows():
                        month = row[('MonthName', '')]
                        start_day = row[('Date', 'min')].day
                        end_day = row[('Date', 'max')].day
                        week_labels.append(f"{month} {start_day}-{end_day}")
                    
                    weekly_summary['WeekLabel'] = week_labels
                    return weekly_summary
                
                p1_weekly = get_weekly_data(p1['df'])
                p2_weekly = get_weekly_data(p2['df'])
                
                # Choose data
                if pattern_metric == "Revenue ($)":
                    p1_y = p1_weekly[('Revenue', 'sum')]
                    p2_y = p2_weekly[('Revenue', 'sum')]
                    y_title = 'Revenue ($)'
                    tick_format = '$,.0f'
                    color1 = '#10b981'
                    color2 = '#7D8570'
                else:
                    p1_y = p1_weekly[('Quantity', 'sum')]
                    p2_y = p2_weekly[('Quantity', 'sum')]
                    y_title = 'Quantity'
                    tick_format = ',.0f'
                    color1 = '#10b981'
                    color2 = '#7D8570'
                
                # Side-by-side weekly charts
                weekly_comp_col1, weekly_comp_col2 = st.columns(2)
                
                with weekly_comp_col1:
                    st.caption(f"📊 {p1['date_range']}")
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=p1_weekly['WeekLabel'],
                        y=p1_y,
                        marker_color=color1,
                        text=[f"{v:,.0f}" for v in p1_y],
                        textposition='outside',
                        textfont=dict(size=9),
                        hovertemplate=f'<b>%{{x}}</b><br>{y_title}: %{{y:,.0f}}<extra></extra>'
                    ))
                    fig.update_layout(
                        height=350,
                        margin=dict(l=0, r=0, t=30, b=40),
                        xaxis=dict(title='Week'),
                        yaxis=dict(title=y_title, tickformat=tick_format),
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with weekly_comp_col2:
                    st.caption(f"📊 {p2['date_range']}")
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=p2_weekly['WeekLabel'],
                        y=p2_y,
                        marker_color=color2,
                        text=[f"{v:,.0f}" for v in p2_y],
                        textposition='outside',
                        textfont=dict(size=9),
                        hovertemplate=f'<b>%{{x}}</b><br>{y_title}: %{{y:,.0f}}<extra></extra>'
                    ))
                    fig.update_layout(
                        height=350,
                        margin=dict(l=0, r=0, t=30, b=40),
                        xaxis=dict(title='Week'),
                        yaxis=dict(title=y_title, tickformat=tick_format),
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Side-by-side charts with rank changes
            st.markdown("### 📈 Top Products Comparison")
            
            # Get top products for both periods
            p1_data = p1['df'].groupby('Description').agg({
                'Revenue': 'sum',
                'Quantity': 'sum'
            }).sort_values('Revenue', ascending=False).head(10)
            
            p2_data = p2['df'].groupby('Description').agg({
                'Revenue': 'sum',
                'Quantity': 'sum'
            }).sort_values('Revenue', ascending=False).head(10)
            
            # Calculate rank changes
            p1_ranks = {prod: i+1 for i, prod in enumerate(p1_data.index)}
            p2_ranks = {prod: i+1 for i, prod in enumerate(p2_data.index)}
            
            rank_changes = {}
            for prod in p2_data.index:
                if prod in p1_ranks:
                    change = p1_ranks[prod] - p2_ranks[prod]  # Positive means moved up
                    if change > 0:
                        rank_changes[prod] = f"↑{change}"
                    elif change < 0:
                        rank_changes[prod] = f"↓{abs(change)}"
                    else:
                        rank_changes[prod] = "—"
                else:
                    rank_changes[prod] = "NEW"
            
            comp_chart_col1, comp_chart_col2 = st.columns(2)
            
            with comp_chart_col1:
                st.caption(f"📊 {p1['date_range']}")
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=p1_data.index,
                    y=p1_data['Revenue'],
                    marker_color='#7D8570',
                    text=[f"#{i+1}" for i in range(len(p1_data))],
                    textposition='outside',
                    textfont=dict(color='#5A6B5E', size=10),
                    hovertemplate='<b>%{x}</b><br>$%{y:,.0f} • %{customdata} units<extra></extra>',
                    customdata=p1_data['Quantity'].astype(int)
                ))
                fig.update_layout(
                    showlegend=False, 
                    height=400, 
                    margin=dict(l=0, r=0, t=40, b=80),
                    xaxis={'tickangle': -45, 'title': ''},
                    yaxis={'tickformat': '$,.0f', 'title': 'Revenue'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with comp_chart_col2:
                st.caption(f"📊 {p2['date_range']}")
                
                fig = go.Figure()
                
                # Add rank with rank change indicators
                rank_labels = []
                for i, prod in enumerate(p2_data.index):
                    rank_indicator = rank_changes.get(prod, "")
                    if rank_indicator:
                        rank_labels.append(f"#{i+1} {rank_indicator}")
                    else:
                        rank_labels.append(f"#{i+1}")
                
                fig.add_trace(go.Bar(
                    x=p2_data.index,
                    y=p2_data['Revenue'],
                    marker_color='#B5C99A',
                    text=rank_labels,
                    textposition='outside',
                    textfont=dict(color='#5A6B5E', size=10),
                    hovertemplate='<b>%{x}</b><br>$%{y:,.0f} • %{customdata} units<extra></extra>',
                    customdata=p2_data['Quantity'].astype(int)
                ))
                fig.update_layout(
                    showlegend=False, 
                    height=400, 
                    margin=dict(l=0, r=0, t=40, b=80),
                    xaxis={'tickangle': -45, 'title': ''},
                    yaxis={'tickformat': '$,.0f', 'title': 'Revenue'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # If specific product selected, show hourly comparison
            if selected_product != "All Products":
                st.subheader(f"⏱️ Hourly Sales Pattern: {selected_product}")
                
                # Get hourly data for both periods
                p1_hourly = p1['df'].groupby('Hour').agg({
                    'Revenue': 'sum',
                    'Quantity': 'sum'
                }).reset_index()
                
                p2_hourly = p2['df'].groupby('Hour').agg({
                    'Revenue': 'sum',
                    'Quantity': 'sum'
                }).reset_index()
                
                # Create side-by-side hourly charts
                hourly_col1, hourly_col2 = st.columns(2)
                
                with hourly_col1:
                    st.caption(f"📊 {p1['date_range']}")
                    fig = go.Figure()
                    
                    # Line chart for revenue without fill
                    fig.add_trace(go.Scatter(
                        x=p1_hourly['Hour'],
                        y=p1_hourly['Revenue'],
                        mode='lines',
                        name='Revenue',
                        line=dict(color='#7D8570', width=3),
                        hovertemplate='Hour: %{x}<br>Revenue: $%{y:,.2f}<extra></extra>'
                    ))
                    
                    # Add units as markers
                    fig.add_trace(go.Scatter(
                        x=p1_hourly['Hour'],
                        y=p1_hourly['Revenue'],
                        mode='markers+text',
                        marker=dict(size=8, color='#5A6B5E'),
                        text=[f"{int(q)}" for q in p1_hourly['Quantity']],
                        textposition='top center',
                        textfont=dict(size=9, color='#5A6B5E'),
                        showlegend=False,
                        hovertemplate='Units: %{text}<extra></extra>'
                    ))
                    
                    fig.update_layout(
                        height=350,
                        margin=dict(l=0, r=0, t=10, b=0),
                        xaxis=dict(title='Hour of Day', dtick=1),
                        yaxis=dict(title='Revenue ($)', tickformat='$,.0f'),
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with hourly_col2:
                    st.caption(f"📊 {p2['date_range']}")
                    fig = go.Figure()
                    
                    # Line chart for revenue without fill
                    fig.add_trace(go.Scatter(
                        x=p2_hourly['Hour'],
                        y=p2_hourly['Revenue'],
                        mode='lines',
                        name='Revenue',
                        line=dict(color='#B5C99A', width=3),
                        hovertemplate='Hour: %{x}<br>Revenue: $%{y:,.2f}<extra></extra>'
                    ))
                    
                    # Add units as markers
                    fig.add_trace(go.Scatter(
                        x=p2_hourly['Hour'],
                        y=p2_hourly['Revenue'],
                        mode='markers+text',
                        marker=dict(size=8, color='#7D8570'),
                        text=[f"{int(q)}" for q in p2_hourly['Quantity']],
                        textposition='top center',
                        textfont=dict(size=9, color='#7D8570'),
                        showlegend=False,
                        hovertemplate='Units: %{text}<extra></extra>'
                    ))
                    
                    fig.update_layout(
                        height=350,
                        margin=dict(l=0, r=0, t=10, b=0),
                        xaxis=dict(title='Hour of Day', dtick=1),
                        yaxis=dict(title='Revenue ($)', tickformat='$,.0f'),
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Peak hours summary
                p1_peak_hour = p1_hourly.loc[p1_hourly['Revenue'].idxmax(), 'Hour']
                p2_peak_hour = p2_hourly.loc[p2_hourly['Revenue'].idxmax(), 'Hour']
                
                peak_col1, peak_col2 = st.columns(2)
                with peak_col1:
                    st.info(f"🕐 Peak Hour: {int(p1_peak_hour)}:00")
                with peak_col2:
                    st.info(f"🕐 Peak Hour: {int(p2_peak_hour)}:00")
            
            # Product-level comparison table
            st.markdown("---")
            # Category/Product comparison visualization
            if selected_category == "All Categories" and selected_product == "All Products":
                st.subheader("📊 Category Performance Comparison")
                
                # Get category data for both periods
                p1_cat = p1['df'].groupby('Category')['Revenue'].sum()
                p2_cat = p2['df'].groupby('Category')['Revenue'].sum()
                
                # Debug info
                st.caption(f"Period 1 categories: {len(p1_cat)} | Period 2 categories: {len(p2_cat)}")
                
                # Create donut charts side by side
                donut_col1, donut_col2 = st.columns(2)
                
                with donut_col1:
                    st.caption(f"📊 {p1['date_range']}")
                    fig = go.Figure(data=[go.Pie(
                        labels=p1_cat.index,
                        values=p1_cat.values,
                        hole=0.5,
                        marker=dict(colors=px.colors.qualitative.Pastel),
                        texttemplate='%{percent}',
                        textposition='inside',
                        textfont=dict(size=11, color='white'),
                        hovertemplate='<b>%{label}</b><br>$%{value:,.0f} • %{percent}<extra></extra>'
                    )])
                    fig.update_layout(
                        height=450,
                        margin=dict(l=20, r=20, t=40, b=20),
                        showlegend=True,
                        legend=dict(
                            orientation='v',
                            yanchor='top',
                            y=1,
                            xanchor='left',
                            x=1.05,
                            font=dict(size=9)
                        ),
                        annotations=[dict(
                            text=f'${p1_cat.sum():,.0f}',
                            x=0.5, y=0.5,
                            font_size=18,
                            showarrow=False
                        )]
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with donut_col2:
                    st.caption(f"📊 {p2['date_range']}")
                    fig = go.Figure(data=[go.Pie(
                        labels=p2_cat.index,
                        values=p2_cat.values,
                        hole=0.5,
                        marker=dict(colors=px.colors.qualitative.Set2),
                        texttemplate='%{percent}',
                        textposition='inside',
                        textfont=dict(size=11, color='white'),
                        hovertemplate='<b>%{label}</b><br>$%{value:,.0f} • %{percent}<extra></extra>'
                    )])
                    fig.update_layout(
                        height=450,
                        margin=dict(l=20, r=20, t=40, b=20),
                        showlegend=True,
                        legend=dict(
                            orientation='v',
                            yanchor='top',
                            y=1,
                            xanchor='left',
                            x=1.05,
                            font=dict(size=9)
                        ),
                        annotations=[dict(
                            text=f'${p2_cat.sum():,.0f}',
                            x=0.5, y=0.5,
                            font_size=18,
                            showarrow=False
                        )]
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Change summary below donuts
                st.markdown("#### 📈 Category Changes")
                
                # Use full date range as column names to avoid duplicates
                period1_label = p1['date_range']
                period2_label = p2['date_range']
                
                comp_table = pd.DataFrame({
                    'Category': p1_cat.index,
                    period1_label: p1_cat.values,
                    period2_label: p2_cat.reindex(p1_cat.index, fill_value=0).values
                })
                
                # Add all categories from period 2 that weren't in period 1
                for cat in p2_cat.index:
                    if cat not in comp_table['Category'].values:
                        new_row = pd.DataFrame({
                            'Category': [cat],
                            period1_label: [0],
                            period2_label: [p2_cat[cat]]
                        })
                        comp_table = pd.concat([comp_table, new_row], ignore_index=True)
                
                comp_table['Change $'] = comp_table[period2_label] - comp_table[period1_label]
                comp_table['Change %'] = ((comp_table[period2_label] - comp_table[period1_label]) / comp_table[period1_label] * 100).replace([float('inf'), -float('inf')], 100).fillna(0)
                comp_table = comp_table.sort_values('Change %', ascending=False)
                comp_table = comp_table.set_index('Category')
                
                # Apply color-coded styling with arrows
                def color_change(val):
                    if val > 0:
                        return f'background-color: rgba(16, 185, 129, 0.2); color: #10b981; font-weight: bold;'
                    elif val < 0:
                        return f'background-color: rgba(239, 68, 68, 0.2); color: #ef4444; font-weight: bold;'
                    else:
                        return 'background-color: rgba(156, 163, 175, 0.1); color: #6b7280;'
                
                st.dataframe(comp_table.style.format({
                    period1_label: "${:,.2f}",
                    period2_label: "${:,.2f}",
                    'Change $': "${:,.2f}",
                    'Change %': "{:+.1f}%"
                }).applymap(color_change, subset=['Change %'])
                  .bar(subset=['Change $'], align='mid', color=['#ef4444', '#10b981']),
                use_container_width=True)
                
            else:
                st.subheader("📊 Product Performance Comparison")
                
                p1_prod = p1['df'].groupby('Description')['Revenue'].sum()
                p2_prod = p2['df'].groupby('Description')['Revenue'].sum()
                
                # Donut charts for products
                donut_col1, donut_col2 = st.columns(2)
                
                with donut_col1:
                    st.caption(f"📊 {p1['date_range']}")
                    # Show top 6 products + Others
                    top_6_p1 = p1_prod.nlargest(6)
                    other_p1 = p1_prod[~p1_prod.index.isin(top_6_p1.index)].sum()
                    if other_p1 > 0:
                        plot_data_p1 = pd.concat([top_6_p1, pd.Series({'Others': other_p1})])
                    else:
                        plot_data_p1 = top_6_p1
                    
                    fig = go.Figure(data=[go.Pie(
                        labels=plot_data_p1.index,
                        values=plot_data_p1.values,
                        hole=0.5,
                        marker=dict(colors=px.colors.qualitative.Pastel),
                        texttemplate='%{percent}',
                        textposition='inside',
                        textfont=dict(size=11, color='white'),
                        hovertemplate='<b>%{label}</b><br>$%{value:,.0f} • %{percent}<extra></extra>'
                    )])
                    fig.update_layout(
                        height=450,
                        margin=dict(l=20, r=20, t=40, b=20),
                        showlegend=True,
                        legend=dict(
                            orientation='v',
                            yanchor='top',
                            y=1,
                            xanchor='left',
                            x=1.05,
                            font=dict(size=9)
                        ),
                        annotations=[dict(
                            text=f'${p1_prod.sum():,.0f}',
                            x=0.5, y=0.5,
                            font_size=18,
                            showarrow=False
                        )]
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with donut_col2:
                    st.caption(f"📊 {p2['date_range']}")
                    # Show top 6 products + Others
                    top_6_p2 = p2_prod.nlargest(6)
                    other_p2 = p2_prod[~p2_prod.index.isin(top_6_p2.index)].sum()
                    if other_p2 > 0:
                        plot_data_p2 = pd.concat([top_6_p2, pd.Series({'Others': other_p2})])
                    else:
                        plot_data_p2 = top_6_p2
                    
                    fig = go.Figure(data=[go.Pie(
                        labels=plot_data_p2.index,
                        values=plot_data_p2.values,
                        hole=0.5,
                        marker=dict(colors=px.colors.qualitative.Set2),
                        texttemplate='%{percent}',
                        textposition='inside',
                        textfont=dict(size=11, color='white'),
                        hovertemplate='<b>%{label}</b><br>$%{value:,.0f} • %{percent}<extra></extra>'
                    )])
                    fig.update_layout(
                        height=450,
                        margin=dict(l=20, r=20, t=40, b=20),
                        showlegend=True,
                        legend=dict(
                            orientation='v',
                            yanchor='top',
                            y=1,
                            xanchor='left',
                            x=1.05,
                            font=dict(size=9)
                        ),
                        annotations=[dict(
                            text=f'${p2_prod.sum():,.0f}',
                            x=0.5, y=0.5,
                            font_size=20,
                            showarrow=False
                        )]
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Change summary
                st.markdown("#### 📈 Product Changes")
                
                # Use full date range as column names to avoid duplicates
                period1_label = p1['date_range']
                period2_label = p2['date_range']
                
                comp_table = pd.DataFrame({
                    'Product': p1_prod.index,
                    period1_label: p1_prod.values,
                    period2_label: p2_prod.reindex(p1_prod.index, fill_value=0).values
                })
                
                # Add all products from period 2 that weren't in period 1
                for prod in p2_prod.index:
                    if prod not in comp_table['Product'].values:
                        new_row = pd.DataFrame({
                            'Product': [prod],
                            period1_label: [0],
                            period2_label: [p2_prod[prod]]
                        })
                        comp_table = pd.concat([comp_table, new_row], ignore_index=True)
                
                comp_table['Change $'] = comp_table[period2_label] - comp_table[period1_label]
                comp_table['Change %'] = ((comp_table[period2_label] - comp_table[period1_label]) / comp_table[period1_label] * 100).replace([float('inf'), -float('inf')], 100).fillna(0)
                comp_table = comp_table.sort_values('Change %', ascending=False)
                comp_table = comp_table.set_index('Product')
                
                # Apply color-coded styling with arrows
                def color_change(val):
                    if val > 0:
                        return f'background-color: rgba(16, 185, 129, 0.2); color: #10b981; font-weight: bold;'
                    elif val < 0:
                        return f'background-color: rgba(239, 68, 68, 0.2); color: #ef4444; font-weight: bold;'
                    else:
                        return 'background-color: rgba(156, 163, 175, 0.1); color: #6b7280;'
                
                st.dataframe(comp_table.style.format({
                    period1_label: "${:,.2f}",
                    period2_label: "${:,.2f}",
                    'Change $': "${:,.2f}",
                    'Change %': "{:+.1f}%"
                }).applymap(color_change, subset=['Change %'])
                  .bar(subset=['Change $'], align='mid', color=['#ef4444', '#10b981']),
                use_container_width=True)

elif service and st.session_state.get('folder_id'):
    # Show date picker at top when Drive is connected but no data loaded yet
    st.markdown("## 📅 Select Date Range to Load Data")
    
    # Define date constraints
    FIRST_SALE_DATE = datetime(2024, 5, 29).date()  # First sale date
    today = datetime.now().date()
    
    # Info message about data availability
    st.info(f"ℹ️ Sales data available from **May 29, 2024** onwards")
    
    # Preset buttons
    st.markdown("**Quick Select:**")
    preset_col1, preset_col2, preset_col3, preset_col4, preset_col5, preset_col6 = st.columns(6)
    
    with preset_col1:
        if st.button("📆 Today", use_container_width=True):
            st.session_state.preset_start = today
            st.session_state.preset_end = today
    
    with preset_col2:
        if st.button("🕐 Yesterday", use_container_width=True):
            st.session_state.preset_start = today - timedelta(days=1)
            st.session_state.preset_end = today - timedelta(days=1)
    
    with preset_col3:
        if st.button("📊 Last 7 Days", use_container_width=True):
            st.session_state.preset_start = today - timedelta(days=6)
            st.session_state.preset_end = today
    
    with preset_col4:
        if st.button("📈 Last 30 Days", use_container_width=True):
            st.session_state.preset_start = today - timedelta(days=29)
            st.session_state.preset_end = today
    
    with preset_col5:
        if st.button("📅 This Month", use_container_width=True):
            st.session_state.preset_start = today.replace(day=1)
            st.session_state.preset_end = today
    
    with preset_col6:
        if st.button("📆 Last Month", use_container_width=True):
            last_month = today.replace(day=1) - timedelta(days=1)
            st.session_state.preset_start = last_month.replace(day=1)
            st.session_state.preset_end = last_month
    
    st.markdown("---")
    
    # Calendar date pickers
    st.markdown("**Or Choose Custom Dates:**")
    date_col1, date_col2, date_col3 = st.columns([2, 2, 1])
    
    # Use preset dates if available, otherwise default
    default_start = st.session_state.get('preset_start', today - timedelta(days=6))
    default_end = st.session_state.get('preset_end', today)
    
    with date_col1:
        start_date = st.date_input(
            "📅 From Date",
            value=default_start,
            min_value=FIRST_SALE_DATE,  # Can't select before first sale
            max_value=today,
            help="Select start date (data available from May 29, 2024)"
        )
    
    with date_col2:
        end_date = st.date_input(
            "📅 To Date",
            value=default_end,
            min_value=start_date,
            max_value=today,
            help="Select end date"
        )
    
    with date_col3:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        load_button = st.button("🔄 Load Data", type="primary", use_container_width=True)
    
    # Date range info
    days_selected = (end_date - start_date).days + 1
    st.info(f"📊 Selected: **{start_date.strftime('%b %d, %Y')}** to **{end_date.strftime('%b %d, %Y')}** ({days_selected} day{'s' if days_selected != 1 else ''})")
    
    # Load data when button clicked
    if load_button:
        with st.spinner("📥 Loading data from Google Drive..."):
            df, error = process_gdrive_files(
                service, 
                st.session_state.folder_id,
                pd.Timestamp(start_date),
                pd.Timestamp(end_date)
            )
            
            if error:
                st.error(error)
            elif not df.empty:
                st.session_state.df = df
                st.session_state.data_loaded = True
                st.success(f"✅ Loaded {len(df):,} records from {df['Date'].nunique()} days!")
                st.rerun()
            else:
                st.warning("No data found in selected range")

else:
    # Enhanced Welcome Screen
    st.markdown("""
    <div style='text-align: center; padding: 40px 20px;'>
        <div style='font-size: 80px; margin-bottom: 20px;'>🥖</div>
        <h1 style='color: #7D8570; font-family: Georgia, serif; margin-bottom: 10px;'>
            Welcome to Your Business Analytics
        </h1>
        <p style='color: #5A6B5E; font-size: 18px; margin-bottom: 40px;'>
            Your comprehensive sales analytics dashboard
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features overview
    st.markdown("### 📊 What You Can Do:")
    
    feat_col1, feat_col2, feat_col3 = st.columns(3)
    
    with feat_col1:
        st.markdown("""
        <div style='padding: 20px; background: linear-gradient(135deg, #B5C99A 0%, #7D8570 100%); 
                    border-radius: 12px; text-align: center; height: 180px;'>
            <div style='font-size: 48px; margin-bottom: 10px;'>📈</div>
            <h4 style='color: white; margin: 0;'>Smart Analytics</h4>
            <p style='color: #FAF9F6; font-size: 14px; margin-top: 8px;'>
                Daily, weekly & monthly views with automatic insights
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with feat_col2:
        st.markdown("""
        <div style='padding: 20px; background: linear-gradient(135deg, #A58A6F 0%, #7D8570 100%); 
                    border-radius: 12px; text-align: center; height: 180px;'>
            <div style='font-size: 48px; margin-bottom: 10px;'>🔄</div>
            <h4 style='color: white; margin: 0;'>Live Sync</h4>
            <p style='color: #FAF9F6; font-size: 14px; margin-top: 8px;'>
                Automatically loads data from your Google Drive folder
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with feat_col3:
        st.markdown("""
        <div style='padding: 20px; background: linear-gradient(135deg, #7D8570 0%, #5A6B5E 100%); 
                    border-radius: 12px; text-align: center; height: 180px;'>
            <div style='font-size: 48px; margin-bottom: 10px;'>⚡</div>
            <h4 style='color: white; margin: 0;'>Period Compare</h4>
            <p style='color: #FAF9F6; font-size: 14px; margin-top: 8px;'>
                Side-by-side comparison of any two time periods
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    
    # Getting Started
    st.markdown("### 🚀 Ready to Get Started?")
    
    start_col1, start_col2 = st.columns([2, 1])
    
    with start_col1:
        st.info("""
        **📅 Sales data available from May 29, 2024 onwards**
        
        Your dashboard is already connected to Google Drive and ready to load data.
        Simply select a date range above to begin!
        """)
        
        st.markdown("""
        **Quick Tips:**
        - 📆 Use the preset buttons (Today, Last 7 Days, etc.) for quick access
        - 🔍 Filter by category or product to drill down
        - ⚖️ Compare periods to track growth
        - 📊 Toggle between Revenue and Quantity views
        """)
    
    with start_col2:
        st.markdown("""
        <div style='padding: 25px; background: #F5F5F0; border-radius: 12px; border-left: 4px solid #7D8570;'>
            <h4 style='margin-top: 0; color: #5A6B5E;'>📖 Features</h4>
            <ul style='font-size: 14px; color: #5A6B5E; padding-left: 20px;'>
                <li>Hourly sales patterns</li>
                <li>Day-by-day breakdown</li>
                <li>Week-by-week trends</li>
                <li>Top products analysis</li>
                <li>Category performance</li>
                <li>Automated categorization</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    
    with col2:
        st.markdown("""
        ### ✨ Features:
        
        - 📊 Daily/Weekly/Monthly Reports
        - 🔍 Smart Filtering
        - 📈 Interactive Charts
        - 📥 Excel Export
        - 🔄 Auto-sync from Drive
        - ⚡ Fast Performance
        """)
    
    st.markdown("---")
    
    with st.expander("📖 How to find your Google Drive Folder ID"):
        st.markdown("""
        1. Open Google Drive in your browser
        2. Navigate to the folder with your daily sales files
        3. Click on the folder name in the address bar
        4. The URL looks like: `https://drive.google.com/drive/folders/1ABC123XYZ`
        5. Copy just the ID part after `/folders/`: `1ABC123XYZ`
        6. Paste it in the sidebar input field
        """)

st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px; color: #6B705C; font-size: 13px;'>
    <p style='margin: 0;'><strong>Your Business</strong> | Your Business Retail Sales Analytics Dashboard</p>
    <p style='margin: 5px 0 0 0; opacity: 0.7;'>Open Source Sales Dashboard - Contribute on GitHub!</p>
</div>
""", unsafe_allow_html=True)