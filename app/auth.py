import os
from fastapi import Header, HTTPException, status
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the master password from environment variables
MASTER_PASSWORD = os.getenv("MASTER_PASSWORD")

async def verify_master_password(x_master_password: str = Header(None, alias="X-Master-Password")):
    """
    Dependency to verify the master password provided in the request header.
    """
    if not MASTER_PASSWORD:
        # This is a server-side configuration error.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Master password is not configured on the server.",
        )

    if not x_master_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Master password required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if x_master_password != MASTER_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect master password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # If we reach here, the password is correct
    return True
