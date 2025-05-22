"""
Script to standardize password hashing in the database.
This script ensures all users have bcrypt-hashed passwords for consistent authentication.
"""
import asyncio
import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.user import User
from app.core.security import get_password_hash
from app.core.database import engine
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from passlib.context import CryptContext

# Create a test password context to identify hash types
pwd_context = CryptContext(schemes=["bcrypt", "argon2", "pbkdf2_sha256", "des_crypt"], deprecated="auto")

async def standardize_hash_formats():
    """Standardize all user password hashes to bcrypt format."""
    logger.info("Starting password hash standardization process")
    
    async with AsyncSession(engine) as session:
        # Get all users
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        logger.info(f"Found {len(users)} users in the database")
        
        # Track stats for reporting
        stats = {
            "total": len(users),
            "already_bcrypt": 0,
            "converted": 0,
            "errors": 0
        }
        
        # Create a standard test password for hash identification
        # (We don't need the actual passwords, just to identify hash types)
        test_password = "StandardTestPassword123!"
        bcrypt_test_hash = get_password_hash(test_password)
        
        # Make sure our standard hashing produces bcrypt hashes
        if not bcrypt_test_hash.startswith('$2b$'):
            logger.error(f"ERROR: The standard hashing function is not producing bcrypt hashes!")
            logger.error(f"Test hash: {bcrypt_test_hash}")
            return
        
        logger.info(f"Verified standard hashing produces bcrypt format: {bcrypt_test_hash[:20]}...")
        
        # Process each user
        for user in users:
            try:
                # Skip already standardized users (bcrypt hashes start with $2b$)
                if user.hashed_password.startswith('$2b$'):
                    logger.info(f"User {user.id} ({user.email}) already has bcrypt hash")
                    stats["already_bcrypt"] += 1
                    continue
                
                # For non-bcrypt hashes, we can't convert directly (we don't know the original password)
                # So we'll set a temporary known password, then update the database
                logger.info(f"User {user.id} ({user.email}) has non-bcrypt hash: {user.hashed_password[:20]}...")
                
                # Save the hash type for reporting
                hash_type = "unknown"
                try:
                    hash_info = pwd_context.identify(user.hashed_password)
                    hash_type = hash_info if hash_info else "unknown"
                except Exception as e:
                    hash_type = f"error identifying: {str(e)}"
                
                logger.info(f"Hash type identified as: {hash_type}")
                
                # Generate a bcrypt hash for this user
                default_password = f"ResetPassword_{user.id}_{user.email.split('@')[0]}"
                new_hash = get_password_hash(default_password)
                
                # Update the user's password hash
                user.hashed_password = new_hash
                session.add(user)
                
                # Record that we changed this user's password
                with open("reset_passwords.txt", "a") as f:
                    f.write(f"User {user.id} ({user.email}): {default_password}\n")
                
                logger.info(f"Updated user {user.id} ({user.email}) to bcrypt hash: {new_hash[:20]}...")
                stats["converted"] += 1
                
            except Exception as e:
                logger.error(f"Error processing user {user.email}: {str(e)}")
                stats["errors"] += 1
        
        # Commit all changes
        await session.commit()
        
        # Report results
        logger.info("=" * 50)
        logger.info("Password Hash Standardization Complete")
        logger.info("=" * 50)
        logger.info(f"Total users: {stats['total']}")
        logger.info(f"Already using bcrypt: {stats['already_bcrypt']}")
        logger.info(f"Converted to bcrypt: {stats['converted']}")
        logger.info(f"Errors: {stats['errors']}")
        
        if stats["converted"] > 0:
            logger.info("=" * 50)
            logger.info("IMPORTANT: Some user passwords were reset!")
            logger.info("See reset_passwords.txt for the new passwords")
            logger.info("=" * 50)

if __name__ == "__main__":
    logger.info("Running password hash standardization")
    asyncio.run(standardize_hash_formats()) 