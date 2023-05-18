import requests

wikidata_endpoint = "https://www.wikidata.org/w/rest.php/wikibase/v0"
test_endpoint = "https://test.wikidata.org/w/rest.php/wikibase/v0"

class WikibaseRestAPI:
    def get_access_token(self):
        if self.access_token is not None:
            return self.access_token
        if self.api_key is None or self.api_secret is None:
            return None

        # Do the non-owner API rigamarole to get an access token from a key and
        # secret.

    def __init__(self, access_token=None, api_key=None, api_secret=None,
                 endpoint=wikidata_endpoint):
        self.api_key = api_key
        self.api_secret = api_secret
        self.endpoint = endpoint
        self.access_token = access_token
        if self.access_token is None:
            if self.api_key is not None and self.api_secret is not None:
                self.access_token = self.get_access_token()
        self.base_headers = {"Content-Type": "application/json"}
        if self.access_token is not None:
            self.base_headers["Authorization"] = f"Bearer {self.access_token}"

    def _request(self, verb, content, params={}, headers={}, data=None):
        for k, v in self.base_headers.items():
            headers[k] = v

        request = requests.request(verb, self.endpoint + content, params=params,
                      headers=headers, data=data)

        if request.status_code != 200:
            raise ResponseError

        try:
            return request.json()
        except:
            print(request.text)
            raise requests.exceptions.JSONDecodeError

    def _get(self, content, params={}):
        return self._request("GET", content, params=params)

    def _post(self, content, data):
        return self._request("POST", content, data=data)

    def _put(self, content, data):
        return self._request("PUT", content, data=data)

    def _patch(self, content):
        return self._request("PATCH", content, data=data)

    def _delete(self, content):
        return self._request("DELETE", content, data=data)

    # GET
    def get_item(self, item_id):
        return self._get(f"/entities/items/{item_id}")

    def get_item_labels(self, item_id):
        return self._get(f"/entities/items/{item_id}/labels")

    def get_item_descriptions(self, item_id):
        return self._get(f"/entities/items/{item_id}/descriptions")

    def get_item_aliases(self, item_id):
        return self._get(f"/entities/items/{item_id}/aliases")

    def get_item_statements(self, item_id):
        return self._get(f"/entities/items/{item_id}/statements")

    def get_statement(self, statement_id):
        return self._get(f"/entities/statements/{statement_id}")

    # POST
    def add_statement(self, item_id, data):
        return self._post("/entities/items/{item_id}/statements", data)

    # PUT
    def replace_statement(self, statement_id, data):
        return self._put(f"/statements/{statement_id}", data)

    # PATCH
    def update_statement(self, statement_id, data):
        return self._patch(f"/statements/{statement_id}", data)

    # DELETE
    def delete_statement(self, statement_id, data):
        return self._delete(f"/statements/{statement_id}", data)

# Tests

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
