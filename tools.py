# tools.py
from typing import Optional
from langchain_core.tools import tool

@tool
def search_products_by_embedding(query: str, category: Optional[str] = None) -> str:
    """
    Searches for products semantically similar to the user's query.
    Use this tool ONLY when the user is looking for specific product features or characteristics.
    DO NOT use this tool for promotion requests or social recommendations.
    
    :param query: Text describing what the user is looking for
    :param category: Optional category to filter results
    :return: List of products similar to the query
    """
    print("***** VECTOR SEARCH TOOL *****")
    
    # Here we would call Elasticsearch
    # For now, we'll simulate with mocked data
    mock_products = [
        {
            "name": "Samsung Galaxy S21",
            "category": "Smartphones",
            "brand": "Samsung",
            "description": "Smartphone with 6.2 inch AMOLED display, triple 64MP camera, 8GB RAM",
            "price": 799.99
        },
        {
            "name": "iPhone 13",
            "category": "Smartphones",
            "brand": "Apple",
            "description": "Smartphone with A15 Bionic processor, dual 12MP camera, 4GB RAM",
            "price": 899.99
        },
        {
            "name": "Xiaomi Redmi Note 11",
            "category": "Smartphones", 
            "brand": "Xiaomi",
            "description": "Smartphone with 6.4 inch display, quad camera, 6GB RAM",
            "price": 500.99
        }
    ]
    
    if category:
        mock_products = [p for p in mock_products if p["category"].lower() == category.lower()]
    
    if not mock_products:
        return "No products found matching your query."
    
    result = "Products found based on your description:\n\n"
    for product in mock_products:
        result += f"Name: {product['name']}\n"
        result += f"Category: {product['category']}\n"
        result += f"Brand: {product['brand']}\n"
        result += f"Description: {product['description']}\n"
        result += f"Price: ${product['price']:.2f}\n\n"
    
    return result




@tool
def get_social_recommendations(user_id: str = "default_user") -> str:
    """
    Gets product recommendations based on the user's social network (friends of friends).
    Use this tool when the user asks for recommendations based on their social network or what's popular.
    ALWAYS use this tool when the user asks about what other people are buying or what's trending.
    
    :param user_id: User ID
    :return: Products recommended based on social network
    """
    print("***** SOCIAL GRAPH TOOL *****")
    
    # Here we would query Neo4j
    # Simulation of query results
    mock_results = [
        {
            "name": "Galaxy Buds Pro",
            "category": "Accessories",
            "brand": "Samsung",
            "description": "Premium wireless earbuds with immersive audio and active noise cancellation",
            "price": 199.99,
            "social_count": 5
        },
        {
            "name": "Smart TV 55\" Crystal UHD 4K",
            "category": "Electronics",
            "brand": "Samsung",
            "description": "Smart TV with Crystal 4K processor, borderless design and integrated voice assistant",
            "price": 649.99,
            "social_count": 3
        },
        
        
    ]
    
    result = "Popular products in your friend network:\n\n"
    for product in mock_results:
        result += f"Name: {product['name']}\n"
        result += f"Category: {product['category']}\n"
        result += f"Brand: {product['brand']}\n"
        result += f"Description: {product['description']}\n"
        result += f"Price: ${product['price']:.2f}\n"
        result += f"Social: {product['social_count']} friends of your friends purchased this product\n\n"
    
    return result


@tool
def get_promotion_by_category(category: str = "all") -> str:
    """
    Searches for products on promotion with their prices and details.
    IMPORTANT: This tool ALWAYS returns complete product information including prices.
    Use this tool for any promotion-related queries.
    
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
        result += f"Promotional price: ${product['price']:.2f}\n\n"
    
    return result