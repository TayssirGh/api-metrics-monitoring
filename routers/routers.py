from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from dal.database import get_db_connection
from dal.models import User, Product
from services.api_key_service import authenticate_api_key
from services.logs_service import fetch_and_log_data, log_api_usage

router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "Hello, World!"}

@router.get("/protected_endpoint_1")
def protected_route(request: Request, user: User = Depends(authenticate_api_key), db: Session = Depends(get_db_connection)):
    log_api_usage(user, request, db, rows_fetched=5, response_data=512, status_code=200)
    return {"message": f"Hello, {user.username}! You have access from endpoint 1 👋"}

@router.get("/protected_endpoint_2")
def protected_route(request: Request, user: User = Depends(authenticate_api_key), db: Session = Depends(get_db_connection)):
    log_api_usage(user, request, db, rows_fetched=1500, response_data=256, status_code=200)
    return {"message": f"Hello, {user.username}! You have access from endpoint 2 👋"}

@router.get("/products")
def get_products(request: Request, user: User = Depends(authenticate_api_key),
                 db: Session = Depends(get_db_connection)) -> JSONResponse:
    return fetch_and_log_data(request, user, db, query=select(Product).where(Product.price > 200))
