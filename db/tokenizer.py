import re
import nltk
from nltk.corpus import stopwords


class TextTokenizer:

    def __init__(self):
        self.ensure_model_downloaded()

    def ensure_model_downloaded(self):
        nltk.download('stopwords')

    def clean_text(self, query: str) -> list:
        # Remove special characters, keep only letters and spaces
        cleaned_query = re.sub(r'[^A-Za-z0-9\s]', '', query)
        
        # Tokenize the query (split by spaces)
        words = cleaned_query.split()
        
        # Convert to lowercase
        words = [word.lower() for word in words]
        
        # Optionally remove stopwords (common words like 'the', 'is', etc.)
        stop_words = set(stopwords.words('english'))
        filtered_words = [word for word in words if word not in stop_words]
        
        return filtered_words