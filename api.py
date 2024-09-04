import json
import jsonpatch
import requests
import time

wikidata_endpoint = "https://www.wikidata.org/w/rest.php/wikibase/v0"

singular = {
    # English can't do plural inflections consistently. That would be too nice.
    "items": "item",
    "properties": "property"
}

def _prepare_payload(verb, part, new_data, old_data, bot, edit_summary, tags=[]):
    for tag in tags:
        payload["tags"].append(tag)
    if edit_summary is not None:
        payload["comment"] = edit_summary
    if verb.lower() == "patch" and old_data is not None:
        payload["patch"] = list(jsonpatch.make_patch(old_data, new_data))
    elif verb.lower() != "delete":
        payload[part] = new_data
    return payload

class WikibaseRestAPI:
    def get_access_token(self):
        if self.access_token is not None:
            return self.access_token
        if self.api_key is None or self.api_secret is None:
            return None

        return Exception("get_access_token is not implemented. You will need to"
            "provide an access token directly in the meantime.")

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

    def _request(self, verb, path, params={}, headers={}, payload=None,
        max_retries=10, base_delay=1, max_delay=60):
        for retry in range(max_retries):
            try:
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
                #print(f"{verb.upper()} {path}")
                if request.status_code == 409:
                    print(f"Conflict; skipping – {request.text}")
                    return request.json()
                elif request.status_code > 299:
                    print(request.text)
                    raise Exception("HTTP Error with status code: {}"\
                        .format(request.status_code))
                return request.json()
            except (Exception, requests.exceptions.RequestException,
                requests.exceptions.JSONDecodeError) as e:
                if retry < max_retries - 1:
                    delay = min(base_delay * (2 ** retry), max_delay)
                    print(f"Error encountered: {str(e)}. "
                          f"Retrying {retry + 2}/{max_retries} in {delay} seconds...")
                    time.sleep(delay)
                    continue
                else:  # if it's the last retry, raise the error
                    print(f"Error encountered: {str(e)}. All retries exhausted!")
                    raise Exception(f"All retries exhausted after {max_retries}"
                                    f" attempts. Last error encountered: {str(e)}")

    def _get(self, path, params={}):
        return self._request("get", path, params=params)

    def _post(self, path, part, data, bot, edit_summary, tags):
        return self._request("post", path, payload=_prepare_payload(
            "post", part, data, None, bot, edit_summary, tags))

    def _put(self, path, part, data, bot, edit_summary, tags):
        return self._request("put", path, payload=_prepare_payload(
            "put", part, data, None, bot, edit_summary, tags))

    def _patch(self, path, data, old_data, bot, edit_summary, tags):
        return self._request("patch", path, payload=_prepare_payload(
            "patch", None, data, old_data, bot, edit_summary, tags))

    def _delete(self, path, bot, edit_summary, tags):
        return self._request("delete", path, payload=_prepare_payload(
            "delete", None, None, None, bot, edit_summary, tags))


    # GET
    def get_entity(self, entity_type, entity_id):
        return self._get(f"/entities/{entity_type}/{entity_id}")

    def get_entity_labels(self, entity_type, entity_id):
        return self._get(f"/entities/{entity_type}/{entity_id}/labels")

    def get_entity_label(self, entity_type, entity_id, language_code):
        return self._get(f"/entities/{entity_type}/{entity_id}/labels/{language_code}")

    def get_entity_descriptions(self, entity_type, entity_id):
        return self._get(f"/entities/{entity_type}/{entity_id}/descriptions")

    def get_entity_description(self, entity_type, entity_id, language_code):
        return self._get(f"/entities/{entity_type}/{entity_id}/descriptions/{language_code}")

    def get_entity_aliases(self, entity_type, entity_id):
        return self._get(f"/entities/{entity_type}/{entity_id}/aliases")

    def get_entity_aliases_in_language(self, entity_type, entity_id, language_code):
        return self._get(f"/entities/{entity_type}/{entity_id}/aliases/{language_code}")

    def get_entity_statements(self, entity_type, entity_id):
        return self._get(f"/entities/{entity_type}/{entity_id}/statements")

    def get_entity_statement(self, entity_type, entity_id, statement_id):
        return self._get(f"/entities/{entity_type}/{entity_id}/statements/{statement_id}")

    def get_item_sitelinks(self, item_id):
        return self._get(f"/entities/items/{item_id}/sitelinks")

    def get_item_sitelink(self, item_id, site_id):
        return self._get(f"/entities/items/{item_id}/sitelinks/{site_id}")


    # PATCH
    def update_statement(self, statement_id, data, old_data,
        bot=False,edit_summary=None, tags=[]):
        return self._patch(f"/statements/{statement_id}",
            data, old_data, bot, edit_summary, tags)

    def update_entity(self, entity_type, entity_id, data, old_data,
        bot=False, edit_summary=None, tags=[]):
        return self._patch(f"/entities/{entity_type}/{entity_id}",
            data, old_data, bot, edit_summary, tags)

    def update_entity_labels(self, entity_type, entity_id, data, old_data,
        bot=False, edit_summary=None, tags=[]):
        return self._patch(f"/entities/{entity_type}/{entity_id}/labels",
            data, old_data, bot, edit_summary, tags)

    def update_entity_descriptions(self, entity_type, entity_id, data, old_data,
        bot=False, edit_summary=None, tags=[]):
        return self._patch(f"/entities/{entity_type}/{entity_id}/descriptions",
            data, old_data, bot, edit_summary, tags)

    def update_entity_aliases(self, entity_type, entity_id, data, old_data,
        bot=False, edit_summary=None, tags=[]):
        return self._patch(f"/entities/{entity_type}/{entity_id}/aliases",
            data, old_data, bot, edit_summary, tags)

    def update_entity_statement(self, entity_type, entity_id, statement_id, data, old_data,
        bot=False, edit_summary=None, tags=[]):
        return self._patch(f"/entities/{entity_type}/{entity_id}/statements/{statement_id}",
            data, old_data, bot, edit_summary, tags)


    # POST
    def add_item(self, data, bot=False, edit_summary=None, tags=[]):
        return self._post(f"/entities/items",
            "item", data, bot, edit_summary, tags)

    def add_entity_label(self, entity_type, entity_id, data,
        bot=False, edit_summary=None, tags=[]):
        return self._post(f"/entities/{entity_type}/{entity_id}/labels",
            "label", data, bot, edit_summary, tags)

    def add_entity_description(self, entity_type, entity_id, data,
        bot=False, edit_summary=None, tags=[]):
        return self._post(f"/entities/{entity_type}/{entity_id}/descriptions",
            "description", data, bot, edit_summary, tags)

    def add_entity_aliases(self, entity_type, entity_id, data,
        bot=False, edit_summary=None, tags=[]):
        return self._post(f"/entities/{entity_type}/{entity_id}/aliases",
            "aliases", data, bot, edit_summary, tags)

    def add_entity_statement(self, entity_type, entity_id, data,
        bot=False, edit_summary=None, tags=[]):
        return self._post(f"/entities/{entity_type}/{entity_id}/statements",
            "statement", data, bot, edit_summary, tags)


    # PUT
    def replace_statement(self, statement_id, data,
        bot=False, edit_summary=None, tags=[]):
        return self._put(f"/statements/{statement_id}",
            "statement", data, bot, edit_summary, tags)

    def replace_entity_label(self, entity_type, entity_id, language_code, data,
        bot=False, edit_summary=None, tags=[]):
        return self._put(f"/entities/{entity_type}/{entity_id}/labels/{language_code}",
            "label", data, bot, edit_summary, tags)

    def replace_entity_description(self, entity_type, entity_id, language_code, data,
        bot=False, edit_summary=None, tags=[]):
        return self._put(f"/entities/{entity_type}/{entity_id}/descriptions/{language_code}",
            "description", data, bot, edit_summary, tags)

    def replace_entity_aliases(self, entity_type, entity_id, language_code, data,
        bot=False, edit_summary=None, tags=[]):
        return self._put(f"/entities/{entity_type}/{entity_id}/aliases/{language_code}",
            "aliases", data, bot, edit_summary, tags)

    def replace_entity_statement(self, entity_type, entity_id, statement_id, data,
        bot=False, edit_summary=None, tags=[]):
        return self._put(f"/entities/{entity_type}/{entity_id}/statements/{statement_id}",
            "statement", data, bot, edit_summary, tags)


    # DELETE
    def delete_statement(self, statement_id,
        bot=False, edit_summary=None, tags=[]):
        return self._delete(f"/statements/{statement_id}",
            bot, edit_summary, tags)

    def delete_entity(self, entity_type, entity_id,
        bot=False, edit_summary=None, tags=[]):
        return self._delete(f"/entities/{entity_type}/{entity_id}",
            bot, edit_summary, tags)

    def delete_entity_label(self, entity_type, entity_id, language_code,
        bot=False, edit_summary=None, tags=[]):
        return self._delete(f"/entities/{entity_type}/{entity_id}/labels/{language_code}",
            bot, edit_summary, tags)

    def delete_entity_description(self, entity_type, entity_id, language_code,
        bot=False, edit_summary=None, tags=[]):
        return self._delete(f"/entities/{entity_type}/{entity_id}/descriptions/{language_code}",
            bot, edit_summary, tags)

    def delete_entity_aliases(self, entity_type, entity_id, language_code,
        bot=False, edit_summary=None, tags=[]):
        return self._delete(f"/entities/{entity_type}/{entity_id}/aliases/{language_code}",
            bot, edit_summary, tags)

    def delete_entity_statement(self, entity_type, entity_id, statement_id,
        bot=False, edit_summary=None, tags=[]):
        return self._delete(f"/entities/{entity_type}/{entity_id}/statements/{statement_id}",
            bot, edit_summary, tags)


    # Convenience functions
    def get_item(self, item_id):
        return self.get_entity("items", item_id)

    def get_property(self, property_id):
        return self.get_entity("properties", property_id)

    def get_item_labels(self, item_id):
        return self.get_entity_labels("items", item_id)

    def get_property_labels(self, property_id):
        return self.get_entity_labels("properties", property_id)

    def get_item_label(self, item_id, language_code):
        return self.get_entity_label("items", item_id, language_code)

    def get_property_label(self, property_id, language_code):
        return self.get_entity_label("properties", property_id, language_code)

    def get_item_descriptions(self, item_id):
        return self.get_entity_descriptions("items", item_id)

    def get_property_descriptions(self, property_id):
        return self.get_entity_descriptions("properties", property_id)

    def get_item_description(self, item_id, language_code):
        return self.get_entity_description("items", item_id, language_code)

    def get_property_description(self, property_id, language_code):
        return self.get_entity_description("properties", property_id, language_code)

    def get_item_aliases(self, item_id):
        return self.get_entity_aliases("items", item_id)

    def get_property_aliases(self, property_id):
        return self.get_entity_aliases("properties", property_id)

    def get_item_aliases_in_language(self, item_id, language_code):
        return self.get_entity_aliases_in_language("items", item_id, language_code)

    def get_property_aliases_in_language(self, property_id, language_code):
        return self.get_entity_aliases_in_language("properties", property_id, language_code)

    def get_item_statements(self, item_id):
        return self.get_entity_statements("items", item_id)

    def get_property_statements(self, property_id):
        return self.get_entity_statements("properties", property_id)

    def get_item_statement(self, item_id, statement_id):
        return self.get_entity_statement("items", item_id, statement_id)

    def get_property_statement(self, property_id, statement_id):
        return self.get_entity_statement("properties", property_id, statement_id)

    def update_item(self, item_id, data, old_data, bot=False, edit_summary=None, tags=[]):
        return self.update_entity("items", item_id, data, old_data, bot, edit_summary, tags)

    def update_property(self, property_id, data, old_data, bot=False, edit_summary=None, tags=[]):
        return self.update_entity("properties", property_id, data, old_data, bot, edit_summary, tags)

    def update_item_labels(self, item_id, data, old_data, bot=False, edit_summary=None, tags=[]):
        return self.update_entity_labels("items", item_id, data, old_data, bot, edit_summary, tags)

    def update_property_labels(self, property_id, data, old_data, bot=False, edit_summary=None, tags=[]):
        return self.update_entity_labels("properties", property_id, data, old_data, bot, edit_summary, tags)

    def update_item_descriptions(self, item_id, data, old_data, bot=False, edit_summary=None, tags=[]):
        return self.update_entity_descriptions("items", item_id, data, old_data, bot, edit_summary, tags)

    def update_property_descriptions(self, property_id, data, old_data, bot=False, edit_summary=None, tags=[]):
        return self.update_entity_descriptions("properties", item_id, data, old_data, bot, edit_summary, tags)

    def update_item_aliases(self, item_id, data, old_data, bot=False, edit_summary=None, tags=[]):
        return self.update_entity_aliases("items", item_id, data, old_data, bot, edit_summary, tags)

    def update_property_aliases(self, property_id, data, old_data, bot=False, edit_summary=None, tags=[]):
        return self.update_entity_aliases("properties", property_id, data, old_data, bot, edit_summary, tags)

    def update_item_statement(self, item_id, statement_id, data, old_data, bot=False, edit_summary=None, tags=[]):
        return self.update_entity_statement("items", item_id, statement_id, data, old_data, bot, edit_summary, tags)

    def update_property_statement(self, property_id, statement_id, data, old_data, bot=False, edit_summary=None, tags=[]):
        return self.update_entity_statement("properties", property_id, statement_id, data, old_data, bot, edit_summary, tags)

    def add_item_label(self, item_id, data, bot=False, edit_summary=None, tags=[]):
        return self.add_entity_label("items", item_id, data, bot, edit_summary, tags)

    def add_property_label(self, property_id, data, bot=False, edit_summary=None, tags=[]):
        return self.add_entity_label("properties", item_id, data, bot, edit_summary, tags)

    def add_item_description(self, item_id, data, bot=False, edit_summary=None, tags=[]):
        return self.add_entity_description("items", item_id, data, bot, edit_summary, tags)

    def add_property_description(self, property_id, data, bot=False, edit_summary=None, tags=[]):
        return self.add_entity_description("properties", property_id, data, bot, edit_summary, tags)

    def add_item_aliases(self, item_id, data, bot=False, edit_summary=None, tags=[]):
        return self.add_entity_aliases("items", item_id, data, bot, edit_summary, tags)

    def add_property_aliases(self, property_id, data, bot=False, edit_summary=None, tags=[]):
        return self.add_entity_aliases("properties", property_id, data, bot, edit_summary, tags)

    def add_item_statement(self, item_id, data, bot=False, edit_summary=None, tags=[]):
        return self.add_entity_statement("items", item_id, data, bot, edit_summary, tags)

    def add_property_statement(self, property_id, data, bot=False, edit_summary=None, tags=[]):
        return self.add_entity_statement("properties", property_id, data, bot, edit_summary, tags)

    def replace_item_label(self, item_id, language_code, data, bot=False, edit_summary=None, tags=[]):
        return self.replace_entity_label("items", item_id, language_code, data, bot, edit_summary, tags)

    def replace_property_label(self, property_id, language_code, data, bot=False, edit_summary=None, tags=[]):
        return self.replace_entity_label("properties", property_id, language_code, data, bot, edit_summary, tags)

    def replace_item_description(self, item_id, language_code, data, bot=False, edit_summary=None, tags=[]):
        return self.replace_entity_description("items", item_id, language_code, data, bot, edit_summary, tags)

    def replace_property_description(self, property_id, language_code, data, bot=False, edit_summary=None, tags=[]):
        return self.replace_entity_description("properties", property_id, language_code, data, bot, edit_summary, tags)

    def replace_item_aliases(self, item_id, language_code, data, bot=False, edit_summary=None, tags=[]):
        return self.replace_entity_aliases("items", item_id, language_code, data, bot, edit_summary, tags)

    def replace_property_aliases(self, property_id, language_code, data, bot=False, edit_summary=None, tags=[]):
        return self.replace_entity_aliases("properties", property_id, language_code, data, bot, edit_summary, tags)

    def replace_item_statement(self, item_id, statement_id, data, bot=False, edit_summary=None, tags=[]):
        return self.replace_entity_statement("items", item_id, statement_id, data, bot, edit_summary, tags)

    def replace_property_statement(self, property_id, statement_id, data, bot=False, edit_summary=None, tags=[]):
        return self.replace_entity_statement("properties", property_id, statement_id, data, bot, edit_summary, tags)

    def delete_item(self, item_id, bot=False, edit_summary=None, tags=[]):
        return self.delete_entity("items", item_id, bot, edit_summary, tags)

    def delete_property(self, property_id, bot=False, edit_summary=None, tags=[]):
        return self.delete_entity("properties", property_id, bot, edit_summary, tags)

    def delete_item_label(self, item_id, language_code, bot=False, edit_summary=None, tags=[]):
        return self.delete_entity_label("items", item_id, language_code, bot, edit_summary, tags)

    def delete_property_label(self, property_id, language_code, bot=False, edit_summary=None, tags=[]):
        return self.delete_entity_label("properties", property_id, language_code, bot, edit_summary, tags)

    def delete_item_description(self, item_id, language_code, bot=False, edit_summary=None, tags=[]):
        return self.delete_entity_description("items", item_id, language_code, bot, edit_summary, tags)

    def delete_property_description(self, property_id, language_code, bot=False, edit_summary=None, tags=[]):
        return self.delete_entity_description("properties", property_id, language_code, bot, edit_summary, tags)

    def delete_item_statement(self, item_id, statement_id, bot=False, edit_summary=None, tags=[]):
        return self.delete_entity_statement("items", item_id, statement_id, bot, edit_summary, tags)

    def delete_property_statement(self, property_id, statement_id, bot=False, edit_summary=None, tags=[]):
        return self.delete_entity_statement("properties", property_id, statement_id, bot, edit_summary, tags)

    def delete_item_aliases(self, item_id, language_code, bot=False, edit_summary=None, tags=[]):
        return self.delete_entity_aliases("items", item_id, language_code, bot, edit_summary, tags)

    def delete_property_aliases(self, property_id, language_code, bot=False, edit_summary=None, tags=[]):
        return self.delete_entity_aliases("properties", property_id, language_code, bot, edit_summary, tags)
