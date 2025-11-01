"""
Database handler for Machine Efficiency Tracker
Manages SQLite database operations for machines, logs, and failures
"""
import sqlite3
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional


class DatabaseHandler:
    """Handles all database operations"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Machines table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS machines (
                machine_id TEXT PRIMARY KEY,
                machine_name TEXT NOT NULL,
                machine_type TEXT,
                location TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Machine logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS machine_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                machine_id TEXT NOT NULL,
                status TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                duration_minutes REAL,
                production_count INTEGER DEFAULT 0,
                notes TEXT,
                FOREIGN KEY (machine_id) REFERENCES machines(machine_id)
            )
        ''')
        
        # Failures table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS failures (
                failure_id INTEGER PRIMARY KEY AUTOINCREMENT,
                machine_id TEXT NOT NULL,
                failure_type TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                downtime_minutes REAL,
                resolution TEXT,
                FOREIGN KEY (machine_id) REFERENCES machines(machine_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_machine(self, machine_id: str, machine_name: str, 
                    machine_type: str, location: str):
        """Add a new machine"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO machines 
                (machine_id, machine_name, machine_type, location)
                VALUES (?, ?, ?, ?)
            ''', (machine_id, machine_name, machine_type, location))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def log_machine_status(self, machine_id: str, status: str, 
                          duration_minutes: float, production_count: int = 0,
                          notes: str = ""):
        """Log machine status change"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO machine_logs 
                (machine_id, status, duration_minutes, production_count, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (machine_id, status, duration_minutes, production_count, notes))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def log_failure(self, machine_id: str, failure_type: str, 
                    downtime_minutes: float, resolution: str = ""):
        """Log machine failure"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO failures 
                (machine_id, failure_type, downtime_minutes, resolution)
                VALUES (?, ?, ?, ?)
            ''', (machine_id, failure_type, downtime_minutes, resolution))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_all_machines(self) -> pd.DataFrame:
        """Get all machines"""
        conn = sqlite3.connect(self.db_path)
        try:
            df = pd.read_sql_query("SELECT * FROM machines ORDER BY machine_id", conn)
        except Exception as e:
            df = pd.DataFrame()
        finally:
            conn.close()
        return df
    
    def get_machine_logs(self, machine_id: Optional[str] = None, 
                        start_date: Optional[str] = None,
                        end_date: Optional[str] = None) -> pd.DataFrame:
        """Get machine logs with optional filters"""
        conn = sqlite3.connect(self.db_path)
        query = "SELECT * FROM machine_logs WHERE 1=1"
        params = []
        
        if machine_id:
            query += " AND machine_id = ?"
            params.append(machine_id)
        if start_date:
            query += " AND DATE(timestamp) >= ?"
            params.append(start_date)
        if end_date:
            query += " AND DATE(timestamp) <= ?"
            params.append(end_date)
        
        query += " ORDER BY timestamp DESC"
        
        try:
            df = pd.read_sql_query(query, conn, params=params)
        except Exception as e:
            df = pd.DataFrame()
        finally:
            conn.close()
        return df
    
    def get_failures(self, machine_id: Optional[str] = None,
                    start_date: Optional[str] = None,
                    end_date: Optional[str] = None) -> pd.DataFrame:
        """Get failure logs"""
        conn = sqlite3.connect(self.db_path)
        query = "SELECT * FROM failures WHERE 1=1"
        params = []
        
        if machine_id:
            query += " AND machine_id = ?"
            params.append(machine_id)
        if start_date:
            query += " AND DATE(timestamp) >= ?"
            params.append(start_date)
        if end_date:
            query += " AND DATE(timestamp) <= ?"
            params.append(end_date)
        
        query += " ORDER BY timestamp DESC"
        
        try:
            df = pd.read_sql_query(query, conn, params=params)
        except Exception as e:
            df = pd.DataFrame()
        finally:
            conn.close()
        return df
    
    def delete_machine(self, machine_id: str):
        """Delete a machine and all its associated logs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM machine_logs WHERE machine_id = ?", (machine_id,))
            cursor.execute("DELETE FROM failures WHERE machine_id = ?", (machine_id,))
            cursor.execute("DELETE FROM machines WHERE machine_id = ?", (machine_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()


