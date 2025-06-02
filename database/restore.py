#!/usr/bin/env python3

import os
import sys
import logging
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseRestore:
    def __init__(self):
        self.backup_dir = Path("/app/backups")
        self.db_params = {
            "host": "db",
            "user": "repport",
            "dbname": "repport",
            "port": "5432"
        }

    def list_backups(self):
        """List all available backup files."""
        try:
            backups = sorted(self.backup_dir.glob("*.dump"))
            if not backups:
                logger.info("No backup files found")
                return []
            
            logger.info("Available backups:")
            for backup in backups:
                logger.info(f"- {backup.name}")
            return backups
        
        except Exception as e:
            logger.error(f"Error listing backups: {str(e)}")
            return []

    def restore_backup(self, backup_file):
        """Restore database from a backup file."""
        try:
            backup_path = self.backup_dir / backup_file if isinstance(backup_file, str) else backup_file
            
            if not backup_path.exists():
                logger.error(f"Backup file not found: {backup_path}")
                return False

            # Build the pg_restore command
            cmd = [
                "pg_restore",
                "-h", self.db_params["host"],
                "-U", self.db_params["user"],
                "-d", self.db_params["dbname"],
                "-p", self.db_params["port"],
                "--clean",
                "--if-exists",
                str(backup_path)
            ]

            # Execute restore
            logger.info(f"Starting restore from {backup_path}")
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                logger.info("Restore completed successfully")
                return True
            else:
                logger.error(f"Restore failed: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Error during restore: {str(e)}")
            return False

def main():
    """Main function to handle restore process."""
    restore = DatabaseRestore()
    
    if len(sys.argv) < 2:
        # If no backup file specified, list available backups
        restore.list_backups()
        logger.info("\nUsage: python restore.py <backup_file>")
        sys.exit(1)

    backup_file = sys.argv[1]
    restore.restore_backup(backup_file)

if __name__ == "__main__":
    main() 