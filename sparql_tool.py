import requests

ENDPOINT = "http://localhost:3030/calligraphy/sparql"

def run_sparql(query):

    response = requests.post(
        ENDPOINT,
        data={"query": query},
        headers={
            "Accept": "application/sparql-results+json"
        }
    )

    return response.json()