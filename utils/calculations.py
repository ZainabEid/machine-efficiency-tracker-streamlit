"""
Efficiency calculations for Machine Efficiency Tracker
Calculates various KPIs like running time %, failure rates, productivity, and OEE
"""
import pandas as pd
from typing import Dict, Tuple


class EfficiencyCalculator:
    """Handles all efficiency and productivity calculations"""
    
    @staticmethod
    def calculate_running_time_percentage(logs_df: pd.DataFrame) -> float:
        """
        Calculate percentage of time machine was running
        
        Args:
            logs_df: DataFrame with machine logs
            
        Returns:
            Percentage of running time (0-100)
        """
        if logs_df.empty:
            return 0.0
        
        running_time = logs_df[logs_df['status'] == 'RUNNING']['duration_minutes'].sum()
        total_time = logs_df['duration_minutes'].sum()
        
        if total_time == 0:
            return 0.0
        
        return (running_time / total_time) * 100
    
    @staticmethod
    def calculate_idle_time_percentage(logs_df: pd.DataFrame) -> float:
        """Calculate percentage of idle time"""
        if logs_df.empty:
            return 0.0
        
        idle_time = logs_df[logs_df['status'] == 'IDLE']['duration_minutes'].sum()
        total_time = logs_df['duration_minutes'].sum()
        
        if total_time == 0:
            return 0.0
        
        return (idle_time / total_time) * 100
    
    @staticmethod
    def calculate_downtime_percentage(logs_df: pd.DataFrame) -> float:
        """Calculate percentage of downtime (FAILED + MAINTENANCE)"""
        if logs_df.empty:
            return 0.0
        
        downtime = logs_df[logs_df['status'].isin(['FAILED', 'MAINTENANCE'])]['duration_minutes'].sum()
        total_time = logs_df['duration_minutes'].sum()
        
        if total_time == 0:
            return 0.0
        
        return (downtime / total_time) * 100
    
    @staticmethod
    def calculate_daily_failure_rate(failures_df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate daily failure rate statistics
        
        Args:
            failures_df: DataFrame with failure logs
            
        Returns:
            Dictionary with failure statistics
        """
        if failures_df.empty:
            return {
                "avg_failures_per_day": 0.0,
                "total_failures": 0,
                "max_failures_per_day": 0,
                "days_tracked": 0
            }
        
        failures_df['date'] = pd.to_datetime(failures_df['timestamp']).dt.date
        daily_counts = failures_df.groupby('date').size()
        
        return {
            "avg_failures_per_day": round(daily_counts.mean(), 2),
            "total_failures": len(failures_df),
            "max_failures_per_day": int(daily_counts.max()),
            "days_tracked": len(daily_counts)
        }
    
    @staticmethod
    def calculate_productivity(logs_df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate machine productivity metrics
        
        Args:
            logs_df: DataFrame with machine logs
            
        Returns:
            Dictionary with productivity metrics
        """
        if logs_df.empty:
            return {
                "total_production": 0,
                "production_per_hour": 0.0,
                "total_runtime_hours": 0.0,
                "total_runtime_minutes": 0.0
            }
        
        running_logs = logs_df[logs_df['status'] == 'RUNNING']
        total_production = running_logs['production_count'].sum()
        total_runtime_minutes = running_logs['duration_minutes'].sum()
        total_runtime_hours = total_runtime_minutes / 60
        
        production_per_hour = (total_production / total_runtime_hours 
                              if total_runtime_hours > 0 else 0)
        
        return {
            "total_production": int(total_production),
            "production_per_hour": round(production_per_hour, 2),
            "total_runtime_hours": round(total_runtime_hours, 2),
            "total_runtime_minutes": round(total_runtime_minutes, 2)
        }
    
    @staticmethod
    def calculate_oee(logs_df: pd.DataFrame, failures_df: pd.DataFrame,
                     ideal_cycle_time: float, planned_production_time: float) -> Dict[str, float]:
        """
        Calculate Overall Equipment Effectiveness (OEE)
        OEE = Availability × Performance × Quality
        
        Args:
            logs_df: DataFrame with machine logs
            failures_df: DataFrame with failure logs
            ideal_cycle_time: Ideal time to produce one unit (minutes)
            planned_production_time: Total planned production time (minutes)
            
        Returns:
            Dictionary with OEE components
        """
        if logs_df.empty:
            return {
                "availability": 0,
                "performance": 0,
                "quality": 100,
                "oee": 0
            }
        
        # Availability = (Operating Time / Planned Production Time)
        total_downtime = failures_df['downtime_minutes'].sum() if not failures_df.empty else 0
        operating_time = planned_production_time - total_downtime
        availability = (operating_time / planned_production_time * 100) if planned_production_time > 0 else 0
        
        # Performance = (Actual Production / Target Production)
        running_logs = logs_df[logs_df['status'] == 'RUNNING']
        actual_production = running_logs['production_count'].sum()
        target_production = operating_time / ideal_cycle_time if ideal_cycle_time > 0 else 0
        performance = (actual_production / target_production * 100) if target_production > 0 else 0
        
        # Quality (assuming 100% for now - can be extended with defect tracking)
        quality = 100
        
        # OEE
        oee = (availability * performance * quality) / 10000
        
        return {
            "availability": round(min(availability, 100), 2),
            "performance": round(min(performance, 100), 2),  # Cap at 100%
            "quality": round(quality, 2),
            "oee": round(oee, 2)
        }
    
    @staticmethod
    def calculate_mtbf(failures_df: pd.DataFrame, total_runtime_hours: float) -> float:
        """
        Calculate Mean Time Between Failures (MTBF)
        
        Args:
            failures_df: DataFrame with failure logs
            total_runtime_hours: Total operating time in hours
            
        Returns:
            MTBF in hours
        """
        if failures_df.empty or total_runtime_hours == 0:
            return 0.0
        
        num_failures = len(failures_df)
        mtbf = total_runtime_hours / num_failures
        
        return round(mtbf, 2)
    
    @staticmethod
    def calculate_mttr(failures_df: pd.DataFrame) -> float:
        """
        Calculate Mean Time To Repair (MTTR)
        
        Args:
            failures_df: DataFrame with failure logs
            
        Returns:
            MTTR in hours
        """
        if failures_df.empty:
            return 0.0
        
        total_downtime_minutes = failures_df['downtime_minutes'].sum()
        num_failures = len(failures_df)
        
        mttr_hours = (total_downtime_minutes / 60) / num_failures
        
        return round(mttr_hours, 2)
    
    @staticmethod
    def get_status_distribution(logs_df: pd.DataFrame) -> Dict[str, float]:
        """
        Get distribution of time spent in each status
        
        Args:
            logs_df: DataFrame with machine logs
            
        Returns:
            Dictionary with status percentages
        """
        if logs_df.empty:
            return {}
        
        total_time = logs_df['duration_minutes'].sum()
        if total_time == 0:
            return {}
        
        status_time = logs_df.groupby('status')['duration_minutes'].sum()
        status_pct = (status_time / total_time * 100).round(2)
        
        return status_pct.to_dict()


