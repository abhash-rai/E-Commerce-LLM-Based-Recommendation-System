import uvicorn
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

from llm.llm import LLM
from db.sql_db import DB

db = DB()
llm = LLM(db, load_model_data_on_start=True)

server_host = "127.0.0.1"
server_port = 8000
app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": f"Try ot APIs: http://{server_host}:{server_port}/docs"}

@app.get("/get_customer_profile/{user_id}")
async def get_customer_profile(user_id: int):
    return llm.get_user_profile(user_id)

@app.get("/recommend_product/{user_id}")
async def recommend_product(user_id: int):
    """
    Returns recommendations id for a given user ID.

    Args:
        user_id (int): ID of the user.

    Returns:
        dict: dictionary containing given user id, generated recommended id, and recommended product data.
    """
    if db.get_data(table="User", id=user_id):
        recommendation_data = llm.make_recommendation_for_customer(user_id=user_id)
        recommendation_id = recommendation_data['recommendation_id']
        product_id = recommendation_data['product_id']

        product_dict = db.get_data(table="Product", id=product_id, return_as_dict=True)
        
        return {
            'user_id': user_id,
            'recommendation_id': recommendation_id,
            'product_data': product_dict
        }
    
    else:
        raise HTTPException(status_code=404, detail="User ID not found")

@app.get("/search_products")
async def search_products(
    user_id: int,
    query: str = Query(..., min_length=1, max_length=100),
    min_price: float = Query(None, ge=0),
    max_price: float = Query(None, ge=0),
    min_stock: int = Query(None, ge=1),
):
    """
    Search for products by a query string with optional price filters.

    Args:
        query (str): The search term.
        min_price (float): Minimum price for filtering (optional).
        max_price (float): Maximum price for filtering (optional).
        min_stock (float): Minimum stock for filtering (optional).

    Returns:
        dict: A list of matching products.
    """
    if db.get_data(table="User", id=user_id):
        return db.search_product(
            user_id=user_id,
            search_keyword=query,
            min_price=min_price,
            max_price=max_price,
            min_stock=min_stock,
            return_as_dict=True
        )
    
    else:
        raise HTTPException(status_code=404, detail="User ID not found")

@app.post("/set_recommendation_feedback")
async def set_recommendation_feedback(
    user_id: int,
    recommendation_id: int,
    rating_score: int = Query(..., ge=0, le=5),
):
    """
    Sets feedback for a recommendation. Only accepts feedback from the same user as the user who was recommended. 

    Args:
        recommendation_id (int): ID of the recommendation.
        rating_score (int): Rating score (0 to 5).
    """
    if user_id == db.get_data(table="Recommendation", id=recommendation_id, return_as_dict=False).user_id:
        recommendation_feedback_id = db.record_recommendation_feedback(
            recommendation_id=recommendation_id,
            user_id=user_id,
            rating=rating_score
        )
        if recommendation_feedback_id:
            return JSONResponse(
                content={"status": "success", "message": "Feedback recorded successfully"},
                status_code=200,
            )
        else:
            raise HTTPException(status_code=409, detail="Feedback for this recommendation has already been submitted.")
    
    else:
        raise HTTPException(status_code=403, detail="Given user is not authorized to access or interact with this recommendation.")

@app.get("/get_recommendation_performance")
async def get_recommendation_performance():
    """
    Returns a dictionary of the number of recommendations per rating score (0 to 5). Can be used for visualization like barplot for real time monitoring of recommendation performance from user feedbacks.

    Returns:
        dict: Key-value pairs where keys are rating scores and values are the count of recommendations for each score.
    """
    return db.summarize_recommendation_feedback_rating()

if __name__ == "__main__":
    uvicorn.run(f"{Path(__file__).stem}:app", host=server_host, port=server_port, reload=True)
