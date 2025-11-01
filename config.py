"""
Configuration settings for Machine Efficiency Tracker
"""
import os

# Database Configuration
DB_PATH = "machine_efficiency.db"

# Machine Status
MACHINE_STATUS = {
    "RUNNING": "🟢 Running",
    "IDLE": "🟡 Idle",
    "MAINTENANCE": "🟠 Maintenance",
    "FAILED": "🔴 Failed",
    "OFFLINE": "⚫ Offline"
}

# Time Settings
SHIFT_HOURS = 8  # Hours per shift
SHIFTS_PER_DAY = 3

# KPI Thresholds
MIN_EFFICIENCY = 75  # Minimum acceptable efficiency %
MAX_FAILURE_RATE = 5  # Maximum acceptable failures per day

# OEE Settings
DEFAULT_IDEAL_CYCLE_TIME = 1.0  # minutes per unit
DEFAULT_PLANNED_PRODUCTION_TIME = SHIFT_HOURS * 60  # minutes per shift

