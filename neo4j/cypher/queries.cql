CREATE (:Person {name: 'Ana'})-[:KNOWS]->(:Person {name: 'Carlos'})


CREATE (:Person {name: 'Ana'})
CREATE (:Person:Employee {name: 'Carlos', department: 'TI'})

MATCH (p:Person) RETURN p


MATCH (e:Employee) RETURN e.name, e.department


MATCH (p {name: 'Ana'}) 
SET p:Customer


MATCH (p:Employee {name: 'Carlos'}) 
REMOVE p:Employee


CREATE (n {name:'Ana'})


MATCH (p {name: 'Ana'}) 
SET p:Customer

MATCH (p:Employee {name: 'Carlos'}) 
REMOVE p:Employee

CREATE (:Person {name: 'Ana', age: 30})

CREATE (a:Person)-[:KNOWS {since: 2020, type: 'colleague'}]->(b:Person)

MATCH (p:Person)-[:KNOWS]->(friend)
RETURN p.name, friend.name



