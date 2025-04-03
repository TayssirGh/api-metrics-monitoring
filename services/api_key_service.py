import json
import secrets
from typing import Any, Type

from fastapi import Depends, HTTPException, Security, Request
from fastapi.security import APIKeyHeader
from sqlalchemy import String, cast
from sqlalchemy.orm import Session

from dal.database import get_db_connection
from dal.models import APIMetrics, User


def generate_api_key():
    return secrets.token_hex(32)


api_key_header: APIKeyHeader = APIKeyHeader(name="parcellesix-API-Key", auto_error=False)


def authenticate_api_key(
        api_key: str = Security(api_key_header),
        db: Session = Depends(get_db_connection)
) -> Type[User]:
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")

    user = db.query(User).filter(cast(User.api_key, String) == cast(api_key, String)).first()
    if not user:
        raise HTTPException(status_code=403, detail="Invalid API key")

    return user
