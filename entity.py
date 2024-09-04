import json
import copy
from api import WikibaseRestAPI, wikidata_endpoint

class Base:
    def __init__(self):
        self.data = {}

    def to_dict(self):
        return self.data

class Connection:
    def __init__(self, endpoint=wikidata_endpoint, access_token=None, bot=False, edit_summary="Updating item data", tags=[]):
        self.endpoint = endpoint
        self.bot = bot
        self.edit_summary = edit_summary
        self.tags = []
        self.api = WikibaseRestAPI(access_token=access_token, endpoint=self.endpoint)

    def add_edit_tag(self, content):
        self.tags.append(content)

    def remove_edit_tag(self, content):
        if content in self.tags:
            self.tags.remove(content)

    def set_edit_summary(self, content):
        self.edit_summary = content

    def append_to_edit_summary(self, content):
        self.edit_summary = f"{self.edit_summary} {content}"

class Snak(Base):
    def __init__(self, property_id=None, data_type=None, value_type="value", value_content=None):
        self.data = {
            "property": {
                "id": property_id,
                "data_type": data_type},
            "value": {
                "type": value_type}
            }

        if value_type not in ["somevalue", "novalue"]:
            self.data["value"]["content"] = value_content

    def get_property_id(self):
        return self.data["property"]["id"]

    def get_property_type(self):
        return self.data["property"]["data_type"]

    def get_value(self):
        return self.data["value"]

    def set_property(self, property_id, data_type):
        self.data["property"] = {
            "id": property_id,
            "data_type": data_type
        }

    def set_value(self, content):
        self.data["value"]["type"] = "value"
        self.data["value"]["content"] = content

    def set_no_value(self):
        self.data["value"] = {"type": "novalue"}

    def set_unknown_value(self):
        self.data["value"] = {"type": "somevalue"}

    def set_property_and_value(self, property_id, data_type, content):
        self.data = {
            "property": {
                "id": property_id,
                "data_type": data_type
            },
            "value": {
                "type": "value",
                "content": content
            }
        }

    def set_wikibase_item_value(self, property_id, content):
        self.set_property_and_value(property_id, "wikibase-item", content)

    def set_string_value(self, property_id, content):
        self.set_property_and_value(property_id, "string", content)

    def set_monolingual_text_value(self, property_id, language, text):
        self.set_property_and_value(property_id, "monolingualtext",
            {"text": text, "language": language})

    def set_external_id_value(self, property_id, content):
        self.set_property_and_value(property_id, "external-id", content)

    def set_url_value(self, property_id, content):
        self.set_property_and_value(property_id, "url", content)

    def set_quantity_value(self, property_id, amount, unit):
        if amount > 0:
            amount = "+" + str(amount)
        else:
            amount = str(amount)
        self.set_property_and_value(property_id, "quantity",
            {"amount": amount, "unit": unit})

    def set_commons_media_value(self, property_id, content):
        self.set_property_and_value(property_id, "commonsMedia", content)

    def set_time_value(self, property_id, time, precision, calendarmodel="Q1985727"):
        self.set_property_and_value(property_id, "time",
            {"time": time + "T00:00:00Z",
             "precision": precision,
             "calendarmodel": f"http://www.wikidata.org/entity/{calendarmodel}"})

class Sitelink(Base):
    def __init__(self, site_code=None, title=None, url=None, badges=[]):
        self.site_code = site_code
        self.data = {
            "title": title,
            "url": url,
            "badges": badges
        }

    def get_site_code(self):
        return self.site_code

    def get_title(self):
        return self.data["title"]

    def get_url(self):
        return self.data["url"]

    def get_badges(self):
        return self.data["badges"]

    def set_site_code(self, content):
        self.site_code = content

    def set_title(self, content):
        self.data["title"] = content

    def set_url(self, content):
        self.data["url"] = content

    def add_badge(self, content):
        self.data["badges"].append(content)

    def remove_badge(self, content):
        if content in self.data["badges"]:
            self.data["badges"].remove(content)

class Reference(Base):
    def __init__(self, ref_hash=None):
        self.data = {
            "hash": ref_hash,
            "parts": []
        }

    def to_dict(self):
        return {
            "hash": self.data["hash"],
            "parts": [part.to_dict() for part in self.data["parts"]]
        }

    def get_hash(self):
        return self.data["hash"]

    def set_hash(self, ref_hash):
        self.data["hash"] = ref_hash

    def add_part(self, part):
        if isinstance(part, Snak):
            self.data["parts"].append(part.data)
        else:
            raise ValueError("Reference part must be a Snak")

    def remove_part(self, part):
        if part.data in self.data["parts"]:
            self.data["parts"].remove(part.data)

class Statement(Snak):
    def __init__(self, statement_id=None, rank="normal", property_id=None,
        data_type=None, value_type="value", value_content=None):
        super().__init__(
            property_id=property_id,
            data_type=data_type,
            value_type=value_type,
            value_content=value_content)
        self.data["id"] = statement_id
        self.data["rank"] = rank
        self.data["qualifiers"] = []
        self.data["references"] = []

    def to_dict(self):
        r = {
            "id": self.data["id"],
            "rank": self.data["rank"],
            "property": self.data["property"],
            "value": self.data["value"],
        }
        if "qualifiers" in self.data:
            r["qualifiers"] = [qualifier.to_dict() for qualifier in self.data["qualifiers"]]
        if "references" in self.data:
            r["references"] = [reference.to_dict() for reference in self.data["references"]]

    def get_id(self):
        return self.data["id"]

    def get_rank(self):
        return self.data["rank"]

    def get_qualifiers(self):
        return self.data["qualifiers"]

    def get_references(self):
        return self.data["references"]

    def set_id(self, content):
        self.data["id"] = content

    def set_rank(self, content):
        if content in ["deprecated", "normal", "preferred"]:
            self.data["rank"] = content
        else:
            raise ValueError("Rank must be deprecated, normal, or preferred")

    def add_qualifier(self, qualifier):
        if isinstance(qualifier, Snak):
            self.data["qualifiers"].append(qualifier.data)
        else:
            raise ValueError("Qualifier must be a Snak")

    def remove_qualifier(self, qualifier):
        if qualifier.data in self.data["qualifiers"]:
            self.data["qualifiers"].remove(qualifier.data)

    def add_reference(self, reference):
        if isinstance(reference, Reference):
            self.data["references"].append(reference.data)
        else:
            raise ValueError("Reference must be a Reference-type object")

    def remove_reference(self, reference):
        if reference.data in self.data["references"]:
            self.data["references"].remove(reference.data)


class Entity(Base):
    def __init__(self, connection=None, entity_id=None, entity_type="items"):
        self.data = {
            "id": entity_id,
            "type": entity_type,
            "labels": {},
            "descriptions": {},
            "aliases": {},
            "statements": {},
            "sitelinks": {}
        }
        if isinstance(connection, Connection):
            self.connection = connection
        else:
            raise ValueError("connection must be a Connection-type object")
        self.original_data = None
        if entity_id is not None and connection is not None:
            self.load()

    def load(self):
        if self.connection is None:
            raise Exception("No Wikibase connection defined.")
        self.data = self.connection.api.get_entity(self.data["type"], self.data["id"])
        self.original_data = copy.deepcopy(self.data)

    def to_dict(self):
        statements = {}
        for property_id, statements_list in self.data["statements"].items():
            expanded_statements_list = []
            for statement in statements_list:
                to_append = {}
                if "id" in statement:
                    to_append["id"] = statement["id"]
                if "rank" in statement:
                    to_append["rank"] = statement["rank"]
                if "property" in statement:
                    to_append["property"] = statement["property"]
                if "value" in statement:
                    to_append["value"] = statement["value"]
                if "qualifiers" in statement:
                    to_append["qualifiers"] = [qualifier.to_dict() for qualifier in statement["qualifiers"]]
                if "references" in statement:
                    to_append["references"] = [reference.to_dict() for reference in statement["references"]]
                expanded_statements_list.append(to_append)
            statements[property_id] = expanded_statements_list
        return {
            "id": self.data["id"],
            "type": self.data["type"],
            "labels": self.data["labels"],
            "descriptions": self.data["descriptions"],
            "aliases": self.data["aliases"],
            "statements": statements,
            "sitelinks": self.data["sitelinks"]
        }

    def submit(self):
        if self.connection is None:
            raise Exception("No Wikibase connection defined.")
        # Don't submit anything if no changes have been made
        if self.data == self.original_data:
            return
        print(json.dumps(self.data))
        if self.original_data is None:
            if self.data["type"] != "items":
                raise RuntimeException("Creation of non-item entities not supported.")
            # Submit new item (only items supported)
            return self.connection.api.add_item(
                       self.data,
                       bot=self.connection.bot,
                       edit_summary=self.connection.edit_summary,
                       tags=self.connection.tags)
        else:
            plural = {"item": "items", "property": "properties"}
            # Update existing entities
            return self.connection.api.update_entity(
                       plural[self.data["type"]],
                       self.data["id"],
                       self.data,
                       self.original_data,
                       bot=self.connection.bot,
                       edit_summary=self.connection.edit_summary,
                       tags=self.connection.tags)

    def get_id(self):
        return self.data["id"]

    def get_entity_type(self):
        return self.data["type"]

    def get_labels(self):
        return self.data["labels"]

    def get_label(self, language_code):
        return self.data["labels"].get(language_code)

    def get_descriptions(self):
        return self.data["descriptions"]

    def get_description(self, language_code):
        return self.data["descriptions"].get(language_code)

    def get_aliases(self, language_code=None):
        if language_code is None:
            return self.data["aliases"]
        return self.data["aliases"].get(language_code)

    def get_statements(self, property_id=None):
        if property_id is None:
            return self.data["statements"]
        return self.data["statements"].get(property_id)

    def get_sitelinks(self):
        return self.data["sitelinks"]

    def get_sitelink(self, site_code):
        return self.data["sitelinks"].get(site_code)

    def set_label(self, language_code, content):
        self.data["labels"][language_code] = content

    def set_description(self, language_code, content):
        self.data["descriptions"][language_code] = content

    def add_alias(self, language_code, content):
        if language_code not in self.data["aliases"]:
            self.data["aliases"][language_code] = []
        self.data["aliases"][language_code].append(content)

    def remove_alias(self, language_code, content):
        if language_code in self.data["aliases"] and content in self.data["aliases"][language_code]:
            self.data["aliases"][language_code].remove(content)

    def add_statement(self, content):
        if isinstance(content, Statement):
            if content.data["property"]["id"] not in self.data["statements"]:
                self.data["statements"][content.data["property"]["id"]] = []
            self.data["statements"][content.data["property"]["id"]].append(content.data)
        else:
            raise ValueError("Statement must be a Statement-type object")

    def remove_statement(self, content):
        if content in self.data["statements"]:
            self.data["statements"].remove(content)

    def add_sitelink(self, content):
        if isinstance(content, Sitelink):
            self.data["sitelinks"][content.site_code] = content.data
        else:
            raise ValueError("Sitelink must be a Sitelink-type object")

    def remove_sitelink(self, content):
        if content in self.data["sitelinks"]:
            self.data["sitelinks"].remove(content)
