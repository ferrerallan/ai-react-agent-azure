import os
import json
import openai
import numpy as np
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
from typing import Optional
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from neo4j import GraphDatabase




# Helper: Generate an embedding from text using OpenAI.
def generate_embedding(text: str, model: str = "text-embedding-ada-002") -> list:
    try:
        response = openai.embeddings.create(input=text, model=model)
        return response.data[0].embedding
    except Exception as e:
        print(f"Embedding error: {e}")
        return np.random.rand(1536).tolist()

@tool
def search_products_by_embedding(query: str) -> str:
    """
    Searches for products semantically similar to the user's query.
    Use this tool ONLY when the user is looking for specific product features or characteristics.
    DO NOT use this tool for promotion requests or social recommendations.
    
    :param query: Text describing what the user is looking for
    :param category: Optional category to filter results
    :return: List of products similar to the query
    """
    print("***** VECTOR SEARCH TOOL *****")
    print(f"Query: {query}")

    # Check if running in local environment
    is_local = os.getenv("LOCAL", "false").lower() == "true"
    
    if is_local:
        # Local environment configuration
        ELASTIC_ENDPOINT = os.getenv("ELASTIC_HOST", "https://localhost:9200")
        ELASTIC_USERNAME = os.getenv("ELASTIC_USERNAME", "elastic")
        ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD", "elastic")
        auth_params = {"basic_auth": (ELASTIC_USERNAME, ELASTIC_PASSWORD)}
    else:
        # Azure environment configuration
        ELASTIC_ENDPOINT = os.getenv("ELASTIC_ENDPOINT", "https://elastic-products.es.westus2.azure.elastic-cloud.com")
        ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")
        
        auth_params = {}
        if ELASTIC_API_KEY:
            if ":" in ELASTIC_API_KEY:
                parts = ELASTIC_API_KEY.split(":")
                auth_params["api_key"] = (parts[0], parts[1])
            else:
                auth_params["headers"] = {"Authorization": f"ApiKey {ELASTIC_API_KEY}"}

    ELASTIC_INDEX_NAME = "products"

    try:
        verify_certs = not is_local
        es = Elasticsearch(ELASTIC_ENDPOINT, verify_certs=verify_certs, **auth_params)
    except Exception as e:
        return f"Connection error: {e}"

    query_vector = generate_embedding(query)
    min_score_percentage = 85
    raw_min_score = min_score_percentage / 50.0  # converts to raw score on a 0-2 scale

    search_body = {
        "size": 10,
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
        response = es.search(index=ELASTIC_INDEX_NAME, body=search_body)
        hits = response['hits']['hits']
    except Exception as e:
        return f"Search error: {e}"

    if not hits:
        return "No products found matching your query."

    result = "Products found based on your description:\n\n"
    for hit in hits:
        source = hit['_source']
        result += f"Name: {source.get('name')}\n"
        result += f"Category: {source.get('category')}\n"
        result += f"Brand: {source.get('brand')}\n"
        result += f"Description: {source.get('description')}\n"
        result += f"Price: ${source.get('price'):.2f}\n\n"

    return result

@tool
def get_social_recommendations(user_id: str = "Bob") -> str:
    """
    Gets product recommendations based on the user's social network (friends or friends-of-friends).
    Use this tool when the user asks for recommendations based on their social network or what's popular.
    
    :param user_id: The user ID for whom we want social recommendations
    :return: Formatted list of products recommended based on that user's network
    """

    is_local = os.getenv("LOCAL", "false").lower() == "true"

    if is_local:
        NEO4J_URI = os.getenv("NEO4J_URI")
        NEO4J_USER = os.getenv("NEO4J_USER")
        NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
    else:
        NEO4J_URI = os.getenv("NEO4J_URI_AZURE")
        NEO4J_USER = os.getenv("NEO4J_USER_AZURE")
        NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD_AZURE")

    print("***** SOCIAL GRAPH TOOL *****")
    clear_user = user_id.lower().replace("user_id", "").replace("'", "").replace("=", "").strip()
    print(f"User ID: {clear_user}")

    # Connect to Neo4j
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD) )

    # Cypher query to find products purchased by user's friends or friends-of-friends
    query = """
    MATCH (u:User {userId: $user_id})-[:FRIENDS_WITH*1..2]-(x:User)-[:PURCHASED]->(p:Product)
    RETURN p.name AS name,
           p.category AS category,
           p.brand AS brand,
           p.description AS description,
           p.price AS price,
           count(*) AS social_count
    ORDER BY social_count DESC
    """

    try:
        with driver.session() as session:
            records = session.run(query, user_id=clear_user)
            results = [record.data() for record in records]
    except Exception as e:
        return f"Error querying social recommendations: {str(e)}"
    finally:
        driver.close()

    # If no products found
    if not results:
        return f"No products found in the social network of user '{clear_user}'."

    # Group results by category
    categories = {}
    for r in results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(r)

    # Build output
    output = "Popular products in your friend network:\n\n"

    # Show category breakdown
    if len(categories) > 1:
        output += "Category breakdown:\n"
        for cat, items in categories.items():
            output += f"- {cat}: {len(items)} products\n"
        output += "\n"

    # Show product details
    for r in results:
        output += f"Name: {r['name']}\n"
        output += f"Category: {r['category']}\n"
        output += f"Brand: {r['brand']}\n"
        output += f"Description: {r['description']}\n"
        output += f"Price: ${r['price']:.2f}\n"
        output += f"Social: {r['social_count']} friends or friends-of-friends purchased this\n\n"

    return output

@tool
def get_promotion_by_category(category: str = "all") -> str:
    """
    Searches for products on promotion with their prices and details.
    IMPORTANT: This tool ALWAYS returns complete product information including prices.
    Use this tool for any promotion-related queries.
    DO NOT use this tool for promotion requests or social recommendations.
    
    :param category: Product category or "all" for all promotions
    :return: List of products on promotion with complete details including prices
    """
    
    print("***** PROMOTION TOOL *****")
    # Normalize the category input
    category = category.strip().lower()
    # Handle different variations of "all"
    all_categories = ["all", "all categories", "any", "everything", "", "all products"]
    
    # Promotion API simulation data
    mock_promotions = {
        "smartphones": [
            {
                "name": "Xiaomi Redmi Note 11",
                "category": "Smartphones", 
                "brand": "Xiaomi",
                "description": "Smartphone with 6.4 inch display, quad camera, 6GB RAM",
                "price": 349.99
            }
        ],
        "accessories": [
            {
                "name": "Galaxy Buds Pro",
                "category": "Accessories",
                "brand": "Samsung",
                "description": "Wireless earbuds with active noise cancellation",
                "price": 149.99
            }
        ],
        "footwear": [
            {
                "name": "Nike Air Zoom Pegasus 38",
                "category": "Footwear",
                "brand": "Nike",
                "description": "Running shoes with Zoom Air cushioning",
                "price": 119.99
            }   
        ]
    }
    
    # Show all promotions if requested
    if any(cat in category for cat in all_categories):
        all_promotions = []
        for cat_name, products in mock_promotions.items():
            all_promotions.extend(products)
        
        if not all_promotions:
            return "No promotions available at the moment."
        
        result = "Current promotions across all categories:\n\n"
        for product in all_promotions:
            result += f"Name: {product['name']}\n"
            result += f"Category: {product['category']}\n"
            result += f"Brand: {product['brand']}\n"
            result += f"Description: {product['description']}\n"
            result += f"Promotional price: ${product['price']:.2f}\n\n"
        
        return result
    
    # Try to find a matching category
    for cat_key in mock_promotions.keys():
        if cat_key in category or category in cat_key:
            promotions = mock_promotions[cat_key]
            result = f"Products on promotion in {cat_key} category:\n\n"
            
            for product in promotions:
                result += f"Name: {product['name']}\n"
                result += f"Category: {product['category']}\n"
                result += f"Brand: {product['brand']}\n"
                result += f"Description: {product['description']}\n"
                result += f"Promotional price: ${product['price']:.2f}\n\n"
            
            return result
    
    # If nothing found, return all promotions
    all_promotions = []
    for cat_name, products in mock_promotions.items():
        all_promotions.extend(products)
    
    result = "No exact category match found. Here are all current promotions:\n\n"
    for product in all_promotions:
        result += f"Name: {product['name']}\n"
        result += f"Category: {product['category']}\n"
        result += f"Brand: {product['brand']}\n"
        result += f"Description: {product['description']}\n"
        result += f"Promotional price: ${product['price']:.2f}\n\n-----------------\n"
    
    return result

@tool
def general_chat(input: str) -> str:
    """
    Handles general conversation and questions not specifically about product search, promotions, or social recommendations.
    Use this tool for greetings, general questions, or any input that doesn't fit the other specialized tools.
    
    :param input: The user's input
    :return: A natural, helpful response but with a little nudge toward products
    """
    print("***** GENERAL CHAT TOOL *****")
    
    # Here we would normally make another call to the LLM
    # For the training implementation, we'll use a simplified approach
    
    # Create a response that acknowledges the user's input and guides toward products
    llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0.7)
    
    response = llm.invoke(
        f"""
        The user said: "{input}"
        
        Respond naturally to this message, but find a smooth way to steer the conversation 
        toward product recommendations, promotions, or popular products. Be conversational 
        and friendly, but subtly guide them to ask about products. Keep your response concise.
        """
    )
    
    return response.content

@tool
def verify_recommendation_consistency(recommendation_data: str) -> str:
    """
    Verifies the consistency of product recommendations using an LLM.
    Use this tool as the final step to ensure accurate recommendations without inconsistencies.
    
    :param recommendation_data: String containing the query and results from all tools used
    :return: A verified, accurate response
    """
    print("***** VERIFICATION TOOL *****")
    
    # We would use the LLM to analyze the data and identify inconsistencies
    llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)
    
    response = llm.invoke(
        f"""
        Analyze the following recommendation data and identify any inconsistencies:
        
        {recommendation_data}
        
        Your task:
        1. Check if any products are claimed to match criteria when they don't
        2. Identify which products truly match each criterion
        3. Provide an accurate response that doesn't overstate what was found
        4. when a product doesn't meet all criteria, limit responding to what it does meet
        
        Format your response as if you're directly addressing the user's original query.
        Don't mention this verification process in your response.
        """
    )
    
    return response.content