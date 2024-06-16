import requests
import pandas as pd
from pyrml import RMLConverter

print("Running RML rules")
converter = RMLConverter()
schema = converter.convert('maps.rml')
schema.serialize('output.ttl')

def upload_ttl_to_graphdb(ttl_file_path, endpoint):
    headers = {
        "Content-Type": "text/turtle"
    }

    with open(ttl_file_path, 'rb') as file:
        ttl_data = file.read()

    response = requests.post(endpoint, headers=headers, data=ttl_data)

    return response


file1 = 'realestate.ttl'
file2 = 'output.ttl'
graphdb_url = 'http://localhost:7200'
repo_name = 'repo'

print("Connecting to the repository")
endpoint = f"{graphdb_url}/repositories/{repo_name}/statements"
upload_ttl_to_graphdb(file1, endpoint)
upload_ttl_to_graphdb(file2, endpoint)



def run_sparql_query(endpoint, query):
    headers = {
        "Accept": "application/sparql-results+json, application/json"
    }

    params = {
        "query": query
    }

    try:
        response = requests.get(endpoint, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        results = data['results']['bindings']
        df = pd.DataFrame(
            [{var: binding[var]['value'] if var in binding else None for var in data['head']['vars']} for binding in
             results])
        return df
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
        return pd.DataFrame()

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
print('Running SPARQL queries')

endpoint = f"{graphdb_url}/repositories/{repo_name}"

query = """
prefix res: <http://real.estate.com/>

select ?c (count(?hs) as ?total_houses) (round(avg(?p)) as ?avg_price) ?happy where {
    ?c a res:Country.
	?c res:happinessScore ?happy.
    ?c res:hasHouse ?hs.
    ?hs res:price ?p.
} group by ?c ?happy order by desc(?happy)
"""

results = run_sparql_query(endpoint, query)
print('################################## QUERY 1 ####################################')
print(results)



query = """
prefix res: <http://real.estate.com/>

select ?c ?happy ?e ?f where {
    ?c a res:Country.
	?c res:happinessRank ?happy.
    ?c res:economyIndex ?e.
    ?c res:familyIndex ?f.
} order by desc(?happy)
"""


results = run_sparql_query(endpoint, query)
print('################################## QUERY 2 ####################################')
print(results)



query = """
prefix res: <http://real.estate.com/>

select ?hs ?d (?p/?tR as ?price_room_ratio) ?c ?f where {
    ?hs a res:House.
    ?hs res:description ?d.
    ?hs res:price ?p.
    ?hs res:totalRooms ?tR.
    ?hs res:countryLocation ?c.
    ?c res:freedomIndex ?f.
} order by ?price_room_ratio
"""

results = run_sparql_query(endpoint, query)
print('################################## QUERY 3 ####################################')
print(results)



query = """
prefix res: <http://real.estate.com/>

select ?hs ?c ?tF ?p where {
    ?hs a res:House.
    ?hs res:countryLocation ?c.
    ?c res:nameCountry "Spain".
    ?hs res:totalFloors ?tF.
    FILTER(?tF>4).
    ?hs res:price ?p.
} order by desc(?p)
"""

results = run_sparql_query(endpoint, query)
print('################################## QUERY 4 ####################################')
print(results)