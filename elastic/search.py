import os
import openai
import numpy as np
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

load_dotenv()

ELASTIC_ENDPOINT = os.getenv("ELASTIC_ENDPOINT")
ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")
ELASTIC_INDEX_NAME = "products"
openai.api_key = os.getenv("OPENAI_API_KEY")

def connect_to_elasticsearch():
    try:
        auth_params = {}
        if ELASTIC_API_KEY:
            if ":" in ELASTIC_API_KEY:
                parts = ELASTIC_API_KEY.split(":")
                auth_params["api_key"] = (parts[0], parts[1])
            else:
                auth_params["headers"] = {"Authorization": f"ApiKey {ELASTIC_API_KEY}"}
        es = Elasticsearch(ELASTIC_ENDPOINT, verify_certs=True, **auth_params)
        print(f"Connected: {es.info()}")
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
        return np.random.rand(1536).tolist()

def semantic_search(es, query_text, size=3, min_score_percentage=75):
    raw_min_score = min_score_percentage / 50.0  # Convert to raw score (0 to 2 scale)
    query_vector = generate_embedding(query_text)
    body = {
        "size": size,
        "min_score": raw_min_score,
        "query": {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                    "params": {"query_vector": query_vector}
                }
            }
        }
    }
    try:
        response = es.search(index=ELASTIC_INDEX_NAME, body=body)
        return response['hits']['hits']
    except Exception as e:
        print(f"Search error: {e}")
        return []

def main():
    es = connect_to_elasticsearch()
    if not es:
        return
    query_text = input("Enter search query: ")
    results = semantic_search(es, query_text, size=3, min_score_percentage=80)
    print("Results:")
    for hit in results:
        source = hit['_source']
        raw_score = hit['_score']
        score_percentage = raw_score * 50  # Convert raw score (0-2 scale) to percentage (0-100)
        print(f"Score: {score_percentage:.2f} - {source.get('name')}: {source.get('description')}")

if __name__ == "__main__":
    main()
