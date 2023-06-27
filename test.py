from api import *

test_endpoint = "https://test.wikidata.org/w/rest.php/wikibase/v0"

def test_create_apisession():
    testobj = WikibaseRestAPI()
    assert testobj.api_key == None
    assert testobj.api_secret == None
    assert testobj.endpoint == wikidata_endpoint
    assert testobj.access_token == None
    assert testobj.base_headers == {"Content-Type": "application/json"}
    assert WikibaseRestAPI(endpoint=test_endpoint).endpoint == test_endpoint
    assert WikibaseRestAPI(access_token="abcdefg").base_headers == {
        "Content-Type": "application/json",
        "Authorization": "Bearer abcdefg"
    }

def test_getters():
    testobj = WikibaseRestAPI(endpoint=test_endpoint)
    request = requests.get(test_endpoint + "/entities/items/Q41487")
    benchmark = request.json()
    assert testobj.get_item("Q41487") == benchmark
    assert testobj.get_item_labels("Q41487") == benchmark["labels"]
    assert testobj.get_item_descriptions("Q41487") == benchmark["descriptions"]
    assert testobj.get_item_aliases("Q41487") == benchmark["aliases"]
    assert testobj.get_item_statements("Q41487") == benchmark["statements"]

def run_tests():
    test_create_apisession()
    test_getters()
    print("Tests complete.")

if __name__ == "__main__":
    run_tests()
