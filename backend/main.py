from fastapi import FastAPI, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import uvicorn
from starlette.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import MONGODB_URI, DATABASE_NAME
from backend.models.user import UserCreate, UserResponse, Token
from backend.models.query import QueryCreate, QueryFilter, QueryResponse
from backend.services.auth_service import AuthService
from backend.services.search_service import SearchService
from backend.services.chat_service import ChatService
from pydantic import BaseModel
from typing import List
from pytz import timezone
app = FastAPI(title="Cerebro")
# Managing CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # All Origins allowed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Initialize Services
auth_service = AuthService()
search_service = SearchService()
chat_service = ChatService()


class SearchRequest(BaseModel):
    query: str


class Database:
    client: AsyncIOMotorClient = None

    @classmethod
    async def get_client(cls):
        if not cls.client:
            cls.client = AsyncIOMotorClient(MONGODB_URI)
        return cls.client

    @classmethod
    async def get_database(cls):
        client = await cls.get_client()
        return client[DATABASE_NAME]

    @classmethod
    async def get_queries_collection(cls):
        db = await cls.get_database()
        return db['queries']


# @app.get("/")
# async def root():
#     # return HTMLResponse(content="Celebro", status_code=200)
#     # return RedirectResponse(url="/docs")


# Authentication Routes
@app.post("/signup", response_model=UserResponse)
async def signup(user: UserCreate):
    return await auth_service.create_user(user)


@app.post("/login", response_model=Token)
async def login(username: str, password: str):
    user = await auth_service.authenticate_user(username, password)
    access_token = auth_service.create_access_token(
        data={"sub": user.username}
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Search Routes
@app.post("/search")
async def search_query(
    request: SearchRequest,
    current_user: UserResponse = Depends(auth_service.get_current_user)
):
    try:
        # Web Search
        web_results = search_service.search(request.query)
        # Create context from search results
        context = "\n\n".join([result['snippet'] for result in web_results])
        # Generate AI Answer
        ai_answer = await chat_service.generate_answer(context, request.query)
        # Save Query
        queries_collection = await Database.get_queries_collection()
        query_doc = {
            "user_id": current_user.username,
            "query": request.query,
            "web_results": web_results,
            "ai_answer": ai_answer,
            "created_at": datetime.now(timezone("Asia/Kolkata"))
        }
        await queries_collection.insert_one(query_doc)

        return {
            "web_results": web_results,
            "ai_answer": ai_answer
        }
    except Exception as e:
        import traceback
        print(f"Error details: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/queries", response_model=List[QueryResponse])
async def get_queries(
        filter: QueryFilter = Depends(),
        current_user: UserResponse = Depends(auth_service.get_current_user)
):
    """Retrieve user's recent queries"""
    queries_collection = await Database.get_queries_collection()

    threshold_date = datetime.now() - timedelta(days=filter.days)

    queries = await queries_collection.find({
        "user_id": current_user.username,
        "created_at": {"$gte": threshold_date}
    }).sort("created_at", -1).skip((filter.page - 1) * filter.page_size).limit(filter.page_size).to_list(length=None)

    return queries

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
