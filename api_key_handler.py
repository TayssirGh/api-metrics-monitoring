import secrets

from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from dal.database import get_db_connection
from dal.models import APIKey

def generate_api_key():
    return secrets.token_hex(32)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def authenticate_api_key(
        api_key: str = Security(api_key_header), db: Session = Depends(get_db_connection)
):
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")

    api_key_entry = db.query(APIKey).filter(APIKey.key == api_key).first()

    if not api_key_entry or not api_key_entry.owner:
        raise HTTPException(status_code=403, detail="Invalid API key or user not found")

    api_key_entry.usage_count += 1
    db.commit()

    return api_key_entry.owner


