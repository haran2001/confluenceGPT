# knowledge_base/opensearch_kb.py
from opensearchpy import OpenSearch, RequestsHttpConnection
from sentence_transformers import SentenceTransformer
import json

class OpenSearchKnowledgeBase:
    def __init__(self, 
                 host: str, 
                 port: int, 
                 index_name: str,
                 model_name='all-MiniLM-L6-v2',
                 http_auth=None, 
                 use_ssl=True,
                 verify_certs=True,
                 aws_access_key_id=None,
                 aws_secret_access_key=None,
                 region=None):
        """
        :param host: The host endpoint of your OpenSearch domain (e.g., 'search-my-domain-xxxxxx.us-east-1.es.amazonaws.com')
        :param port: Typically 443 for HTTPS
        :param index_name: The index where we'll store and retrieve documents
        :param model_name: SentenceTransformer model name
        :param http_auth: Tuple (username, password) if using basic auth (not typical for AWS domain with SigV4)
        :param use_ssl: Boolean to indicate HTTPS usage
        :param verify_certs: Whether to verify SSL certificates
        :param aws_access_key_id, aws_secret_access_key, region: Required if using AWS SigV4. 
                                                                 Alternatively, you can use IAM roles with an appropriate library or set environment variables.
        """
        self.host = host
        self.port = port
        self.index_name = index_name
        self.model_name = model_name

        # Initialize embedding model
        self.model = SentenceTransformer(self.model_name)

        # Initialize OpenSearch client
        self.client = OpenSearch(
            hosts = [{'host': self.host, 'port': self.port}],
            http_auth=http_auth,  
            use_ssl=use_ssl,
            verify_certs=verify_certs,
            connection_class=RequestsHttpConnection
        )

    def index_documents(self, docs):
        """
        Index multiple documents into OpenSearch.
        docs = [
          {"id": "doc1", "text": "...", "metadata": ...},
          {"id": "doc2", "text": "...", "metadata": ...},
          ...
        ]
        """
        # Prepare a bulk request body
        bulk_data = []
        for doc in docs:
            # Generate embedding for the text
            embedding = self._get_embedding(doc["text"])

            # Bulk index structure
            bulk_data.append(json.dumps({"index": {"_index": self.index_name, "_id": doc["id"]}}))
            data_doc = {
                "text": doc["text"],
                "text_vector": embedding,
            }
            # Optionally add metadata if needed
            if "metadata" in doc:
                data_doc.update(doc["metadata"])

            bulk_data.append(json.dumps(data_doc))

        # Join all lines
        bulk_body = "\n".join(bulk_data) + "\n"
        response = self.client.bulk(body=bulk_body)
        if response.get('errors'):
            print("Errors occurred while indexing documents:", response)
        else:
            print("Documents indexed successfully")

    def search(self, query_text, k=3):
        """
        Perform a k-NN search using the query text embedding.
        Return top k documents with relevance scores.
        """
        query_embedding = self._get_embedding(query_text)

        # k-NN query
        search_query = {
            "size": k,
            "query": {
                "knn": {
                    "text_vector": {
                        "vector": query_embedding,
                        "k": k
                    }
                }
            }
        }

        response = self.client.search(index=self.index_name, body=search_query)
        hits = response['hits']['hits']

        results = []
        for hit in hits:
            doc_id = hit['_id']
            source = hit['_source']
            score = hit['_score']
            results.append({
                "id": doc_id,
                "text": source["text"],
                "score": score
            })
        return results

    def _get_embedding(self, text):
        """
        Generate a text embedding using the local or remote model.
        Return a list (or array) that can be stored in OpenSearch.
        """
        emb = self.model.encode([text], convert_to_numpy=True)[0]
        return emb.tolist()  # Convert to list for JSON serialization
