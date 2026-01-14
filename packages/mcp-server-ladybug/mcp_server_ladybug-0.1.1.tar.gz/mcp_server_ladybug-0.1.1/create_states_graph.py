#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_server_ladybug.database import DatabaseClient

def main():
    # Initialize database client
    db = DatabaseClient(db_path=":memory:")

    # Create schema
    print("Creating schema...")

    # Create State node table
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

    # Create City node table
    db.query("""
    CREATE NODE TABLE City (
        name STRING PRIMARY KEY,
        state_name STRING
    );
    """)

    # Create relationship table
    db.query("""
    CREATE REL TABLE CapitalOf (FROM City TO State);
    """)

    print("Schema created successfully.")

    # Insert states data
    print("Inserting states data...")
    states_data = [
        ("Alabama", "AL", "Montgomery", "South", "East South Central", 5024279, 52420, 1819),
        ("Alaska", "AK", "Juneau", "West", "Pacific", 733391, 665384, 1959),
        ("Arizona", "AZ", "Phoenix", "West", "Mountain", 7151502, 113990, 1912),
        ("Arkansas", "AR", "Little Rock", "South", "West South Central", 3011524, 53179, 1836),
        ("California", "CA", "Sacramento", "West", "Pacific", 39538223, 163695, 1850),
        ("Colorado", "CO", "Denver", "West", "Mountain", 5773714, 104094, 1876),
        ("Connecticut", "CT", "Hartford", "Northeast", "New England", 3605944, 5543, 1788),
        ("Delaware", "DE", "Dover", "South", "South Atlantic", 989948, 2489, 1787),
        ("Florida", "FL", "Tallahassee", "South", "South Atlantic", 21538187, 65758, 1845),
        ("Georgia", "GA", "Atlanta", "South", "South Atlantic", 10711908, 59425, 1777),
        ("Hawaii", "HI", "Honolulu", "West", "Pacific", 1455271, 10932, 1959),
        ("Idaho", "ID", "Boise", "West", "Mountain", 1839106, 83569, 1890),
        ("Illinois", "IL", "Springfield", "Midwest", "East North Central", 12812508, 57914, 1818),
        ("Indiana", "IN", "Indianapolis", "Midwest", "East North Central", 6785528, 36420, 1816),
        ("Iowa", "IA", "Des Moines", "Midwest", "West North Central", 3190369, 56273, 1846),
        ("Kansas", "KS", "Topeka", "Midwest", "West North Central", 2937880, 82278, 1861),
        ("Kentucky", "KY", "Frankfort", "South", "East South Central", 4505836, 40408, 1792),
        ("Louisiana", "LA", "Baton Rouge", "South", "West South Central", 4657757, 52378, 1812),
        ("Maine", "ME", "Augusta", "Northeast", "New England", 1344212, 35380, 1820),
        ("Maryland", "MD", "Annapolis", "South", "South Atlantic", 6177224, 12406, 1788),
        ("Massachusetts", "MA", "Boston", "Northeast", "New England", 6949503, 10554, 1788),
        ("Michigan", "MI", "Lansing", "Midwest", "East North Central", 10037776, 96714, 1837),
        ("Minnesota", "MN", "Saint Paul", "Midwest", "West North Central", 5706494, 86936, 1858),
        ("Mississippi", "MS", "Jackson", "South", "East South Central", 2961279, 48432, 1817),
        ("Missouri", "MO", "Jefferson City", "Midwest", "West North Central", 6154913, 69707, 1821),
        ("Montana", "MT", "Helena", "West", "Mountain", 1084225, 145546, 1889),
        ("Nebraska", "NE", "Lincoln", "Midwest", "West North Central", 1961504, 77348, 1867),
        ("Nevada", "NV", "Carson City", "West", "Mountain", 3104614, 110572, 1864),
        ("New Hampshire", "NH", "Concord", "Northeast", "New England", 1377529, 9349, 1788),
        ("New Jersey", "NJ", "Trenton", "Northeast", "Mid-Atlantic", 9288994, 8723, 1787),
        ("New Mexico", "NM", "Santa Fe", "West", "Mountain", 2117522, 121590, 1912),
        ("New York", "NY", "Albany", "Northeast", "Mid-Atlantic", 20201249, 54555, 1777),
        ("North Carolina", "NC", "Raleigh", "South", "South Atlantic", 10439388, 53819, 1789),
        ("North Dakota", "ND", "Bismarck", "Midwest", "West North Central", 779094, 70698, 1889),
        ("Ohio", "OH", "Columbus", "Midwest", "East North Central", 11799448, 44826, 1803),
        ("Oklahoma", "OK", "Oklahoma City", "South", "West South Central", 3959353, 69899, 1907),
        ("Oregon", "OR", "Salem", "West", "Pacific", 4237256, 98379, 1859),
        ("Pennsylvania", "PA", "Harrisburg", "Northeast", "Mid-Atlantic", 13002700, 46054, 1787),
        ("Rhode Island", "RI", "Providence", "Northeast", "New England", 1097379, 1545, 1790),
        ("South Carolina", "SC", "Columbia", "South", "South Atlantic", 5118425, 32020, 1788),
        ("South Dakota", "SD", "Pierre", "Midwest", "West North Central", 886667, 77116, 1889),
        ("Tennessee", "TN", "Nashville", "South", "East South Central", 6910840, 42144, 1796),
        ("Texas", "TX", "Austin", "South", "West South Central", 29145505, 268596, 1845),
        ("Utah", "UT", "Salt Lake City", "West", "Mountain", 3271616, 84897, 1896),
        ("Vermont", "VT", "Montpelier", "Northeast", "New England", 643077, 9616, 1791),
        ("Virginia", "VA", "Richmond", "South", "South Atlantic", 8631393, 42775, 1788),
        ("Washington", "WA", "Olympia", "West", "Pacific", 7693612, 71298, 1889),
        ("West Virginia", "WV", "Charleston", "South", "South Atlantic", 1793716, 24230, 1863),
        ("Wisconsin", "WI", "Madison", "Midwest", "East North Central", 5893718, 65496, 1848),
        ("Wyoming", "WY", "Cheyenne", "West", "Mountain", 576851, 97813, 1890),
    ]

    for state_name, abbr, capital, region, division, pop, area, year in states_data:
        query = f"""
        CREATE (s:State {{
            name: '{state_name}',
            abbreviation: '{abbr}',
            region: '{region}',
            division: '{division}',
            population: {pop},
            area_sq_mi: {area},
            statehood_year: {year}
        }});
        """
        db.query(query)

        # Create city node
        query = f"""
        CREATE (c:City {{
            name: '{capital}',
            state_name: '{state_name}'
        }});
        """
        db.query(query)

        # Create relationship
        query = f"""
        MATCH (c:City {{name: '{capital}'}}), (s:State {{name: '{state_name}'}})
        CREATE (c)-[:CapitalOf]->(s);
        """
        db.query(query)

    print("Data inserted successfully.")

    # Verify data
    print("Verifying data...")
    result = db.query("MATCH (s:State) RETURN count(s) AS state_count;")
    print(f"States count: {result}")

    result = db.query("MATCH (c:City) RETURN count(c) AS city_count;")
    print(f"Cities count: {result}")

    result = db.query("MATCH (c:City)-[:CapitalOf]->(s:State) RETURN count(*) AS relationship_count;")
    print(f"Relationships count: {result}")

    # Sample query
    result = db.query("MATCH (c:City)-[:CapitalOf]->(s:State) WHERE s.name = 'California' RETURN c.name, s.name;")
    print(f"California capital: {result}")

    db.close()

if __name__ == "__main__":
    main()