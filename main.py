
from fastapi import FastAPI, Depends, HTTPException
from prometheus_client import Counter, generate_latest
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.responses import Response
from sqlalchemy.orm import Session

from api_key_handler import authenticate_api_key, generate_api_key
from dal.database import get_db_connection
from dal.models import User, APIKey, UserCreate

app = FastAPI()


Instrumentator().instrument(app).expose(app)
api_calls_per_user = Counter(
    "api_calls_per_user",
    "Count of API calls per user and endpoint",
    ["user_id", "endpoint"]
)

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/protected_endpoint_1")
def protected_route(user: User = Depends(authenticate_api_key)):
    api_calls_per_user.labels(user_id=user.id, endpoint="/protected_1").inc()
    return {"message": f"Hello, {user.username}! You have access."}

@app.get("/protected_endpoint_2")
def protected_route(user: User = Depends(authenticate_api_key)):
    api_calls_per_user.labels(user_id=user.id, endpoint="/protected_2").inc()
    return {"message": f"Hello, {user.username}! You have access."}



@app.post("/generate-key/{user_id}")
def create_api_key(user_id: int,  db: Session = Depends(get_db_connection)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    key = generate_api_key()
    api_key_entry = APIKey(key=key, owner=user)
    db.add(api_key_entry)
    db.commit()
    api_calls_per_user.labels(user_id=user.id, endpoint="/generate-key").inc()
    return {"message": "API key generated", "api_key": key}


@app.post("/create-user")
def create_user(user: UserCreate, db: Session = Depends(get_db_connection)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    user = User(username=user.username, email=user.email)
    db.add(user)
    db.commit()

    api_calls_per_user.labels(user_id=user.id, endpoint="/create-user").inc()
    return {"message": "User created successfully", "user_id": user.id}

@app.get("/metrics")
def custom_metrics():
    return Response(content=generate_latest(), media_type="text/plain")
#check http://localhost:8000/metrics for metrics



