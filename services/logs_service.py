import json
from typing import Any, Sequence, List, Dict

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy import Result
from sqlalchemy.orm import Session

from dal.models import User, APIMetrics


def log_api_usage(user: User, request: Request, db: Session, rows_fetched: int, response_data: Any, status_code: int):
    """
        Logs API request details into the `api_metrics` table.

        Args:
            user (User): The authenticated user making the request.
            request (Request): The incoming FastAPI request object.
            db (Session): The database session.
            rows_fetched (int): Number of rows fetched from the database.
            response_data (Any): The response data sent to the client.
            status_code (int): The HTTP status code of the response.
        """
    # this serializes the data to json, it actually saves the number of bytes as int
    response_size: int = len(json.dumps(response_data).encode("utf-8") )
    usage_entry: APIMetrics = APIMetrics(
        user_id=user.id,
        endpoint=request.url.path,
        rows_fetched=rows_fetched,
        response_size=response_size,
        status_code=status_code
    )
    db.add(usage_entry)
    db.commit()

def fetch_and_log_data(request: Request, user: User, db: Session, query) -> JSONResponse:
    """
        Executes a database query, fetches data, logs API usage, and returns a JSON response.

        Args:
            request (Request): The incoming FastAPI request.
            user (User): The authenticated user making the request.
            db (Session): The database session.
            query: SQLAlchemy query to fetch data.

        Returns:
            JSONResponse: The response with fetched data or an error message.
        """
    try:
        result: Result = db.execute(query)
        items: Sequence[Any] = result.scalars().all()
        rows_fetched: int = len(items)

        response_data: List[Dict[str, Any]] = [item.__dict__ for item in items]
        for response_object in response_data:
            response_object.pop("_sa_instance_state", None)  # Remove SQLAlchemy metadata

        api_response: JSONResponse = JSONResponse(content=response_data, status_code=200)

    except Exception as e:
        rows_fetched = 0
        response_data = [{"error": str(e)}]
        api_response = JSONResponse(content=response_data, status_code=500)

    log_api_usage(user, request, db, rows_fetched, response_data, api_response.status_code)

    return api_response