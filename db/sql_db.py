import os
from datetime import datetime
import pandas as pd
from typing import Dict
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, or_
from sqlalchemy.sql import func
from sqlmodel import SQLModel, create_engine, Session, select

import constants
from db.sql_models import User, Category, Product, SearchHistory, Recommendation, RecommendationFeedback
from db.qdrant_db import QdrantDatabase
from db.embedder import TextEmbedder
from db.tokenizer import TextTokenizer

class DB:

    def __init__(self, database_location: str = None):
        self.database_location = constants.SQL_DB_PATH if database_location is None else database_location
        self.engine = None
        self.text_embedder = TextEmbedder()
        self.qdrant_product_database = QdrantDatabase(collection_name=constants.QDRANT_PRODUCT_COLLECTION_NAME)
        self.text_tokenizer = TextTokenizer()
        self.initialize_database()
        
    def initialize_database(self):
        if self.engine is None:
            os.makedirs(os.path.dirname(self.database_location), exist_ok=True)

            sqlite_url = f"sqlite:///{self.database_location}"
            self.engine = create_engine(sqlite_url, echo=True)
            
            if os.path.exists(self.database_location):
                pass
            else:
                print("Database does not exist. Initializing...")
                SQLModel.metadata.create_all(self.engine)
            
    def record_user(self, email: str, profile_description: str):
        user: User = User(email=email, profile_description=profile_description)
        with Session(self.engine) as session:
            session.add(user)
            session.commit()
            session.refresh(user)

    def update_user(self, user_id: int, new_email: str = None, new_profile_description: str = None):
        with Session(self.engine) as session:
            statement = select(User).where(User.user_id == user_id)
            user = session.exec(statement).first()
            if user:
                if new_email is not None:
                    user.email = new_email
                if new_profile_description is not None:
                    user.profile_description = new_profile_description
                user.created_at = user.created_at
                user.updated_at = datetime.now()
                session.commit()
                session.refresh(user)
 
    def record_category(self, name: str, description: str):
        category: Category = Category(name=name, description=description)
        with Session(self.engine) as session:
            session.add(category)
            session.commit()
            session.refresh(category)

    def update_category(self, category_id: int, new_name: str = None, new_description: str = None):
        with Session(self.engine) as session:
            statement = select(Category).where(Category.category_id == category_id)
            category = session.exec(statement).first()
            if category:
                if new_name is not None:
                    category.name = new_name
                if new_description is not None:
                    category.description = new_description
                category.created_at = category.created_at
                category.updated_at = datetime.now()
                session.commit()
                session.refresh(category)
 
    def record_product(self, category_id: int, name: str, description: str, price: float, stock: int):
        product: Product = Product(category_id=category_id, name=name, description=description, price=price, stock=stock)
        with Session(self.engine) as session:
            session.add(product)
            session.commit()
            session.refresh(product)
        
        product_category_str = self.get_data(table='Category', id=category_id)['name']

        product_text = f'Product name is {name} and category is {product_category_str}. Description: {description}'
        product_embedding = self.text_embedder.generate_embedding(product_text)

        self.qdrant_product_database.record_embedding_into_collection(
            id=product.product_id, 
            embedding=product_embedding
        )

    def update_product(self, product_id: int = None, new_category_id: int = None, new_name: str = None, new_description: str = None, new_price: float = None, new_stock: int = None):
        with Session(self.engine) as session:
            statement = select(Product).where(Product.product_id == product_id)
            product: Product = session.exec(statement).first()
            if product:
                if new_category_id is not None:
                    product.category_id = new_category_id
                if new_name is not None:
                    product.name = new_name
                if new_description is not None:
                    product.description = new_description
                if new_price is not None:
                    product.price = new_price
                if new_stock is not None:
                    product.stock = new_stock
                product.created_at = product.created_at
                product.updated_at = datetime.now()
                session.commit()
                session.refresh(product)

        product_category_str = self.get_data(table='Category', id=product.category_id)['name']

        product_text = f'Product name is {new_name} and category is {product_category_str}. Description: {new_description}'
        product_embedding = self.text_embedder.generate_embedding(product_text)

        self.qdrant_product_database.record_embedding_into_collection(
            id=product.product_id, 
            embedding=product_embedding
        )
 
    def record_search_history(self, user_id: int, query: str) -> int:
        query: SearchHistory = SearchHistory(user_id=user_id, query=query)
        with Session(self.engine) as session:
            session.add(query)
            session.commit()
            session.refresh(query)
        return query.search_id
 
    def record_recommendation(self, user_id: int, product_id: int, score: float = 1) -> int:
        recommendation: Recommendation = Recommendation(user_id=user_id, product_id=product_id, score=score)
        with Session(self.engine) as session:
            session.add(recommendation)
            session.commit()
            session.refresh(recommendation)
        return recommendation.recommendation_id
 
    def record_recommendation_feedback(self, recommendation_id: int, user_id: int, rating: int) -> int:
        recommendation_feedback: RecommendationFeedback = RecommendationFeedback(recommendation_id=recommendation_id, user_id=user_id, rating=rating)
        with Session(self.engine) as session:
            try:
                session.add(recommendation_feedback)
                session.commit()
                session.refresh(recommendation_feedback)
                return recommendation_feedback.recommendation_feedback_id
            except IntegrityError as e:
                if "UNIQUE constraint failed" in str(e.orig): #Feedback already exists for recommendation
                    session.rollback()  # Rollback the transaction to keep the session clean
                    return None
                else:
                    # For any other IntegrityError, re-raise the exception
                    raise

    def get_data(self, table: str, id: int, return_as_dict: bool = True) -> dict:
        '''
        Parameters:
            table (str) options:
                - "User"
                - "Category"
                - "Product"
                - "SearchHistory"
                - "Recommendation"
                - "RecommendationFeedback"

            id (str): represents primary id of the choosen table
        
        Returns:
            dict if data found else None
        '''
        mapping = {
            "User": select(User).where(User.user_id == id),
            "Category": select(Category).where(Category.category_id == id),
            "Product": select(Product).where(Product.product_id == id),
            "SearchHistory": select(SearchHistory).where(SearchHistory.search_id == id),
            "Recommendation": select(Recommendation).where(Recommendation.recommendation_id == id),
            "RecommendationFeedback": select(RecommendationFeedback).where(RecommendationFeedback.recommendation_feedback_id == id)
        }

        if table not in mapping: # Not given correct table name
            return None 
        
        statement = mapping[table]
        
        with Session(self.engine) as session:
            data = session.exec(statement).first()
            if data:
                if return_as_dict:
                    return data.dict()
                else:
                    return data
            return None
        
    def search_product(self, user_id: int = None, search_keyword: str = '', min_price: float = None, max_price: float = None, min_stock: int = None, return_as_dict: bool = True, use_vectore_search: bool = True, similarity_threshold: float=0.3):
        if user_id is not None:
            self.record_search_history(user_id, search_keyword)

        search_results = []

        ### Using keyword search ###
        with Session(self.engine) as session:
            tokenized_search_keyword: list = self.text_tokenizer.clean_text(search_keyword)

            conditions = []

            keyword_conditions = []
            for keyword in tokenized_search_keyword:
                keyword_conditions.extend(
                    [
                        Product.name.ilike(f"%{keyword}%"),
                        Product.description.ilike(f"%{keyword}%")
                    ]
                )
            
            if keyword_conditions:
                conditions.append(or_(*keyword_conditions))
            
            if min_price is not None:
                conditions.append(
                    Product.price >= min_price
                )

            if max_price is not None:
                conditions.append(
                    Product.price <= max_price
                )

            if min_stock is None:
                conditions.append(
                    Product.stock > 0  # Ensure that the product has stock greater than 0
                )
            else:
                conditions.append(
                    Product.stock > min_stock
                )
            
            statement = select(Product).where(
                *conditions,  # Unpack the list of conditions
            )
            results = session.exec(statement).all()
            search_results.extend(results)

        ### Using semantic vectore search ###
        if use_vectore_search:
            search_query_embedding = self.text_embedder.generate_embedding(search_keyword)

            products_search_result_ids: list = self.qdrant_product_database.search_similar_products(query_embedding=search_query_embedding, similarity_threshold=similarity_threshold)
            with Session(self.engine) as session:
                statement = select(Product).filter(Product.product_id.in_(products_search_result_ids))
                products = session.exec(statement).all()

            for product in products:
                stock_requirement_met = False
                if min_stock: # when stock given
                    if (product.stock >= min_stock) and (product.stock > 0): 
                        stock_requirement_met = True
                else:
                    if product.stock > 0: # Ensure that the product has stock greater than 0
                        stock_requirement_met = True
                
                if stock_requirement_met:
                    if (min_price is None or product.price >= min_price) and (max_price is None or product.price <= max_price):
                        # filtered_products.append(product)
                        if product not in search_results:
                            search_results.append(product)

        ### Search Result Return ###
        if return_as_dict:
            return [product.dict() for product in search_results]
        else:
            return [product for product in search_results]

    def summarize_recommendation_feedback_rating(self) -> dict:
        with Session(self.engine) as session:
            statement = (
                select(RecommendationFeedback.rating, func.count(RecommendationFeedback.rating))
                .group_by(RecommendationFeedback.rating)
            )

            results = session.exec(statement).all()
            results_dict = {result[0]:result[1] for result in results}
        
        return results_dict