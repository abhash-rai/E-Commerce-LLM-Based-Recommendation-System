import os
from sqlmodel import Field, SQLModel, Relationship
from pydantic import conint
from typing import List, Optional
from datetime import datetime

class User(SQLModel, table=True):
    user_id: int = Field(default=None, primary_key=True)
    email: str = Field(nullable=False, unique=True)
    profile_description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    search_history: List["SearchHistory"] = Relationship(back_populates="user")
    recommendations: List["Recommendation"] = Relationship(back_populates="user")
    feedbacks: List["RecommendationFeedback"] = Relationship(back_populates="user")


class Category(SQLModel, table=True):
    category_id: int = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, unique=True)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    products: List["Product"] = Relationship(back_populates="category")


class Product(SQLModel, table=True):
    product_id: int = Field(default=None, primary_key=True)
    category_id: int = Field(foreign_key="category.category_id", nullable=False)
    name: str = Field(nullable=False)
    description: Optional[str] = None
    price: float = Field(nullable=False)
    stock: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    category: Optional[Category] = Relationship(back_populates="products")
    recommendations: List["Recommendation"] = Relationship(back_populates="product")


class SearchHistory(SQLModel, table=True):
    search_id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.user_id", nullable=False)
    query: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    user: Optional[User] = Relationship(back_populates="search_history")


class Recommendation(SQLModel, table=True):
    recommendation_id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.user_id", nullable=False)
    product_id: int = Field(foreign_key="product.product_id", nullable=False)
    score: float = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    user: Optional[User] = Relationship(back_populates="recommendations")
    product: Optional[Product] = Relationship(back_populates="recommendations")
    feedbacks: List["RecommendationFeedback"] = Relationship(back_populates="recommendation")


class RecommendationFeedback(SQLModel, table=True):
    recommendation_feedback_id: int = Field(default=None, primary_key=True)
    recommendation_id: int = Field(foreign_key="recommendation.recommendation_id", nullable=False, unique=True)
    user_id: int = Field(foreign_key="user.user_id", nullable=False)
    rating: int = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    recommendation: Optional[Recommendation] = Relationship(back_populates="feedbacks")
    user: Optional[User] = Relationship(back_populates="feedbacks")


