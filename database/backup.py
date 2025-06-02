#!/usr/bin/env python3

import os
import sys
import time
import logging
import subprocess
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseBackup:
    def __init__(self):
        self.backup_dir = Path("/app/backups")
        self.db_params = {
            "host": "db",
            "user": "repport",
            "dbname": "repport",
            "port": "5432"
        }
        self.retention_days = 7

    def create_backup(self):
        """Create a new database backup."""
        try:
            # Ensure backup directory exists
            self.backup_dir.mkdir(parents=True, exist_ok=True)

            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"repport_{timestamp}.dump"

            # Build the pg_dump command
            cmd = [
                "pg_dump",
                "-h", self.db_params["host"],
                "-U", self.db_params["user"],
                "-d", self.db_params["dbname"],
                "-p", self.db_params["port"],
                "-F", "c",  # Custom format
                "-f", str(backup_file)
            ]

            # Execute backup
            logger.info(f"Starting backup to {backup_file}")
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                logger.info("Backup completed successfully")
                return True
            else:
                logger.error(f"Backup failed: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Error during backup: {str(e)}")
            return False

    def cleanup_old_backups(self):
        """Remove backups older than retention_days."""
        try:
            current_time = time.time()
            for backup_file in self.backup_dir.glob("*.dump"):
                file_age_days = (current_time - backup_file.stat().st_mtime) / (24 * 3600)
                if file_age_days > self.retention_days:
                    backup_file.unlink()
                    logger.info(f"Deleted old backup: {backup_file}")

        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

def main():
    """Main function to run backup process."""
    backup = DatabaseBackup()
    
    while True:
        if backup.create_backup():
            backup.cleanup_old_backups()
        
        # Sleep for 24 hours
        logger.info("Waiting 24 hours until next backup...")
        time.sleep(24 * 3600)

if __name__ == "__main__":
    main() 