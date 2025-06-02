# PostgreSQL Migration Guide

## Overview

This document describes the migration from SQLite to PostgreSQL in the Repport project. The migration includes setting up PostgreSQL as a Docker service, updating the application configuration, and migrating existing data.

## Changes Made

### 1. Docker Configuration

Added PostgreSQL service to `docker-compose.yml`:

```yaml
services:
  db:
    image: postgres:15
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=repport
      - POSTGRES_PASSWORD=repport
      - POSTGRES_DB=repport
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 2. Backend Configuration Updates

#### Database URL Configuration (`backend/app/core/config.py`)
```python
DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://repport:repport@localhost:5432/repport")
DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", 20))
DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", 10))
DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", 30))
DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", 1800))
```

#### Database Engine Configuration (`backend/app/core/database.py`)
```python
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # Log SQL queries - set to False in production
    future=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE
)
```

### 3. Dependencies Added

Added to `backend/requirements.txt`:
```
asyncpg==0.29.0
psycopg2-binary==2.9.9
```

## Migration Process

### Migration Scripts

1. `backend/scripts/migrate_to_postgres.py`: Main migration script that:
   - Reads data from SQLite database
   - Creates tables in PostgreSQL
   - Migrates data to PostgreSQL
   - Verifies the migration

2. `backend/scripts/migrate_db.ps1` (Windows) and `backend/scripts/migrate_db.sh` (Unix): Helper scripts to run the migration in Docker environment

### Running the Migration

#### Windows:
```powershell
cd backend/scripts
./migrate_db.ps1
```

#### Unix:
```bash
cd backend/scripts
chmod +x migrate_db.sh
./migrate_db.sh
```

### Migration Steps

1. **Data Reading**: Reads all tables and data from SQLite
2. **Table Creation**: Creates new tables in PostgreSQL using SQLModel definitions
3. **Data Migration**: Transfers all data to PostgreSQL
4. **Verification**: Ensures all data was migrated correctly

## Verification

The migration script performs the following checks:
- Compares user count between SQLite and PostgreSQL
- Compares ticket count between SQLite and PostgreSQL
- Verifies data integrity and relationships

## Troubleshooting

### Common Issues

1. **Connection Issues**:
   - Ensure PostgreSQL container is running
   - Check if the database URL is correct
   - Verify network connectivity between services

2. **Data Type Mismatches**:
   - The migration script handles datetime conversions
   - Ensures proper handling of NULL values
   - Maintains data relationships

3. **Permission Issues**:
   - Ensure the database user has proper permissions
   - Check volume mount permissions in Docker

### Logging

The migration script includes comprehensive logging:
- Logs all steps of the migration process
- Records any errors or inconsistencies
- Provides detailed progress information

## Rollback Plan

In case of migration failure:
1. The SQLite database remains untouched
2. PostgreSQL tables are dropped and recreated if needed
3. Original data can be accessed from SQLite backup

## Post-Migration

After successful migration:
1. Update environment variables to use PostgreSQL
2. Test application functionality
3. Monitor database performance
4. Keep SQLite database as backup until verification is complete

## Production Considerations

1. **Backup**:
   - Take backup of SQLite database before migration
   - Use PostgreSQL backup tools (pg_dump) after migration

2. **Performance**:
   - Monitor connection pool settings
   - Adjust pool size based on load
   - Consider adding indexes if needed

3. **Security**:
   - Change default passwords
   - Restrict network access
   - Use SSL for connections

## Future Improvements

1. **Monitoring**:
   - Add database monitoring
   - Set up performance tracking
   - Implement query optimization

2. **Maintenance**:
   - Regular backups
   - Index maintenance
   - Query optimization

3. **Scaling**:
   - Connection pool optimization
   - Read replicas if needed
   - Partitioning for large tables

# PostgreSQL Database Management

This document describes the database backup and restore procedures for the Repport application.

## Backup Storage

### Location
The backups are stored in a Docker volume named `db_backups`, which is managed by Docker and not directly visible in the project's file structure. This provides:
- Data persistence across container restarts
- Isolation from the application code
- Better security and access control

### Directory Structure
Inside the backup container, backups are stored at `/app/backups/` with the following structure:
```
/app/backups/
├── repport_YYYYMMDD_HHMMSS.dump
├── repport_YYYYMMDD_HHMMSS.dump
└── ...
```

### Accessing Backups
Since backups are stored in a Docker volume, they are not directly accessible in your project directory. To work with backups:

1. **List Backups**:
```bash
docker exec repport-backup-1 ls -l /app/backups
```

2. **Copy Backups to Local Machine**:
```bash
# Create a local directory for backups
mkdir -p ./database/backups

# Copy all backups from container to local machine
docker cp repport-backup-1:/app/backups/. ./database/backups/
```

3. **Copy a Specific Backup**:
```bash
docker cp repport-backup-1:/app/backups/repport_YYYYMMDD_HHMMSS.dump ./database/backups/
```

## Automatic Backups

The application uses a Python-based backup solution that automatically backs up the PostgreSQL database every 24 hours. Backups are kept for 7 days, after which they are automatically deleted.

### Backup Implementation

The backup solution consists of two main Python scripts:
1. `database/backup.py`: Handles automated backups and cleanup
2. `database/restore.py`: Manages backup listing and restoration

These scripts are run in a dedicated backup container using the `python:3.11-slim` base image with PostgreSQL client tools installed.

### Backup Schedule

- Frequency: Every 24 hours
- Retention: 7 days (configurable in backup.py)
- Format: PostgreSQL custom format (compressed)

## Manual Backup Operations

### Creating a Manual Backup

To create a manual backup:
```bash
docker exec repport-backup-1 python backup.py
```

### Listing Available Backups

To see all available backups:
```bash
docker exec repport-backup-1 python restore.py
```
This will show a list of backups with their timestamps.

### Restoring from Backup

1. First, list available backups:
```bash
docker exec repport-backup-1 python restore.py
```

2. Then restore using the desired backup file:
```bash
docker exec repport-backup-1 python restore.py repport_YYYYMMDD_HHMMSS.dump
```
Replace `YYYYMMDD_HHMMSS` with the actual timestamp of the backup you want to restore.

### Backup File Naming Convention

Backup files follow this naming pattern:
- Format: `repport_YYYYMMDD_HHMMSS.dump`
- Example: `repport_20250602_105351.dump`
  - Date: 2025-06-02
  - Time: 10:53:51 UTC

## Implementation Details

### Backup Script (backup.py)

The backup script provides the following features:
- Automated backups every 24 hours
- Configurable retention period (default: 7 days)
- Compressed backups using PostgreSQL's custom format
- Detailed logging of backup operations
- Automatic cleanup of old backups
- Error handling and reporting

### Restore Script (restore.py)

The restore script provides:
- List of available backups
- Validation of backup files
- Safe restore with --clean and --if-exists flags
- Detailed logging of restore operations
- Error handling and reporting

## Docker Configuration

The backup solution uses a dedicated service in docker-compose.yml:

```yaml
services:
  backup:
    build:
      context: ./database
      dockerfile: Dockerfile.backup
    volumes:
      - db_backups:/app/backups
    depends_on:
      - db

volumes:
  db_backups:
```

## Railway Deployment

When deploying to Railway:

1. The backup volume (`db_backups`) should be configured as a persistent volume
2. The backup service will automatically run and create daily backups
3. Backups can be accessed through Railway's volume management interface

## Security Considerations

1. **Backup Security**:
   - Backup files contain sensitive data and should be protected
   - Access to the backup volume should be restricted
   - Consider encrypting backup files for additional security
   - Never commit backup files to version control

2. **Monitoring**:
   - Monitor backup success/failure through container logs
   - Set up alerts for backup failures
   - Regularly verify backup integrity

3. **Best Practices**:
   - Keep backup files outside of version control
   - Use secure methods to transfer backup files
   - Regularly test the restore process
   - Document and version your backup procedures

## Troubleshooting

If you encounter issues with backups:

1. Check the backup container logs:
```bash
docker logs repport-backup-1
```

2. Verify the backup service is running:
```bash
docker ps | grep backup
```

3. Check backup directory permissions:
```bash
docker exec repport-backup-1 ls -la /app/backups
```

4. Common issues and solutions:
   - If backups are not being created, check the logs for error messages
   - If restore fails, ensure the backup file exists and is readable
   - If the backup container stops, check for any Python exceptions in the logs

## Best Practices

1. **Regular Testing**:
   - Periodically test the restore process
   - Verify backup integrity
   - Practice recovery procedures

2. **Monitoring**:
   - Monitor backup success/failure
   - Track backup file sizes
   - Monitor available disk space

3. **Documentation**:
   - Keep track of backup schedules
   - Document restore procedures
   - Maintain recovery runbooks 