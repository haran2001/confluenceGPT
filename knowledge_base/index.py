# knowledge_base/indexer.py
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class KnowledgeBase:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # example model
        self.index = None
        self.documents = []  # store original text
        self.embeddings = None

    def build_index(self, texts):
        """
        Build the FAISS index from a list of documents/text blocks.
        """
        self.documents = texts
        self.embeddings = self.model.encode(texts, convert_to_numpy=True)
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.embeddings)

    def query(self, query_text, top_k=3):
        """
        Query the index with a user query, return top_k relevant documents.
        """
        query_embedding = self.model.encode([query_text], convert_to_numpy=True)
        distances, indices = self.index.search(query_embedding, top_k)
        results = []
        for i, idx in enumerate(indices[0]):
            results.append({
                "text": self.documents[idx],
                "distance": float(distances[0][i])
            })
        return results
