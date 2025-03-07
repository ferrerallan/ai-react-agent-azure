CREATE (p1:Person {name: "Ana"})
CREATE (p2:Person {name: "Carlos"})
CREATE (p3:Person {name: "Mariana"})
CREATE (p4:Person {name: "João"})
CREATE (p5:Person {name: "Fernanda"})
CREATE (p6:Person {name: "Lucas"})
CREATE (p7:Person {name: "Ricardo"})
CREATE (p8:Person {name: "Beatriz"})
CREATE (p9:Person {name: "Tiago"})
CREATE (p10:Person {name: "Gabriela"})
-----

MATCH (p1:Person {name: "Ana"}), (p2:Person {name: "Carlos"})
CREATE (p1)-[:KNOWS]->(p2);

MATCH (p2:Person {name: "Carlos"}), (p3:Person {name: "Mariana"})
CREATE (p2)-[:KNOWS]->(p3);

MATCH (p3:Person {name: "Mariana"}), (p4:Person {name: "João"})
CREATE (p3)-[:KNOWS]->(p4);

MATCH (p4:Person {name: "João"}), (p5:Person {name: "Fernanda"})
CREATE (p4)-[:KNOWS]->(p5);

MATCH (p5:Person {name: "Fernanda"}), (p6:Person {name: "Lucas"})
CREATE (p5)-[:KNOWS]->(p6);

MATCH (p6:Person {name: "Lucas"}), (p7:Person {name: "Ricardo"})
CREATE (p6)-[:KNOWS]->(p7);

MATCH (p7:Person {name: "Ricardo"}), (p8:Person {name: "Beatriz"})
CREATE (p7)-[:KNOWS]->(p8);

MATCH (p8:Person {name: "Beatriz"}), (p9:Person {name: "Tiago"})
CREATE (p8)-[:KNOWS]->(p9);

MATCH (p9:Person {name: "Tiago"}), (p10:Person {name: "Gabriela"})
CREATE (p9)-[:KNOWS]->(p10);


----
CREATE (:Vehicle {type: "Carro", model: "Toyota Corolla", year: 2022})
CREATE (:Vehicle {type: "Moto", model: "Honda CB500", year: 2021})
CREATE (:Vehicle {type: "Carro", model: "Ford Mustang", year: 2020})
CREATE (:Vehicle {type: "Moto", model: "Yamaha MT-07", year: 2023})

----
MATCH (p1:Person {name: "Ana"}), (v1:Vehicle {model: "Toyota Corolla"})
CREATE (p1)-[:BOUGHT]->(v1);

MATCH (p2:Person {name: "Carlos"}), (v2:Vehicle {model: "Honda CB500"})
CREATE (p2)-[:BOUGHT]->(v2);

MATCH (p3:Person {name: "Mariana"}), (v3:Vehicle {model: "Ford Mustang"})
CREATE (p3)-[:BOUGHT]->(v3);

MATCH (p4:Person {name: "João"}), (v4:Vehicle {model: "Yamaha MT-07"})
CREATE (p4)-[:BOUGHT]->(v4);

MATCH (p5:Person {name: "Fernanda"}), (v1:Vehicle {model: "Toyota Corolla"})
CREATE (p5)-[:BOUGHT]->(v1);

MATCH (p6:Person {name: "Lucas"}), (v2:Vehicle {model: "Honda CB500"})
CREATE (p6)-[:BOUGHT]->(v2);

MATCH (p7:Person {name: "Ricardo"}), (v3:Vehicle {model: "Ford Mustang"})
CREATE (p7)-[:BOUGHT]->(v3);

MATCH (p8:Person {name: "Beatriz"}), (v4:Vehicle {model: "Yamaha MT-07"})
CREATE (p8)-[:BOUGHT]->(v4);


---

// Pessoas que compraram veículos do tipo Carro ou Moto
MATCH (p:Person)-[:BOUGHT]->(v:Vehicle)
WHERE v.type IN ["Carro", "Moto"]
RETURN p.name, v.type, v.model

// Buscar todas as pessoas conectadas a um nó específico (Ana), até 2 níveis de distância, e quais veículos essas pessoas compraram
MATCH (start:Person {name: "Ana"})-[:KNOWS*1..2]-(connected:Person)
OPTIONAL MATCH (connected)-[:BOUGHT]->(v:Vehicle)
RETURN start.name AS Origem, 
       connected.name AS Pessoa, 
       v.type AS Veiculo, 
       v.model AS Modelo, 
       length(shortestPath((start)-[:KNOWS*1..2]-(connected))) AS Nivel
ORDER BY Nivel, Pessoa

//Qual veiculo mais comprado entre amigos de Carlos
MATCH (c:Person {name: "Carlos"})-[:KNOWS]-(friend:Person)  
MATCH (friend)-[:BOUGHT]->(v:Vehicle)  
RETURN v.model AS Veiculo, v.type AS Tipo, COUNT(v) AS TotalCompras  
ORDER BY TotalCompras DESC  
LIMIT 1


