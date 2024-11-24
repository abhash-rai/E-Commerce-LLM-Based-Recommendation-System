# import spacy
# import numpy as np
# from spacy.cli import download

# class TextEmedder:

#     def __init__(self):
#         self.model_name = 'en_core_web_md'
#         self.ensure_model_downloaded() # Download the 'en_core_web_md' model
#         self.nlp = spacy.load("en_core_web_md")  # Load the NLP model for embeddings

#     def ensure_model_downloaded(self):
#         try:
#             spacy.load(self.model_name)
#         except OSError:
#             download(self.model_name)
            
#     def generate_embedding(self, text: str) -> np.ndarray:
#         return np.array(self.nlp(text).vector).astype(np.float32)



from sentence_transformers import SentenceTransformer
import numpy as np

class TextEmbedder:

    embedding_size = 384

    def __init__(self):
        self.model_name="all-MiniLM-L6-v2"
        self.model = SentenceTransformer(self.model_name)

    def generate_embedding(self, text: str) -> np.ndarray:
        return np.array(self.model.encode(text)).astype(np.float32)