#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_server_ladybug.database import DatabaseClient

def main():
    # Initialize database client with the same in-memory db (but it's empty now)
    # Since we need the data, let's recreate it quickly
    db = DatabaseClient(db_path=":memory:")

    # Quick recreation of schema and Arizona data
    db.query("""
    CREATE NODE TABLE State (
        name STRING PRIMARY KEY,
        abbreviation STRING,
        region STRING,
        division STRING,
        population INT64,
        area_sq_mi INT64,
        statehood_year INT64
    );
    """)

    db.query("""
    CREATE NODE TABLE City (
        name STRING PRIMARY KEY,
        state_name STRING
    );
    """)

    db.query("""
    CREATE REL TABLE CapitalOf (FROM City TO State);
    """)

    # Insert Arizona data
    db.query("""
    CREATE (s:State {
        name: 'Arizona',
        abbreviation: 'AZ',
        region: 'West',
        division: 'Mountain',
        population: 7151502,
        area_sq_mi: 113990,
        statehood_year: 1912
    });
    """)

    db.query("""
    CREATE (c:City {
        name: 'Phoenix',
        state_name: 'Arizona'
    });
    """)

    db.query("""
    MATCH (c:City {name: 'Phoenix'}), (s:State {name: 'Arizona'})
    CREATE (c)-[:CapitalOf]->(s);
    """)

    # Query the capital
    result = db.query("MATCH (c:City)-[:CapitalOf]->(s:State) WHERE s.name = 'Arizona' RETURN c.name;")
    print(result)

    db.close()

if __name__ == "__main__":
    main()