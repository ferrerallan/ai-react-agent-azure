import os
import json
import openai
import numpy as np
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

load_dotenv()

# Altere o protocolo para HTTPS
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
        
        print(f"Tentando conectar a: {ELASTIC_HOST}")
        print(f"Usando autenticação: {bool(auth)}")
        
        # Adicionar configurações para HTTPS
        es = Elasticsearch(
            ELASTIC_HOST, 
            **auth,
            verify_certs=False,  # Ignora verificação de certificados
            ssl_show_warn=False  # Não mostra avisos SSL
        )
        print("Conectado:", es.info())
        return es
    except Exception as e:
        print("Erro de conexão:", e)
        print(f"Detalhes completos: {type(e).__name__}, {str(e)}")
        return None

def create_index(es, index_name=ELASTIC_INDEX_NAME):
    if es.indices.exists(index=index_name):
        print(f"Index '{index_name}' exists.")
        return True
    mapping = {
        "mappings": {
            "properties": {
                "product_id": {"type": "keyword"},
                "name": {"type": "text"},
                "description": {"type": "text"},
                "category": {"type": "keyword"},
                "brand": {"type": "keyword"},
                "price": {"type": "float"},
                "features": {"type": "text"},
                "embedding": {
                    "type": "dense_vector",
                    "dims": 1536,
                    "index": True,
                    "similarity": "cosine"
                }
            }
        }
    }
    try:
        es.indices.create(index=index_name, body=mapping)
        print(f"Index '{index_name}' created.")
        return True
    except Exception as e:
        print("Index creation error:", e)
        return False

def generate_embedding(text, model="text-embedding-ada-002"):
    try:
        response = openai.embeddings.create(input=text, model=model)
        return response.data[0].embedding
    except Exception as e:
        print("Embedding error:", e)
        return np.random.rand(1536).tolist()

def index_product(es, product, index_name=ELASTIC_INDEX_NAME):
    print(product)
    text = f"{product['category']}. {product['description']}"
    product['embedding'] = generate_embedding(text)
    try:
        res = es.index(index=index_name, document=product)
        print(f"Product '{product['name']}' indexed with ID: {res['_id']}")
        return res['_id']
    except Exception as e:
        print("Indexing error:", e)
        return None

def insert_sample_data(es, index_name=ELASTIC_INDEX_NAME):
    sample_products = [
        {
            "product_id": "P001",
            "name": "Samsung Galaxy S21",
            "description": (
                "Samsung Galaxy S21 smartphone with excellent features. "
                "Vibrant 6.2-inch AMOLED display, powerful triple camera system that captures high-quality images, "
                "long-lasting battery and smooth performance."
            ),
            "category": "Smartphones",
            "brand": "Samsung",
            "price": 799.99,
            "features": ["Smartphone", "AMOLED", "Triple Camera", "Good Photos", "Long Battery"]
        },
        {
            "product_id": "P002",
            "name": "iPhone 13",
            "description": (
                "iPhone 13 smartphone known for outstanding performance and camera quality. "
                "Equipped with A15 Bionic chip and dual 12MP camera delivering vibrant images, sleek design and intuitive iOS."
            ),
            "category": "Smartphones",
            "brand": "Apple",
            "price": 899.99,
            "features": ["Smartphone", "A15 Bionic", "Dual Camera", "Great Photos", "Sleek Design"]
        },
        {
            "product_id": "P003",
            "name": "Nike Running Shoes",
            "description": (
                "Nike Running Shoes designed for optimal performance on the track. "
                "Lightweight, breathable, with excellent cushioning and traction."
            ),
            "category": "Sports",
            "brand": "Nike",
            "price": 129.99,
            "features": ["Running Shoes", "Comfort", "Cushioning", "Traction", "Lightweight"]
        },
        {
            "product_id": "P004",
            "name": "Fitbit Charge 5",
            "description": (
                "Fitbit Charge 5 health tracker with advanced sensors for monitoring heart rate, sleep, and activity. "
                "Features a vibrant display and comprehensive health insights."
            ),
            "category": "Health",
            "brand": "Fitbit",
            "price": 179.99,
            "features": ["Health Tracker", "Heart Rate", "Sleep Monitor", "Fitness Insights", "Vibrant Display"]
        },
        {
            "product_id": "P005",
            "name": "Yamaha Acoustic Guitar",
            "description": (
                "Yamaha Acoustic Guitar delivering a warm, balanced sound ideal for both beginners and professionals. "
                "Excellent playability and quality construction."
            ),
            "category": "Musical Instruments",
            "brand": "Yamaha",
            "price": 249.99,
            "features": ["Acoustic Guitar", "Warm Sound", "Balanced Tone", "Beginner Friendly", "Quality Build"]
        },
        {
            "product_id": "P006",
            "name": "Dell XPS 15",
            "description": (
                "Dell XPS 15 laptop featuring a powerful processor, stunning display, and long battery life. "
                "Ideal for high performance work and entertainment."
            ),
            "category": "Electronics",
            "brand": "Dell",
            "price": 1499.99,
            "features": ["Laptop", "High Performance", "Stunning Display", "Long Battery", "Professional"]
        },
        {
            "product_id": "P007",
            "name": "Wilson Tennis Racket",
            "description": (
                "Wilson Tennis Racket engineered for precision and control on the court. "
                "Lightweight and durable, offering excellent maneuverability."
            ),
            "category": "Sports",
            "brand": "Wilson",
            "price": 199.99,
            "features": ["Tennis Racket", "Precision", "Control", "Lightweight", "Durable"]
        }
    ]
    for product in sample_products:
        index_product(es, product, index_name)
    es.indices.refresh(index=index_name)
    print("Sample data inserted and index refreshed.")

def main():
    es = connect_to_elasticsearch()
    if not es:
        print("Connection failed.")
        return
    create_index(es)
    insert_sample_data(es)
    print("Ingestion complete.")

if __name__ == "__main__":
    main()