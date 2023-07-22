import requests
import json
import jsonpatch

wikidata_endpoint = "https://www.wikidata.org/w/rest.php/wikibase/v0"

def _prepare_payload(verb, part, new_data, old_data, bot, edit_summary, tags=[]):
    payload = {
        "tags": ["wikibase-patcher-v1"],
        "bot": bot,
    }

    for tag in tags:
        payload["tags"].append(tag)

    if edit_summary is not None:
        payload["comment"] = edit_summary

    if verb.lower() == "patch" and old_data is not None:
        payload["patch"] = list(jsonpatch.make_patch(old_data, new_data))
    elif verb.lower() != "delete":
        payload[part] = new_data

    print(payload)
    return payload

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


    def _request(self, verb, path, params={}, headers={}, payload=None):
        for k, v in self.base_headers.items():
            headers[k] = v

        if verb.lower() == "patch":
            headers["Content-Type"] = "application/json-patch+json"

        request = requests.request(
                      verb,
                      self.endpoint + path,
                      params=params,
                      headers=headers,
                      data=json.dumps(payload))


        if request.status_code > 299:
            print(request.text)
            raise Exception

        try:
            return request.json()
        except:
            print(request.text)
            raise requests.exceptions.JSONDecodeError


    def _get(self, path, params={}):
        return self._request("get", path, params=params)

    def _post(self, path, payload):
        return self._request("post", path, payload=payload)

    def _put(self, path, payload):
        return self._request("put", path, payload=payload)

    def _patch(self, path, payload):
        return self._request("patch", path, payload=payload)

    def _delete(self, path, data):
        return self._request("delete", path, payload=payload)


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


    # PATCH
    def update_statement(self, statement_id, data, old_data, bot=False, edit_summary=None, tags=[]):
        payload = _prepare_payload("patch", "statement", data, old_data, bot, edit_summary, tags)
        return self._patch(f"/statements/{statement_id}", payload)


    # POST
    def add_statement(self, item_id, data, bot=False, edit_summary=None, tags=[]):
        payload = _prepare_payload("post", "statement", data, None, bot, edit_summary, tags)
        return self._post(f"/entities/items/{item_id}/statements", payload)


    # PUT
    def replace_statement(self, statement_id, data, bot=False, edit_summary=None, tags=[]):
        payload = _prepare_payload("put", "statement", data, None, bot, edit_summary, tags)
        return self._put(f"/statements/{statement_id}", payload)


    # DELETE
    def delete_statement(self, statement_id, data, bot=False, edit_summary=None, tags=[]):
        payload = _prepare_payload("delete", "statement", data, None, bot, edit_summary, tags)
        return self._delete(f"/statements/{statement_id}", payload)
