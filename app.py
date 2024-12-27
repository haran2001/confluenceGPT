# app.py
import streamlit as st
import json
import os
from dotenv import load_dotenv

from confluence_scraper.scraper import ConfluenceScraper
from s3_storage.upload import S3Uploader
from knowledge_base.opensearch_kb import OpenSearchKnowledgeBase

# Load environment variables from .env file
load_dotenv()

def main():
    st.title("Confluence RAG Chatbot with OpenSearch")

    # Sidebar configurations
    with st.sidebar:
        st.subheader("Configuration")
        confluence_url = st.text_input("Confluence URL", value=os.getenv('CONFLUENCE_URL', 'https://your-confluence.com/page'))
        depth = st.number_input("Depth", min_value=0, max_value=10, value=int(os.getenv('SCRAPE_DEPTH', 1)))
        scrape_button = st.button("Scrape & Index")

        s3_bucket = st.text_input("S3 Bucket Name", value=os.getenv('S3_BUCKET_NAME', 'my-confluence-bucket'))

        st.write("---")
        st.subheader("OpenSearch Settings")
        opensearch_host = st.text_input("OpenSearch Host", value=os.getenv('OPENSEARCH_HOST', 'search-my-domain-xxx.us-east-1.es.amazonaws.com'))
        opensearch_index = st.text_input("OpenSearch Index", value=os.getenv('OPENSEARCH_INDEX', 'confluence-index'))
        create_index_btn = st.button("Create Index")

    # Initialize OpenSearch Knowledge Base
    if "kb" not in st.session_state:
        opensearch_username = os.getenv('OPENSEARCH_USERNAME')
        opensearch_password = os.getenv('OPENSEARCH_PASSWORD')
        st.session_state.kb = OpenSearchKnowledgeBase(
            host=opensearch_host,
            port=int(os.getenv('OPENSEARCH_PORT', 443)),
            index_name=opensearch_index,
            model_name=os.getenv('EMBEDDING_MODEL_NAME', 'all-MiniLM-L6-v2'),
            http_auth=(opensearch_username, opensearch_password) if opensearch_username and opensearch_password else None,
            use_ssl=True,
            verify_certs=True
        )

    # Create OpenSearch Index if button clicked
    if create_index_btn:
        create_index_if_not_exists(st.session_state.kb.client, opensearch_index)
        st.success(f"Index '{opensearch_index}' created or already exists.")

    # Scraping and Indexing
    if scrape_button:
        with st.spinner("Scraping Confluence pages..."):
            scraper = ConfluenceScraper(base_url=confluence_url, depth=depth)
            scraped_data = scraper.scrape_page(confluence_url)
            st.session_state.scraped_data = scraped_data

        st.success("Scraping completed.")

        with st.spinner("Uploading data to S3..."):
            uploader = S3Uploader(
                bucket_name=s3_bucket,
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION')
            )
            uploader.upload_json(scraped_data, f"confluence_scrapes/data.json")
        st.success("Data uploaded to S3.")

        # Flatten the scraped data for indexing
        with st.spinner("Indexing data in OpenSearch..."):
            documents = flatten_data_for_indexing(scraped_data)
            st.session_state.kb.index_documents(documents)
        st.success("Data indexed in OpenSearch.")

    # Chat Interface
    st.subheader("Chat with Confluence-based Knowledge")
    user_query = st.text_input("Ask a question about the Confluence docs:")

    if st.button("Send") and user_query:
        with st.spinner("Retrieving relevant information..."):
            results = st.session_state.kb.search(user_query, k=int(os.getenv('TOP_K_RESULTS', 3)))

        if not results:
            st.write("No results found.")
        else:
            st.write("**Top relevant context:**")
            for r in results:
                st.write(f"- Score: {r['score']}, Text: {r['text'][:200]}...")

            # Placeholder for LLM integration
            st.write("**Chatbot Answer (placeholder)**: This is where the LLM would produce a summary of the retrieved context.")

def create_index_if_not_exists(client, index_name):
    # Example 384 dimension
    mapping = {
        "settings": {
            "index": {
                "knn": True
            }
        },
        "mappings": {
            "properties": {
                "text": {"type": "text"},
                "text_vector": {
                    "type": "knn_vector",
                    "dimension": 384
                }
            }
        }
    }

    if not client.indices.exists(index=index_name):
        response = client.indices.create(index=index_name, body=mapping)
        print(f"Index created: {response}")
    else:
        print(f"Index '{index_name}' already exists.")

def flatten_data_for_indexing(data, docs=None, prefix=""):
    """
    Recursively traverse scraped data, return a list of documents for indexing:
      [{"id": "unique_id", "text": "...", "metadata": {...}}, ...]
    """
    if docs is None:
        docs = []

    if not data:
        return docs

    # Use the URL or some unique info as the ID
    doc_id = data.get("url", prefix + "root")
    text_content = data.get("text", "")
    # You can store metadata such as URL, tables, images, etc.
    metadata = {
        "url": data.get("url"),
        # Potentially add tables or images references
    }

    if text_content.strip():
        docs.append({
            "id": doc_id,
            "text": text_content,
            "metadata": metadata
        })

    # Recursively handle subpages
    for sub in data.get("subpages", []):
        flatten_data_for_indexing(sub, docs, prefix=doc_id)

    return docs

if __name__ == "__main__":
    main()
