"""
Database Schemas for Library Management System

Each Pydantic model represents a MongoDB collection.
The collection name is the lowercase of the class name.

Examples:
- Book -> "book"
- Member -> "member"
- Loan -> "loan"
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List


class Book(BaseModel):
    """
    Books collection schema
    Collection name: "book"
    """
    title: str = Field(..., description="Book title")
    author: str = Field(..., description="Author full name")
    isbn: Optional[str] = Field(None, description="ISBN-10 or ISBN-13")
    total_copies: int = Field(1, ge=0, description="Total number of copies in library")
    available_copies: int = Field(1, ge=0, description="Currently available copies")
    tags: Optional[List[str]] = Field(default_factory=list, description="Topic tags")


class Member(BaseModel):
    """
    Members collection schema
    Collection name: "member"
    """
    name: str = Field(..., description="Member full name")
    email: EmailStr = Field(..., description="Member email address")
    membership_id: Optional[str] = Field(None, description="Library-issued member ID")
    phone: Optional[str] = Field(None, description="Phone number")
    is_active: bool = Field(True, description="Whether the membership is active")


class Loan(BaseModel):
    """
    Loans collection schema
    Collection name: "loan"
    """
    book_id: str = Field(..., description="Referenced book _id as string")
    member_id: str = Field(..., description="Referenced member _id as string")
    loan_date: Optional[str] = Field(None, description="ISO datetime when loan started")
    due_date: Optional[str] = Field(None, description="ISO datetime when due")
    return_date: Optional[str] = Field(None, description="ISO datetime when returned")
    status: str = Field("borrowed", description="borrowed | returned | overdue")


# Note: The Flames database viewer can read these via GET /schema
