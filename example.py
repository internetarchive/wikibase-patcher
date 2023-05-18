"""
This example script uses the Domains Wikibase <https://domains.wikibase.cloud>
as an example. In this example, the Domains Wikibase is queried for values of
Property P7 with a certain value, and then replaces them with new statements.
"""

import requests
from api import *
from entity import *

wikibase_endpoint = "https://domains.wikibase.cloud/w/rest.php/wikibase/v0"
sparql_endpoint = "https://domains.wikibase.cloud/query/sparql"

# Query for entities with P7 values of a certain URL
query = """
    PREFIX wdt: <https://domains.wikibase.cloud/prop/direct/>
    PREFIX wd: <https://domains.wikibase.cloud/entity/> 
    SELECT ?item
    WHERE 
    {
      ?item wdt:P7 <https://domains.wikibase.cloud/ontology/worldnews/abyznewslinks> .
    }
"""

response = requests.get(sparql_endpoint, params={'query': query, 'format': 'json'})
results = response.json()

# Initialize a REST API session
api = WikibaseRestAPI(access_token="your_access_token", endpoint=wikibase_endpoint)

for result in results["results"]["bindings"]:
    # Extract the Q number from the URL
    q_number = result["item"]["value"].split('/')[-1]

    # Instantiate a WikibaseEntity object
    entity = WikibaseEntity(api, q_number)

    # Get the current P7 statements
    p7_statements = entity.api.get_item_statements(q_number)["statements"]["P7"]

    # For each P7 statement
    for statement in p7_statements:

        # If the statement's value matches the old URL
        if statement["mainsnak"]["datavalue"]["value"] == "https://domains.wikibase.cloud/ontology/worldnews/abyznewslinks":

            # Update the statement with the new URL
            statement["mainsnak"]["datavalue"]["value"] = "http://www.abyznewslinks.com/"
            entity.api.update_statement(statement["id"], statement)
