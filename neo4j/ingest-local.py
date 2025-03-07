#!/usr/bin/env python3

import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

def ingest_data(tx):
    # Create users
    tx.run("""
    MERGE (u1:User {userId: 'allan'})
      ON CREATE SET u1.name = 'Allan'
    MERGE (u2:User {userId: 'bob'})
      ON CREATE SET u2.name = 'Bob'
    MERGE (u3:User {userId: 'carol'})
      ON CREATE SET u3.name = 'Carol'
    MERGE (u4:User {userId: 'david'})
      ON CREATE SET u4.name = 'David'
    MERGE (u5:User {userId: 'emma'})
      ON CREATE SET u5.name = 'Emma'
    MERGE (u6:User {userId: 'frank'})
      ON CREATE SET u6.name = 'Frank'
    MERGE (u7:User {userId: 'grace'})
      ON CREATE SET u7.name = 'Grace'
    MERGE (u8:User {userId: 'henry'})
      ON CREATE SET u8.name = 'Henry'
    MERGE (u9:User {userId: 'isabel'})
      ON CREATE SET u9.name = 'Isabel'
    MERGE (u10:User {userId: 'jack'})
      ON CREATE SET u10.name = 'Jack'
    """)

    # Create friendship relationships (network topology)
    tx.run("""
    MATCH (allan:User {userId: 'allan'}),
          (bob:User {userId: 'bob'}),
          (carol:User {userId: 'carol'}),
          (david:User {userId: 'david'}),
          (emma:User {userId: 'emma'}),
          (frank:User {userId: 'frank'}),
          (grace:User {userId: 'grace'}),
          (henry:User {userId: 'henry'}),
          (isabel:User {userId: 'isabel'}),
          (jack:User {userId: 'jack'})
          
    // First-degree connections
    MERGE (allan)-[:FRIENDS_WITH]->(bob)
    MERGE (allan)-[:FRIENDS_WITH]->(carol)
    MERGE (bob)-[:FRIENDS_WITH]->(david)
    MERGE (carol)-[:FRIENDS_WITH]->(emma)
    MERGE (david)-[:FRIENDS_WITH]->(frank)
    MERGE (emma)-[:FRIENDS_WITH]->(grace)
    
    // Second-degree connections
    MERGE (frank)-[:FRIENDS_WITH]->(henry)
    MERGE (grace)-[:FRIENDS_WITH]->(isabel)
    
    // Third-degree connections
    MERGE (henry)-[:FRIENDS_WITH]->(jack)
    
    // Additional connections to create cycles
    MERGE (david)-[:FRIENDS_WITH]->(emma)
    MERGE (frank)-[:FRIENDS_WITH]->(grace)
    """)

    # Create products
    tx.run("""
    MERGE (p1:Product {name: 'Galaxy Buds Pro'})
      ON CREATE SET p1.brand = 'Samsung',
                    p1.category = 'Accessories',
                    p1.description = 'Premium wireless earbuds with immersive audio and active noise cancellation',
                    p1.price = 199.99
    MERGE (p2:Product {name: 'Smart TV 55" Crystal UHD 4K'})
      ON CREATE SET p2.brand = 'Samsung',
                    p2.category = 'Electronics',
                    p2.description = 'Smart TV with Crystal 4K processor, borderless design and integrated voice assistant',
                    p2.price = 649.99
    MERGE (p3:Product {name: 'iPhone 14 Pro'})
      ON CREATE SET p3.brand = 'Apple',
                    p3.category = 'Smartphones',
                    p3.description = 'Latest iPhone with A16 Bionic chip, 48MP camera, and Dynamic Island',
                    p3.price = 999.99
    MERGE (p4:Product {name: 'MacBook Air M2'})
      ON CREATE SET p4.brand = 'Apple',
                    p4.category = 'Laptops',
                    p4.description = 'Ultra-thin laptop with Apple Silicon M2 chip and all-day battery life',
                    p4.price = 1199.99
    MERGE (p5:Product {name: 'PlayStation 5'})
      ON CREATE SET p5.brand = 'Sony',
                    p5.category = 'Gaming',
                    p5.description = 'Next-gen gaming console with ray tracing, 3D audio, and fast SSD',
                    p5.price = 499.99
    MERGE (p6:Product {name: 'Kindle Paperwhite'})
      ON CREATE SET p6.brand = 'Amazon',
                    p6.category = 'E-readers',
                    p6.description = 'Waterproof e-reader with 300 ppi glare-free display and weeks of battery life',
                    p6.price = 139.99
    MERGE (p7:Product {name: 'AirPods Max'})
      ON CREATE SET p7.brand = 'Apple',
                    p7.category = 'Accessories',
                    p7.description = 'Over-ear headphones with Active Noise Cancellation and spatial audio',
                    p7.price = 549.99
    MERGE (p8:Product {name: 'Samsung Galaxy S23 Ultra'})
      ON CREATE SET p8.brand = 'Samsung',
                    p8.category = 'Smartphones',
                    p8.description = 'Flagship smartphone with 200MP camera, S Pen, and Snapdragon 8 Gen 2',
                    p8.price = 1199.99
    """)

    # Create purchase relationships
    tx.run("""
    MATCH (u:User), (p:Product)
    WHERE u.userId IN ['bob', 'carol', 'david', 'emma', 'frank', 'grace', 'henry', 'isabel', 'jack'] 
      AND p.name IN ['Galaxy Buds Pro', 'Smart TV 55" Crystal UHD 4K', 'iPhone 14 Pro', 
                     'MacBook Air M2', 'PlayStation 5', 'Kindle Paperwhite', 
                     'AirPods Max', 'Samsung Galaxy S23 Ultra']
    WITH u, p,
         CASE WHEN u.userId = 'bob' AND p.name IN ['Galaxy Buds Pro', 'PlayStation 5'] THEN true
              WHEN u.userId = 'carol' AND p.name IN ['Galaxy Buds Pro', 'Smart TV 55" Crystal UHD 4K', 'iPhone 14 Pro'] THEN true
              WHEN u.userId = 'david' AND p.name IN ['iPhone 14 Pro', 'AirPods Max'] THEN true
              WHEN u.userId = 'emma' AND p.name IN ['MacBook Air M2', 'AirPods Max'] THEN true
              WHEN u.userId = 'frank' AND p.name IN ['Samsung Galaxy S23 Ultra', 'Galaxy Buds Pro'] THEN true
              WHEN u.userId = 'grace' AND p.name IN ['Kindle Paperwhite', 'Smart TV 55" Crystal UHD 4K'] THEN true
              WHEN u.userId = 'henry' AND p.name IN ['PlayStation 5', 'Samsung Galaxy S23 Ultra'] THEN true
              WHEN u.userId = 'isabel' AND p.name IN ['iPhone 14 Pro', 'MacBook Air M2'] THEN true
              WHEN u.userId = 'jack' AND p.name IN ['Kindle Paperwhite'] THEN true
              ELSE false
         END as shouldPurchase
    WHERE shouldPurchase
    MERGE (u)-[:PURCHASED]->(p)
    """)

def main():
    # Connect to Neo4j with certificate verification disabled for local development
    is_local = os.getenv("LOCAL", "false").lower() == "true"
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    with driver.session() as session:
        session.write_transaction(ingest_data)
    
    driver.close()
    print("Data ingestion completed successfully!")

if __name__ == "__main__":
    main()