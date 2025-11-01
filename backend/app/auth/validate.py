import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
import os
from uuid import UUID
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.database.database import get_db
from app.models.profiles import Profile

load_dotenv()


SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "")
ALGORITHM = "HS256"

bearer_scheme = HTTPBearer()


def get_current_user(token = Depends(bearer_scheme)):
    try:
        payload = jwt.decode(
            token.credentials,
            SUPABASE_JWT_SECRET,
            algorithms=[ALGORITHM],
            options={"verify_aud": False} # Supabase uses 'aud':'authenticated'
        )

        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not in token",
            )
        
        email = payload.get("email")
        return {"user_id": user_id, "email": email}
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    

async def get_current_user_profile(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Profile:
    """
    Get or create the current user's profile.
    Profiles are keyed by the auth user ID, so we ensure one exists before proceeding.
    """
    try:
        user_uuid = UUID(current_user["user_id"])
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user id",
        )
    stmt = select(Profile).where(Profile.id == user_uuid).options(selectinload(Profile.subscription))
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()

    if not profile:
        profile = Profile(id=user_uuid)
        db.add(profile)
        await db.commit()
        await db.refresh(profile, ["subscription"])

    return profile
    