import os
import random
import httpx
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from ..database import OtpRequest

# Load the API key from environment variables
FAST2SMS_API_KEY = os.getenv("FAST2SMS_API_KEY", "your_placeholder_api_key")
OTP_EXPIRY_MINUTES = 5

def _generate_otp() -> str:
    """Generates a 5-digit numeric OTP."""
    return str(random.randint(10000, 99999)).zfill(5)

async def _send_sms_otp(phone_number: str, otp: str):
    """
    Sends the OTP via Fast2SMS API.
    """
    if not FAST2SMS_API_KEY or FAST2SMS_API_KEY == "your_placeholder_api_key":
        print("--- OTP Service (Mock) ---")
        print(f"WARNING: FAST2SMS_API_key not set. Mocking SMS dispatch.")
        print(f"Sending OTP to {phone_number}")
        print(f"OTP: {otp}")
        print(f"--------------------------")
        return

    url = "https://www.fast2sms.com/dev/bulkV2"
    payload = {
        "variables_values": otp,
        "route": "otp",
        "numbers": phone_number,
    }
    headers = {
        "authorization": FAST2SMS_API_KEY,
    }

    async with httpx.AsyncClient() as client:
        try:
            print(f"Sending OTP to {phone_number} via Fast2SMS...")
            response = await client.post(url, data=payload, headers=headers)
            response.raise_for_status()

            response_data = response.json()
            if response_data.get("return") is False:
                print(f"Fast2SMS API returned an error: {response_data.get('message')}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to send OTP. Gateway error: {response_data.get('message')}"
                )

            print(f"Fast2SMS response: {response_data}")

        except httpx.HTTPStatusError as e:
            print(f"Error sending OTP via Fast2SMS: {e.response.text}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send OTP via SMS gateway."
            )
        except Exception as e:
            print(f"An unexpected error occurred while sending OTP: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while sending OTP."
            )

async def send_otp(db: Session, phone_number: str, hotel_id: int) -> str:
    """
    Generates, stores, and sends an OTP.
    Returns the unique token for this OTP request.
    """
    otp_code = _generate_otp()

    # Create a new OTP request record
    db_otp_request = OtpRequest(
        hotel_id=hotel_id,
        phone_number=phone_number,
        otp_code=otp_code,
        created_at=datetime.now(timezone.utc)
    )
    db.add(db_otp_request)
    db.commit()
    db.refresh(db_otp_request)

    # "Send" the OTP
    await _send_sms_otp(phone_number, otp_code)

    return db_otp_request.id

def verify_otp(db: Session, token: str, otp: str, phone_number: str):
    """
    Verifies the OTP against the stored record.
    Raises HTTPException for any verification failures.
    """
    # Find the OTP request by token
    db_otp_request = db.query(OtpRequest).filter(OtpRequest.id == token).first()

    if not db_otp_request:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP session or token.")

    # Check if the phone number matches
    if db_otp_request.phone_number != phone_number:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP was not sent to this phone number.")

    # Check if the OTP has already been verified
    if db_otp_request.verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This OTP has already been used.")

    # Check if the OTP has expired
    expiry_time = db_otp_request.created_at.replace(tzinfo=timezone.utc) + timedelta(minutes=OTP_EXPIRY_MINUTES)
    if datetime.now(timezone.utc) > expiry_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP has expired. Please request a new one.")

    # Check if the OTP code is correct
    if db_otp_request.otp_code != otp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP code.")

    # Mark the OTP as verified
    db_otp_request.verified = True
    db.commit()

    return True
