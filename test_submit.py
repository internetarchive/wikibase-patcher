from entity import *
from test_api import make_up_string
import requests
import credentials
import random

connection = Connection(endpoint="https://test.wikidata.org/w/rest.php/wikibase/v0", access_token=credentials.access_token)

def make_up_badge():
    badges = ["Q609", "Q608", "Q226102", "Q226103"]
    n = random.randint(0, 2**32 - 1) % 3
    return badges[n]

def make_up_item():
    url = "https://test.wikidata.org/w/api.php"
    params = {
        "action": "query",
        "list": "random",
        "rnnamespace": 0,
        "rnlimit": 1,
        "rnfilterredir": "nonredirects",
        "format": "json"
    }
    response = requests.get(url, params=params)
    data = response.json()
    qitem = data["query"]["random"][0]["title"]
    return str(qitem)

def make_up_sitelink(domain="en.wikipedia.org", namespace=0):
    url = "https://" + domain + "/w/api.php"
    params = {
        "action": "query",
        "list": "random",
        "rnnamespace": namespace,
        "rnlimit": 1,
        "format": "json"
    }
    response = requests.get(url, params=params)
    data = response.json()
    article_title = data['query']['random'][0]['title']
    article_link = f"https://{domain}/wiki/{article_title.replace(' ', '_')}"
    return article_title, article_link

def make_up_commons_file():
    article_title, _ = make_up_sitelink(domain="commons.wikimedia.org", namespace=6)
    article_title = article_title.replace("File:", "")
    return article_title

def make_up_time():
    year = str(random.randint(1800, 2020))
    month = str(random.randint(1, 13)).zfill(2)
    day = str(random.randint(1, 29)).zfill(2)
    return f"+{year}-{month}-{day}"

def generate_random_test_entity(entity_id=None):
    entity = Entity(connection=connection, entity_id=entity_id)
    entity.set_label("en", make_up_string("l"))
    entity.set_description("en", make_up_string("d"))
    entity.add_alias("en", make_up_string("a"))

    article_title, article_link = make_up_sitelink()
    if entity_id is None:
        # Apparently the REST API can't be used to modify existing sitelinks
        # So I am dropping that as a test case for the existing item.
        sitelink = Sitelink(site_code="enwiki", title=article_title, url=article_link)
        sitelink.add_badge(make_up_badge())
        entity.add_sitelink(sitelink)

    statement = Statement(
        property_id="P95201",
        data_type="wikibase-item",
        value_content=make_up_item()
    )

    qualifier = Snak(property_id="P664", data_type="string", value_content=make_up_string("q"))
    statement.add_qualifier(qualifier)

    reference = Reference()
    ref_part = Snak(property_id="P43659", data_type="url", value_content=f"https://{make_up_string('X')}.com")
    reference.add_part(ref_part)
    statement.add_reference(reference)

    entity.add_statement(statement)

    # Testing other data types
    st = Statement()
    st.set_string_value("P664", make_up_string("s"))
    entity.add_statement(st)

    st = Statement()
    st.set_monolingual_text_value("P98445", "en", make_up_string("m"))
    entity.add_statement(st)

    st = Statement()
    st.set_external_id_value("P98444", make_up_string("i"))
    entity.add_statement(st)

    st = Statement()
    st.set_url_value("P7711", f"https://{make_up_string('R')}.org")
    entity.add_statement(st)

    st = Statement()
    st.set_quantity_value("P543", random.randint(0, 1000), "http://test.wikidata.org/entity/" + make_up_item())
    entity.add_statement(st)

    st = Statement()
    st.set_commons_media_value("P98443", make_up_commons_file())
    entity.add_statement(st)

    st = Statement()
    st.set_time_value("P66", make_up_time(), 11)
    entity.add_statement(st)

    return entity


if __name__ == "__main__":
    new_item = generate_random_test_entity()
    new_item.submit()

    existing_item = generate_random_test_entity(entity_id="Q235642")
    existing_item.submit()
