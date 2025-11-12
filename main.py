import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson.objectid import ObjectId

from database import db, create_document, get_documents
from schemas import Book, Member, Loan

app = FastAPI(title="Library Management API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Helpers to convert ObjectId to string

def serialize_doc(doc: dict):
    if not doc:
        return doc
    d = dict(doc)
    if "_id" in d:
        d["_id"] = str(d["_id"])
    return d


@app.get("/")
def read_root():
    return {"message": "Library Management Backend is running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    # Check environment variables
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


# ------- Library Endpoints -------

# Create documents
@app.post("/api/books", response_model=dict)
async def create_book(book: Book):
    try:
        book_id = create_document("book", book)
        return {"_id": book_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/members", response_model=dict)
async def create_member(member: Member):
    try:
        member_id = create_document("member", member)
        return {"_id": member_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/loans", response_model=dict)
async def create_loan(loan: Loan):
    try:
        loan_id = create_document("loan", loan)
        return {"_id": loan_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# List documents (basic search by query param q)
@app.get("/api/books", response_model=List[dict])
async def list_books(q: Optional[str] = None, limit: int = 50):
    try:
        filter_dict = {}
        if q:
            filter_dict = {"$or": [
                {"title": {"$regex": q, "$options": "i"}},
                {"author": {"$regex": q, "$options": "i"}},
                {"isbn": {"$regex": q, "$options": "i"}},
                {"tags": {"$regex": q, "$options": "i"}},
            ]}
        docs = get_documents("book", filter_dict, limit)
        return [serialize_doc(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/members", response_model=List[dict])
async def list_members(q: Optional[str] = None, limit: int = 50):
    try:
        filter_dict = {}
        if q:
            filter_dict = {"$or": [
                {"name": {"$regex": q, "$options": "i"}},
                {"email": {"$regex": q, "$options": "i"}},
                {"membership_id": {"$regex": q, "$options": "i"}},
            ]}
        docs = get_documents("member", filter_dict, limit)
        return [serialize_doc(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/loans", response_model=List[dict])
async def list_loans(limit: int = 50):
    try:
        docs = get_documents("loan", {}, limit)
        return [serialize_doc(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Schema endpoint for viewer tools
class SchemaResponse(BaseModel):
    schemas: List[str]


@app.get("/schema")
async def get_schema():
    return {
        "schemas": ["book", "member", "loan"]
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
