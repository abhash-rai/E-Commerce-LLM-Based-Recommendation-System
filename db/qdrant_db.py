import os
import spacy
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from qdrant_client.http.exceptions import UnexpectedResponse

from db.embedder import TextEmbedder
import constants

class QdrantDatabase:

    def __init__(self, collection_name: str):
        self.db_location = constants.QDRANT_STORAGE_PATH
        self.collection_name = collection_name
        self.client = QdrantClient("http://localhost:6333")  # Connect to the Qdrant instance
        # self.delete_collection() # degub
        self.create_collection_if_not_exists()

    def create_collection_if_not_exists(self):
        try:
            # Check if the collection already exists
            self.client.get_collection(self.collection_name)
            print(f"Collection '{self.collection_name}' already exists.")
        except Exception as e:
            if "Not found" in str(e):
                print(f"Collection '{self.collection_name}' not found. Creating...")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=TextEmbedder.embedding_size, distance=Distance.COSINE),  # Adjust size and distance as needed
                )
                print(f"Collection '{self.collection_name}' created successfully.")
            else:
                raise e
            
    def delete_collection(self):
        try:
            # Delete the specified collection
            self.client.delete_collection(collection_name=self.collection_name)
            print(f"Collection '{self.collection_name}' deleted successfully.")
            print("Remaining collections:", [c.name for c in self.client.get_collections().collections])
        except Exception as e:
            print(f"Failed to delete collection '{self.collection_name}': {e}")

    def record_embedding_into_collection(self, id: int, embedding: np.ndarray):        
        point = PointStruct(
            id=id,
            vector=embedding.tolist(),  # Convert the numpy array to a list
            # payload={"name": name, "category": category, "description": description}  # Optional metadata
        )

        self.client.upsert(collection_name=self.collection_name, points=[point])

    def search_similar_products(self, query_embedding: np.ndarray, k: int = 50, similarity_threshold: float = 0.3):
        """
        Search for the top k most similar products based on a query.
        
        :param query: The query string to search for similar products.
        :param k: The number of similar products to retrieve (default: 5).
        :return: A list of similar products with metadata.
        """

        # Search for the most similar products
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding.tolist(),
            limit=k,
            score_threshold=similarity_threshold,  # Only include results above this similarity score
            # with_payload=True  # Include metadata in the results
        )
        
        similar_products = []
        for result in results:
            print(result)
            similar_products.append(result.id)
            # payload = result.payload
            # similar_products.append({
            #     "product_id": product_id,
            #     "name": payload["name"],
            #     "description": payload["description"]
            # })

        return similar_products
