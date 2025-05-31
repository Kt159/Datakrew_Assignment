# main.py
import os
from typing import Optional 
from datetime import datetime, timedelta, timezone 
import jwt
from dotenv import load_dotenv 
from sqlalchemy import text 

from fastapi import FastAPI, Request, HTTPException, status, Depends 
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_pipeline import AgentExecutor

# Load environment variables
load_dotenv()

app = FastAPI()
agent = AgentExecutor()


# --- Configuration from Environment Variables ---
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM', 'HS256') 
try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 30))
except ValueError:
    print("Warning: ACCESS_TOKEN_EXPIRE_MINUTES in .env is not an integer. Defaulting to 30.")
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- FastAPI Middleware for CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost","https://localhost:3000","https://datakrew-assignment-frontend-chatbot.onrender.com",
                    "https://0.0.0.0"], 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"], 
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="get-token")

# --- Pydantic Models ---
class NameCredential(BaseModel):
    name: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class QuestionRequest(BaseModel):
    question: str

# --- JWT Utility Functions ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) 
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError as e: 
        print(f"JWT Decode Error: {e}") 
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_fleet_id(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    fleet_id = payload.get("fleet_id") 
    if fleet_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token does not contain fleet_id",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return fleet_id

# --- API Endpoints ---
@app.post("/get-token", response_model=Token)
def get_token_by_name(credential: NameCredential):
    """
    MOCKUP ONLY: Takes a fleet_name, finds the fleet_id, and issues a JWT.
    This is a placeholder; in production, use password/2FA.
    """
    name = credential.name.strip()
    fleet_id = None
    try:
        with agent.db._engine.connect() as connection:
            result = connection.execute(
                text("SELECT fleet_id FROM fleets WHERE name = :name"),
                {"name": name}
            ).fetchone()
            if result:
                fleet_id = result[0]
        
    except Exception as e:
        print(f"Database error fetching fleet_id: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error during fleet lookup."
        )
    if fleet_id:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"fleet_id": fleet_id}, 
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"} 
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fleet name not found."
        )

@app.post("/ask")
async def ask_question_with_fleet_context(
    request: QuestionRequest,
    fleet_id: int = Depends(get_current_fleet_id) 
):
    """
    Allows asking a question, protected by the JWT.
    The agent uses the fleet_id from the token to filter data.
    """
    response = agent.run_query_with_agent(request.question, fleet_id)
    final_reply = response.get("output", "Error in generated output, please rephrase your question.")
    return {"reply": final_reply}