from sparql_tool import run_sparql

query = """
PREFIX ex:<http://example.org/>

SELECT ?zi
WHERE{
    ex:文彭 ex:courtesyName ?zi .
}
"""

data = run_sparql(query)

zi = data["results"]["bindings"][0]["zi"]["value"]

print(zi)