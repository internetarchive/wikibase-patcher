from api import *
import credentials
import hashlib
import time

test_endpoint = "https://test.wikidata.org/w/rest.php/wikibase/v0"

def make_up_string(tweak):
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    time_bytes = current_time.encode('utf-8')
    md5_hash = hashlib.md5()
    md5_hash.update(time_bytes + tweak.encode('utf-8'))
    md5_digest = md5_hash.hexdigest()
    return md5_digest

def test_create_apisession():
    testobj = WikibaseRestAPI()
    assert testobj.api_key is None
    assert testobj.api_secret is None
    assert testobj.endpoint == wikidata_endpoint
    assert testobj.access_token is None
    assert testobj.base_headers == {"Content-Type": "application/json"}
    assert WikibaseRestAPI(endpoint=test_endpoint).endpoint == test_endpoint
    assert WikibaseRestAPI(access_token="abcdefg").base_headers == {
        "Content-Type": "application/json",
        "Authorization": "Bearer abcdefg"
    }

def test_getters():
    # Corresponding to test.wikidata.org
    test_item = "Q41487"
    test_property = "P98435"
    language_code = "en"
    site_code = "commonswiki"
    other_language_code = "en-us"
    test_item_statement = "Q41487$afcef841-4ee6-4be6-3c62-eb4021c84eed"
    test_item_statement_property = "P286"
    test_property_statement = "P98435$f2550e05-42fa-3537-c0a9-16aa8038f3f5"
    test_property_statement_property = "P31"

    testobj = WikibaseRestAPI(endpoint=test_endpoint)
    request = requests.get(test_endpoint + f"/entities/items/{test_item}")
    benchmark = request.json()
    request_property = requests.get(test_endpoint + f"/entities/properties/{test_property}")
    benchmark_property = request_property.json()

    print("get_item")
    assert testobj.get_item(test_item) \
        == benchmark

    print("get_item_labels")
    assert testobj.get_item_labels(test_item) \
        == benchmark["labels"]

    print("get_item_descriptions")
    assert testobj.get_item_descriptions(test_item) \
        == benchmark["descriptions"]

    print("get_item_aliases")
    assert testobj.get_item_aliases(test_item) \
        == benchmark["aliases"]

    print("get_item_sitelinks")
    assert testobj.get_item_sitelinks(test_item) \
        == benchmark["sitelinks"]

    print("get_item_statements")
    assert testobj.get_item_statements(test_item) \
        == benchmark["statements"]

    print("get_item_label")
    assert testobj.get_item_label(test_item, language_code) \
        == benchmark["labels"].get(language_code)

    print("get_item_description")
    assert testobj.get_item_description(test_item, language_code) \
        == benchmark["descriptions"].get(language_code)

    print("get_item_aliases_in_language")
    assert testobj.get_item_aliases_in_language(test_item, other_language_code) \
        == benchmark["aliases"].get(other_language_code)

    print("get_item_sitelink")
    assert testobj.get_item_sitelink(test_item, site_code) \
        == benchmark["sitelinks"].get(site_code)

    print("get_item_statement")
    assert testobj.get_item_statement(test_item, test_item_statement) \
        == benchmark["statements"].get(test_item_statement_property)[0]

    print("get_property")
    assert testobj.get_property(test_property) \
        == benchmark_property

    print("get_property_labels")
    assert testobj.get_property_labels(test_property) \
        == benchmark_property["labels"]

    print("get_property_descriptions")
    assert testobj.get_property_descriptions(test_property) \
        == benchmark_property["descriptions"]

    print("get_property_aliases")
    assert testobj.get_property_aliases(test_property) \
        == benchmark_property["aliases"]

    print("get_property_statements")
    assert testobj.get_property_statements(test_property) \
        == benchmark_property["statements"]

    print("get_property_label")
    assert testobj.get_property_label(test_property, language_code) \
        == benchmark_property["labels"].get(language_code)

    print("get_property_description")
    assert testobj.get_property_description(test_property, language_code) \
        == benchmark_property["descriptions"].get(language_code)

    print("get_property_aliases_in_language")
    assert testobj.get_property_aliases_in_language(test_property, other_language_code) \
        == benchmark_property["aliases"].get(other_language_code)

    print("get_property_statement")
    assert testobj.get_property_statement(test_property, test_property_statement) \
        == benchmark_property["statements"].get(test_property_statement_property)[0]


def test_editing():
    testobj = WikibaseRestAPI(endpoint=test_endpoint, access_token=credentials.access_token)

    print("add_item")
    item_data = {
        "labels": {"en": make_up_string("l")},
        "descriptions": {"en": make_up_string("d")},
        "aliases": {"en": [make_up_string("a")]}
    }
    item_response = testobj.add_item(item_data)
    item_id = item_response["id"]

    print("add_item_statement")
    statement_data = {
        "rank": "normal",
        "property": { "id": "P95201" },
        "value": {
            "content": "Q41487",
            "type": "value"
        },
        "qualifiers": [],
        "references": []
    }
    statement_response = testobj.add_item_statement(item_id, statement_data)
    statement_id = statement_response["id"]

    print("update_item_labels")
    new_labels = {"en": make_up_string("l")}
    old_labels = item_data["labels"]
    testobj.update_item_labels(item_id, new_labels, old_labels)

    print("replace_item_statement")
    updated_statement_data = {
        "rank": "normal",
        "property": {
            "id": "P95201"
        },
        "value": {
            "content": "Q225467",
            "type": "value"
        },
        "qualifiers": [],
        "references": []
    }
    testobj.replace_item_statement(item_id, statement_id, updated_statement_data)

    print("update_statement")
    testobj.update_statement(statement_id, statement_data, updated_statement_data)

    print("update_item")
    updated_item_data = item_data
    updated_item_data["statements"] = [statement_data]
    testobj.update_item(item_id, updated_item_data, item_data)

    print("update_item_descriptions")
    new_description = {"en": make_up_string("d")}
    old_description = updated_item_data["descriptions"]
    testobj.update_item_descriptions(item_id, new_description, old_description)

    print("update_item_aliases")
    new_aliases = {"en": [make_up_string("a")]}
    old_aliases = updated_item_data["aliases"]
    testobj.update_item_aliases(item_id, new_aliases, old_aliases)

    #print("delete_statement")
    #testobj.delete_item_statement(item_id, statement_id)

    # delete_item
    #testobj.delete_item(item_id)

    property_id = "P98435"
    property_data = requests.get(test_endpoint + f"/entities/properties/{property_id}").json()

    #print("add_property_statement")
    #property_statement_response = testobj.add_property_statement(property_id, statement_data)
    #property_statement_id = property_statement_response["id"]

    #print("update_property_labels")
    #new_property_labels = {"en": make_up_string("l")}
    #old_property_labels = property_data["labels"]
    #testobj.update_property_labels(property_id, new_property_labels, old_property_labels)

    #print("replace_property_statement")
    #testobj.replace_property_statement(property_id, property_statement_id, updated_statement_data)

    #print("delete_property_statement")
    #testobj.delete_property_statement(property_id, property_statement_id)

    # delete_property
    #testobj.delete_property(property_id)

def run_tests():
    test_create_apisession()
    test_getters()
    test_editing()
    print("Tests complete.")

if __name__ == "__main__":
    run_tests()
