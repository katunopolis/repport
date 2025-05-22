param(
    [Parameter(Mandatory=$true)]
    [string]$Email,
    
    [Parameter(Mandatory=$true)]
    [string]$Password
)

# Script location (assuming it's in the scripts folder)
$scriptPath = $PSScriptRoot
$backendPath = Split-Path -Parent $scriptPath

Write-Host "Creating Python script for password reset..."

# Create a temporary file
$tempScript = @"
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath('.'))

from app.models.user import User
from app.core.security import get_password_hash
from app.core.database import engine
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

async def fix_admin_password(email, password):
    """Fix the admin password to ensure it works correctly."""
    async with AsyncSession(engine) as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"Error: User {email} not found.")
            return
        
        # Update password with bcrypt hash to ensure compatibility
        user.hashed_password = get_password_hash(password)
        session.add(user)
        await session.commit()
        print(f"Password for {email} has been updated.")
        
        # Verify the user details
        await session.refresh(user)
        print(f"User ID: {user.id}")
        print(f"Email: {user.email}")
        print(f"Is Admin: {user.is_superuser}")
        print(f"Is Active: {user.is_active}")
        print(f"New Hash: {user.hashed_password[:20]}...")

if __name__ == "__main__":
    email = "$Email"
    password = "$Password"
    
    asyncio.run(fix_admin_password(email, password))
"@

# Save the script to a file in the container
$pythonScriptPath = "/app/scripts/temp_fix_admin.py"
$containerName = "repport-backend-1"

# Copy the Python script to the container
$tempScript | Out-File -FilePath "$scriptPath/temp_fix_admin.py" -Encoding utf8
Write-Host "Copying script to container..."
docker cp "$scriptPath/temp_fix_admin.py" "${containerName}:$pythonScriptPath"

# Execute the script in the container
Write-Host "Fixing admin user $Email..."
docker exec $containerName python $pythonScriptPath

# Clean up
Remove-Item "$scriptPath/temp_fix_admin.py"
Write-Host "Done!" 