"""
Sample data generator for testing Machine Efficiency Tracker
Generates realistic sample data for machines, logs, and failures
"""
import random
from datetime import datetime, timedelta
from database.db_handler import DatabaseHandler
import config


class DataGenerator:
    """Generates sample data for testing"""
    
    def __init__(self, db_handler: DatabaseHandler):
        self.db = db_handler
        
        # Sample data configurations
        self.machine_types = ["CNC", "Lathe", "Mill", "Press", "Assembly", "Packaging"]
        self.locations = ["Floor A, Section 1", "Floor A, Section 2", "Floor B, Section 1", 
                         "Floor B, Section 2", "Warehouse", "Assembly Line"]
        self.failure_types = ["Mechanical Failure", "Electrical Issue", "Sensor Malfunction",
                            "Software Error", "Overheating", "Calibration Error", 
                            "Material Jam", "Power Outage"]
        self.resolutions = ["Replaced part", "Reset system", "Cleaned sensors", 
                          "Updated software", "Cooled down system", "Recalibrated",
                          "Cleared jam", "Restored power"]
    
    def generate_sample_machines(self, count: int = 5):
        """Generate sample machines"""
        print(f"Generating {count} sample machines...")
        
        for i in range(1, count + 1):
            machine_id = f"M{i:03d}"
            machine_type = random.choice(self.machine_types)
            machine_name = f"{machine_type} Machine {i}"
            location = random.choice(self.locations)
            
            try:
                self.db.add_machine(machine_id, machine_name, machine_type, location)
                print(f"  ✓ Added {machine_id}: {machine_name}")
            except Exception as e:
                print(f"  ✗ Error adding {machine_id}: {e}")
    
    def generate_sample_logs(self, days: int = 7, logs_per_day: int = 10):
        """Generate sample machine logs"""
        machines_df = self.db.get_all_machines()
        
        if machines_df.empty:
            print("No machines found. Please generate machines first.")
            return
        
        print(f"Generating sample logs for {days} days...")
        total_logs = 0
        
        for _, machine in machines_df.iterrows():
            machine_id = machine['machine_id']
            
            for day in range(days):
                date = datetime.now() - timedelta(days=days-day)
                
                for _ in range(logs_per_day):
                    # Random status with weighted probabilities
                    status_choices = ['RUNNING', 'RUNNING', 'RUNNING', 'RUNNING', 
                                    'IDLE', 'IDLE', 'MAINTENANCE', 'FAILED']
                    status = random.choice(status_choices)
                    
                    # Duration based on status
                    if status == 'RUNNING':
                        duration = random.uniform(30, 180)  # 30-180 minutes
                        production = random.randint(20, 150)
                    elif status == 'IDLE':
                        duration = random.uniform(10, 60)
                        production = 0
                    elif status == 'MAINTENANCE':
                        duration = random.uniform(60, 240)
                        production = 0
                    else:  # FAILED
                        duration = random.uniform(30, 120)
                        production = 0
                    
                    try:
                        self.db.log_machine_status(machine_id, status, duration, production)
                        total_logs += 1
                    except Exception as e:
                        print(f"  ✗ Error logging for {machine_id}: {e}")
        
        print(f"  ✓ Generated {total_logs} logs")
    
    def generate_sample_failures(self, count: int = 20):
        """Generate sample failure logs"""
        machines_df = self.db.get_all_machines()
        
        if machines_df.empty:
            print("No machines found. Please generate machines first.")
            return
        
        print(f"Generating {count} sample failures...")
        
        for i in range(count):
            machine_id = random.choice(machines_df['machine_id'].tolist())
            failure_type = random.choice(self.failure_types)
            downtime = random.uniform(15, 240)  # 15 minutes to 4 hours
            resolution = random.choice(self.resolutions)
            
            try:
                self.db.log_failure(machine_id, failure_type, downtime, resolution)
            except Exception as e:
                print(f"  ✗ Error logging failure: {e}")
        
        print(f"  ✓ Generated {count} failures")
    
    def generate_complete_dataset(self, num_machines: int = 5, days: int = 7):
        """Generate a complete dataset with machines, logs, and failures"""
        print("=" * 50)
        print("Generating Complete Sample Dataset")
        print("=" * 50)
        
        self.generate_sample_machines(num_machines)
        self.generate_sample_logs(days=days, logs_per_day=15)
        self.generate_sample_failures(count=num_machines * 3)
        
        print("=" * 50)
        print("Sample data generation complete!")
        print("=" * 50)


def main():
    """Main function for standalone execution"""
    db = DatabaseHandler(config.DB_PATH)
    generator = DataGenerator(db)
    
    # Generate complete dataset
    generator.generate_complete_dataset(num_machines=5, days=14)


if __name__ == "__main__":
    main()


