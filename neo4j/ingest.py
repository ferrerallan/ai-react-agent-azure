#!/usr/bin/env python3

import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Ajuste para o endereço e a senha corretos do seu Neo4j
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

def ingest_data(tx):
    # Cria alguns usuários
    tx.run("""
    MERGE (u:User {userId: 'allan'})
      ON CREATE SET u.name = 'Allan'
    MERGE (u2:User {userId: 'bob'})
      ON CREATE SET u2.name = 'Bob'
    MERGE (u3:User {userId: 'carol'})
      ON CREATE SET u3.name = 'Carol'
    """)

    # Cria relacionamentos de amizade
    tx.run("""
    MATCH (a:User {userId: 'allan'}),
          (b:User {userId: 'bob'}),
          (c:User {userId: 'carol'})
    MERGE (a)-[:FRIENDS_WITH]->(b)
    MERGE (b)-[:FRIENDS_WITH]->(c)
    """)

    # Cria alguns produtos
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
    """)

    # Cria relacionamentos de compra
    tx.run("""
    MATCH (bob:User {userId: 'bob'}),
          (carol:User {userId: 'carol'}),
          (buds:Product {name: 'Galaxy Buds Pro'}),
          (tv:Product {name: 'Smart TV 55" Crystal UHD 4K'})
    MERGE (bob)-[:PURCHASED]->(buds)
    MERGE (carol)-[:PURCHASED]->(buds)
    MERGE (carol)-[:PURCHASED]->(tv)
    """)

def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with driver.session() as session:
        session.write_transaction(ingest_data)
    driver.close()
    print("Ingestão concluída!")

if __name__ == "__main__":
    main()
