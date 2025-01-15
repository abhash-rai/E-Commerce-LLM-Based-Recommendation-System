import os
import pandas as pd
import torch
from sqlmodel import Session, select
from transformers import T5ForConditionalGeneration, T5Tokenizer

import constants
from db.sql_db import DB
from db.sql_models import User, Category, Product, SearchHistory, Recommendation, RecommendationFeedback

class LLM:

    def __init__(self, db: DB, load_model_data_on_start: bool = True):
        self.db: DB = db
        self.engine = self.db.engine

        self.MODEL_NAME = constants.LLM_NAME
        self.model = None
        self.tokenizer = False
        self.model_output_max_length = constants.LLM_MAX_OUTPUT_LENGTH
        self.model_path = constants.LLM_FINE_TUNED_SAVE_PATH
        self.tokenizer_path = constants.LLM_FINE_TUNED_TOKENIZER_PATH
        if load_model_data_on_start:
            self.load_data_for_inferencing()

    def load_data_for_inferencing(self):
        if self.model is None or self.tokenizer is None:
            self.model = T5ForConditionalGeneration.from_pretrained(self.model_path)
            self.tokenizer = T5Tokenizer.from_pretrained(self.tokenizer_path, legacy=False)   

    def make_inference_on_model(self, query):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(device)
        inputs = self.tokenizer(query, return_tensors="pt").to(device)
        
        self.model.eval()
        with torch.no_grad():
            outputs = self.model.generate(
                inputs['input_ids'], 
                max_length=self.model_output_max_length, 
                num_beams=5,  # You can adjust this for more diverse text
                early_stopping=True
            )
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return generated_text

    def engineer_prompt(self, profile_description: str, user_search_history: str, candidates_for_recommendation, return_customer_info_only = False) -> str:
        '''
        Parameters:
            - profile_description (str): example -> "I love gaming and books"
            - user_search_history (str): example -> "Laptop,Video Games,Gaming Mouse,Gaming Headset,Piano,Wireless Earbuds"
            - candidates_for_recommendation (dict) -> {1:"Laptop", 2:"PlayStation 5", 3:"Xbox Series X", 4:"Gaming Chair"}
        '''
        if return_customer_info_only:  
            return f'''Customer Profile: 
{profile_description}

Search History: 
{user_search_history}'''
        
        else:
            return f'''Given the following customer profile and search history, suggest the most relevant product from the provided list of candidates. Return only the name of the product that best matches the customer's needs based on their profile and search activity.
Customer Profile: {profile_description}
Search History: {user_search_history}
Products for Recommendation: {candidates_for_recommendation}
Your Task: Select the most suitable product from the list of "Products for Recommendation" based on the customer profile and search history.
'''
    
    def make_recommendation_for_customer(self, user_id: int) -> int:
        '''
        Takes user id, obtains profile description of the user and their search history and based on it makes a recommendation from available products, stores the recommendation and returns recommendation id.

        Returns:
            - database recommendation id (int)
        '''
        profile_description = self.db.get_data("User", user_id)['profile_description']

        with Session(self.engine) as session:
            statement = select(SearchHistory.query).where(SearchHistory.user_id == user_id)
            all_user_search_history = session.exec(statement).all()
            all_user_search_history_str = ','.join(all_user_search_history)

        products_for_recommendation = self.db.search_product(user_id, profile_description, use_vectore_search=True, similarity_threshold=0.3, return_as_dict=False)
        products_dict_for_recommendation = {product.product_id: product.name for product in products_for_recommendation}
        
        query = self.engineer_prompt(profile_description, all_user_search_history_str, products_dict_for_recommendation)
        print(query)

        recommendation_str = self.make_inference_on_model(query)
        # recommended_product_id = int(recommendation_str.split(',')[0])
        # recommended_product_name = recommendation_str.replace(f'{recommended_product_id},', '').strip()
        # print(recommended_product_id, recommended_product_name)
        
        for product in products_for_recommendation:
            if recommendation_str.strip().lower() == product.name.strip().lower():
                recommended_product_id = product.product_id
                recommendation_id = self.db.record_recommendation(user_id, recommended_product_id)
                break
        
        return {
            'product_id': recommended_product_id,
            'recommendation_id': recommendation_id,
        }

        return recommendation_str
    
    def get_user_profile(self, user_id):
        profile_description = self.db.get_data("User", user_id)['profile_description']

        with Session(self.engine) as session:
            statement = select(SearchHistory.query).where(SearchHistory.user_id ==  user_id)
            all_user_search_history = session.exec(statement).all()
            all_user_search_history_str = ','.join(all_user_search_history)

        return self.engineer_prompt(profile_description, all_user_search_history_str, None, return_customer_info_only=True)

    def generate_dataset_for_llm_fine_tuning(self, csv_file_path: str):
        os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)

        df = pd.DataFrame(columns=['input', 'output'])

        with Session(self.engine) as session:
            statement = select(RecommendationFeedback).where(RecommendationFeedback.rating >= 3)
            recommendation_feedbacks = session.exec(statement).all()
            if len(recommendation_feedbacks) == 0:
                return
        
        for feedback in recommendation_feedbacks:
            recommendation = self.db.get_data("Recommendation", feedback.recommendation_id, return_as_dict=False)
            answer: Product = self.db.get_data("Product", recommendation.product_id, return_as_dict=False)
            answer_text = answer.name
            answer_id = answer.product_id

            profile_description = self.db.get_data("User", feedback.user_id)['profile_description']

            with Session(self.engine) as session:
                statement = select(SearchHistory.query).where(SearchHistory.user_id == feedback.user_id)
                all_user_search_history = session.exec(statement).all()
                all_user_search_history_str = ','.join(all_user_search_history)

            products_for_recommendation = self.db.search_product(profile_description, use_vectore_search=True, similarity_threshold=0.3, return_as_dict=False)
            # products_dict_for_recommendation = {product.product_id: product.name for product in products_for_recommendation}
            # if answer_text not in products_dict_for_recommendation.values():
            #     products_dict_for_recommendation[answer_id] = answer_text
            
            products_dict_for_recommendation = [product.name for product in products_for_recommendation]
            if answer_text not in products_dict_for_recommendation:
                products_dict_for_recommendation.append(answer_text)
            
            query = self.engineer_prompt(profile_description, all_user_search_history_str, products_dict_for_recommendation)

            df.loc[len(df)] = [query, f'{answer_text}']  # Add to the DataFrame
        
        df.to_csv(csv_file_path, index=False)
