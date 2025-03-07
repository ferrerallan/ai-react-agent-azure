import os
import json
import openai
import numpy as np
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

load_dotenv()

ELASTIC_HOST = os.getenv("ELASTIC_HOST", "https://localhost:9200")
ELASTIC_USERNAME = os.getenv("ELASTIC_USERNAME")
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD")
ELASTIC_INDEX_NAME = "products"
openai.api_key = os.getenv("OPENAI_API_KEY")

def connect_to_elasticsearch():
    try:
        auth = {}
        if ELASTIC_USERNAME and ELASTIC_PASSWORD:
            auth["basic_auth"] = (ELASTIC_USERNAME, ELASTIC_PASSWORD)
        
        # Add configurations for HTTPS
        es = Elasticsearch(
            ELASTIC_HOST, 
            **auth,
            verify_certs=False,  # Ignore certificate verification
            ssl_show_warn=False  # Don't show SSL warnings
        )
        return es
    except Exception as e:
        print(f"Connection error: {e}")
        return None

def generate_embedding(text, model="text-embedding-ada-002"):
    try:
        response = openai.embeddings.create(input=text, model=model)
        return response.data[0].embedding
    except Exception as e:
        print(f"Embedding error: {e}")
        return None

def search_by_term(es, search_term, index_name=ELASTIC_INDEX_NAME):
    """Search by term using text search"""
    try:
        query = {
            "query": {
                "multi_match": {
                    "query": search_term,
                    "fields": ["name", "description", "category", "brand", "features"]
                }
            }
        }
        
        response = es.search(index=index_name, body=query)
        return response["hits"]["hits"]
    except Exception as e:
        print(f"Term search error: {e}")
        return []

def search_by_vector(es, search_text, index_name=ELASTIC_INDEX_NAME, top_k=3):
    """Semantic search using vector embedding"""
    try:
        # Generate embedding for search text
        embedding = generate_embedding(search_text)
        if not embedding:
            return []
            
        # Build vector similarity query
        query = {
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                        "params": {"query_vector": embedding}
                    }
                }
            },
            "size": top_k
        }
        
        response = es.search(index=index_name, body=query)
        return response["hits"]["hits"]
    except Exception as e:
        print(f"Vector search error: {e}")
        return []

def format_results(results):
    """Format results for display"""
    if not results:
        return "No results found."
        
    formatted = []
    for i, hit in enumerate(results, 1):
        source = hit["_source"]
        score = hit["_score"]
        
        product_info = (
            f"{i}. {source['name']} ({source['brand']})\n"
            f"   Category: {source['category']}\n"
            f"   Price: ${source['price']}\n"
            f"   Score: {score:.4f}\n"
            f"   Description: {source['description'][:100]}...\n"
        )
        formatted.append(product_info)
    
    return "\n".join(formatted)

def run_search(search_query, mode="both", top_k=3):
    es = connect_to_elasticsearch()
    if not es:
        return "Failed to connect to Elasticsearch."
    
    results = []
    
    if mode in ["text", "both"]:
        print("\n=== TEXT SEARCH RESULTS ===")
        text_results = search_by_term(es, search_query)
        print(format_results(text_results))
        results.append(("TEXT SEARCH", text_results))
    
    if mode in ["vector", "both"]:
        print("\n=== SEMANTIC SEARCH RESULTS ===")
        vector_results = search_by_vector(es, search_query, top_k=top_k)
        print(format_results(vector_results))
        results.append(("SEMANTIC SEARCH", vector_results))
    
    return results

def main():
    # List of queries to test
    example_queries = [
        "smartphone with good camera",
        "fitness equipment",
        "musical instrument for beginners",
        "laptop for work",
        "sports product"
    ]
    
    print("=== ELASTICSEARCH SEARCH SYSTEM ===\n")
    
    while True:
        print("\nChoose an option:")
        print("1. Use a predefined query")
        print("2. Enter your own query")
        print("3. Exit")
        
        choice = input("Option: ")
        
        if choice == "1":
            print("\nAvailable queries:")
            for i, query in enumerate(example_queries, 1):
                print(f"{i}. {query}")
            
            query_choice = input("\nChoose a query (1-5): ")
            try:
                query_index = int(query_choice) - 1
                if 0 <= query_index < len(example_queries):
                    search_query = example_queries[query_index]
                    print(f"\nSearching for: '{search_query}'")
                    run_search(search_query)
                else:
                    print("Invalid choice.")
            except ValueError:
                print("Please enter a number.")
        
        elif choice == "2":
            search_query = input("\nEnter your query: ")
            if search_query.strip():
                run_search(search_query)
            else:
                print("Query cannot be empty.")
        
        elif choice == "3":
            print("\nExiting program. Goodbye!")
            break
        
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()