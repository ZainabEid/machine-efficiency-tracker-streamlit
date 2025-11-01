# ⚙️ Machine Efficiency Tracker

A comprehensive Streamlit application for monitoring machine efficiency, tracking operational status, and analyzing productivity metrics in real-time.

## 🎯 Features

### Core Functionality
- **Real-time Machine Monitoring** - Track machine status (Running, Idle, Maintenance, Failed, Offline)
- **Efficiency Calculations** - Calculate running time percentage, idle time, and downtime
- **Productivity Metrics** - Monitor production output and production per hour
- **Failure Tracking** - Log and analyze machine failures and downtime
- **Advanced Analytics** - Visualize trends, compare machines, and identify patterns

### Key Metrics
- ⚡ Running Time Percentage
- 📦 Production Output & Rate
- ⚠️ Daily Failure Rate
- 🔧 MTBF (Mean Time Between Failures)
- ⏱️ MTTR (Mean Time To Repair)
- 📊 OEE (Overall Equipment Effectiveness)

### Visualizations
- Machine status overview
- Running time comparison charts
- Failure analysis graphs
- Production trends over time
- Status distribution pie charts
- Daily activity timelines

## 📁 Project Structure

```
machine_efficiency_tracker_streamlit/
├── app.py                          # Main Streamlit application
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── machine_efficiency.db          # SQLite database (auto-generated)
│
├── database/
│   ├── __init__.py
│   └── db_handler.py              # Database operations
│
├── utils/
│   ├── __init__.py
│   ├── calculations.py            # Efficiency calculations
│   └── data_generator.py          # Sample data generator
│
├── models/
│   └── __init__.py                # Data models
│
└── components/
    └── __init__.py                # UI components
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or download the project**
   ```bash
   cd machine_efficiency_tracker_streamlit
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Access the application**
   - The app will automatically open in your default browser
   - Default URL: http://localhost:8501

## 📖 Usage Guide

### 1. First-Time Setup

#### Option A: Add Machines Manually
1. Navigate to **"➕ Add Machine"** in the sidebar
2. Fill in the machine details:
   - Machine ID (e.g., M001)
   - Machine Name (e.g., CNC Machine 1)
   - Machine Type (CNC, Lathe, Mill, etc.)
   - Location (e.g., Floor A, Section 1)
3. Click **"Add Machine"**

#### Option B: Generate Sample Data
1. Navigate to **"🎲 Generate Sample Data"**
2. Choose the number of machines (1-20)
3. Select days of history (1-90)
4. Click **"Generate Sample Data"**
5. Sample machines, logs, and failures will be created automatically

### 2. Logging Machine Activity

#### Log Status Changes
1. Go to **"📝 Add Log"** → **"Status Log"** tab
2. Select the machine
3. Choose status (Running, Idle, Maintenance, Failed, Offline)
4. Enter duration in minutes
5. Add production count (if applicable)
6. Add notes (optional)
7. Click **"Add Log"**

#### Log Failures
1. Go to **"📝 Add Log"** → **"Failure Log"** tab
2. Select the machine
3. Enter failure type
4. Enter downtime in minutes
5. Describe the resolution
6. Click **"Log Failure"**

### 3. Monitoring Dashboard

The **"📊 Dashboard"** provides:
- Overall metrics across all machines
- Machine status overview table
- Running time comparison chart
- Failure count by machine
- Status distribution
- Production trends

**Date Range Filter**: Use the sidebar date selector to filter data by date range.

### 4. Machine Details

1. Navigate to **"🤖 Machine Details"**
2. Select a machine from the dropdown
3. View detailed metrics:
   - Running time percentage
   - Total production
   - Production per hour
   - Failure count
   - Runtime hours
   - MTBF (Mean Time Between Failures)
4. Explore tabs:
   - **Recent Logs**: View and download activity logs
   - **Failures**: Analyze failure history and types
   - **Charts**: Visualize status distribution and timeline

### 5. Advanced Analytics

The **"📈 Analytics"** page offers:
- Production analysis and trends
- Efficiency comparison across machines
- Failure trend analysis
- Top failure types
- Downtime analysis by machine

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Database location
DB_PATH = "machine_efficiency.db"

# Machine status labels
MACHINE_STATUS = {
    "RUNNING": "🟢 Running",
    "IDLE": "🟡 Idle",
    # ... customize as needed
}

# Time settings
SHIFT_HOURS = 8
SHIFTS_PER_DAY = 3

# KPI thresholds
MIN_EFFICIENCY = 75  # Minimum acceptable efficiency %
MAX_FAILURE_RATE = 5  # Maximum failures per day
```

## 📊 Key Performance Indicators (KPIs)

### Running Time Percentage
```
Running Time % = (Total Running Time / Total Time) × 100
```

### Production Per Hour
```
Production/Hour = Total Production / Total Running Hours
```

### Daily Failure Rate
```
Avg Daily Failures = Total Failures / Days Tracked
```

### MTBF (Mean Time Between Failures)
```
MTBF = Total Running Hours / Number of Failures
```

### MTTR (Mean Time To Repair)
```
MTTR = Total Downtime Hours / Number of Failures
```

### OEE (Overall Equipment Effectiveness)
```
OEE = Availability × Performance × Quality
```

## 🗃️ Database Schema

### Tables

#### machines
- `machine_id` (TEXT, PRIMARY KEY) - Unique machine identifier
- `machine_name` (TEXT) - Machine name
- `machine_type` (TEXT) - Type of machine
- `location` (TEXT) - Physical location
- `created_at` (TIMESTAMP) - Creation timestamp

#### machine_logs
- `log_id` (INTEGER, PRIMARY KEY) - Auto-incrementing log ID
- `machine_id` (TEXT) - Foreign key to machines
- `status` (TEXT) - Machine status
- `timestamp` (TIMESTAMP) - Log timestamp
- `duration_minutes` (REAL) - Duration of the status
- `production_count` (INTEGER) - Units produced
- `notes` (TEXT) - Additional notes

#### failures
- `failure_id` (INTEGER, PRIMARY KEY) - Auto-incrementing failure ID
- `machine_id` (TEXT) - Foreign key to machines
- `failure_type` (TEXT) - Type of failure
- `timestamp` (TIMESTAMP) - Failure timestamp
- `downtime_minutes` (REAL) - Downtime duration
- `resolution` (TEXT) - Resolution description

## 🔌 Integration Options

### Future Enhancements
- **API Integration**: Connect to machine sensors or PLCs for real-time data
- **MQTT Support**: Subscribe to IoT device messages
- **Alert System**: Email/SMS notifications for failures or low efficiency
- **User Authentication**: Multi-user access with role-based permissions
- **Export Features**: Generate PDF reports and Excel exports
- **Predictive Maintenance**: ML-based failure prediction
- **Mobile App**: Responsive mobile interface

## 🛠️ Troubleshooting

### Database Issues
If you encounter database errors:
```bash
# Delete the database and restart
rm machine_efficiency.db
streamlit run app.py
```

### Port Already in Use
If port 8501 is busy:
```bash
streamlit run app.py --server.port 8502
```

### Dependencies Not Found
Reinstall requirements:
```bash
pip install --upgrade -r requirements.txt
```

## 📝 Sample Data Generator

Generate test data programmatically:

```python
from database.db_handler import DatabaseHandler
from utils.data_generator import DataGenerator
import config

# Initialize
db = DatabaseHandler(config.DB_PATH)
generator = DataGenerator(db)

# Generate complete dataset
generator.generate_complete_dataset(
    num_machines=5,  # Number of machines
    days=14          # Days of history
)
```

Or run standalone:
```bash
python -m utils.data_generator
```

## 🤝 Contributing

To extend the application:

1. **Add New Calculations**: Edit `utils/calculations.py`
2. **Modify Database**: Update `database/db_handler.py`
3. **Customize UI**: Edit `app.py` or create new components in `components/`
4. **Add Machine Types**: Update `config.py`

## 📄 License

This project is open-source and available for modification and distribution.

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the code comments
3. Regenerate sample data to test functionality

## 🎓 Best Practices

### Data Entry
- Log status changes regularly for accurate metrics
- Include detailed notes for maintenance and failures
- Use consistent failure type descriptions

### Monitoring
- Set appropriate date ranges for meaningful analysis
- Review dashboard daily for efficiency trends
- Investigate machines with high failure rates

### Maintenance
- Back up the database file regularly
- Archive old data periodically
- Monitor disk space usage

## 📈 Version History

### v1.0.0 (Initial Release)
- Core machine monitoring functionality
- Efficiency calculations and analytics
- SQLite database integration
- Interactive Streamlit dashboard
- Sample data generator
- Export capabilities

---

**Built with ❤️ using Streamlit**

*For optimal performance, ensure Python 3.8+ and all dependencies are up to date.*


