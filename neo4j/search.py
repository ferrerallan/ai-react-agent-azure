#!/usr/bin/env python3

import sys
from neo4j import GraphDatabase

# Ajuste para o endereço e senha corretos
NEO4J_URI = "bolt://20.9.140.20:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "neo123456"

def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with driver.session() as session:
        
        print("=== LISTA DE USUÁRIOS ===")
        result_users = session.run("MATCH (u:User) RETURN u.userId AS userId, u.name AS name")
        for record in result_users:
            print(f"UserID: {record['userId']}, Name: {record['name']}")

        print("\n=== AMIZADES ===")
        result_friends = session.run("""
            MATCH (u1:User)-[:FRIENDS_WITH]->(u2:User)
            RETURN u1.name AS user1, u2.name AS user2
        """)
        for record in result_friends:
            print(f"{record['user1']} é amigo de {record['user2']}")

        print("\n=== COMPRAS ===")
        result_purchases = session.run("""
            MATCH (u:User)-[:PURCHASED]->(p:Product)
            RETURN u.name AS user, p.name AS product
        """)
        for record in result_purchases:
            print(f"{record['user']} comprou {record['product']}")

        print("\n=== LISTA DE PRODUTOS ===")
        result_products = session.run("""
            MATCH (p:Product)
            RETURN p.name AS name, p.brand AS brand, p.category AS category
        """)
        for record in result_products:
            print(f"Produto: {record['name']}, Marca: {record['brand']}, Categoria: {record['category']}")

    driver.close()
    print("\nConsultas concluídas com sucesso!")

if __name__ == "__main__":
    main()
