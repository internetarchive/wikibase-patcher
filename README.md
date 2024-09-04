# wikibase-patcher

Python functions for interacting with a Wikibase REST API and corresponding Python object classes.

Note that for whatever reason, tests when editing properties have failed, so for now this is useful only for editing items.

## Setup

1. `git clone https://github.com/internetarchive/wikibase-patcher wikibasepatcher`

2. `cd wikibasepatcher`

3. `python3 -m venv venv`

4. `pip3 install -r requirements.txt`

5. `cp credentials.py.example credentials.py`

5. Generate an OAuth2 token for your batch-editing account.

6. Update `credentials.py` with the access token generated above.

## Usage

This example uses Test Wikidata, its REST API endpoint, and its properties and items.

### Connecting to a Wikibase

To interact with a Wikibase instance, you first need to establish a connection using the `Connection` class. This connection will handle the API requests and manage authentication.

```python
from entity import Connection
from credentials import access_token

connection = Connection(
    # Replace with your Wikibase REST API endpoint
    endpoint="https://test.wikidata.org/w/rest.php/wikibase/v0",
    # Required for authenticated (edit) operations
    access_token=access_token,
    # Set as True to edit with bot flag
    bot=True,
    # Optional: default edit summary
    edit_summary="Updating item data",
    # Optional: tags to categorize edits (must be valid edit tags)
    tags=["tag1", "tag2"]
)
```

### Instantiating an Entity

Once the connection is established, you can instantiate an `Entity` object using an existing entity ID. This allows you to retrieve and manipulate the entity's data.

```python
from entity import Entity

entity_id = "Q42"  # Replace with your entity ID
entity = Entity(connection=connection, entity_id=entity_id)

# Retrieve data from the Entity
entity.load()
```

### Retrieving Data from an Entity

After loading an entity, you can access its various properties such as labels, descriptions, aliases, statements, and sitelinks.

```python
# Get the entity ID
print(entity.get_id())

# Get labels
print(entity.get_labels())

# Get descriptions
print(entity.get_descriptions())

# Get aliases
print(entity.get_aliases())

# Get statements
print(entity.get_statements())

# Get sitelinks
print(entity.get_sitelinks())
```

### Updating and Setting Values

You can update the entity's properties by setting new labels, descriptions, aliases, statements, and sitelinks.

```python
# Set a new label
entity.set_label("en", "New Label")

# Set a new description
entity.set_description("en", "New Description")

# Add an alias
entity.add_alias("en", "New Alias")

# Create new string statement
from entity import Statement

statement = Statement()
statement.set_string_value("P664", "New string value")

# Add qualifier to statement
# Qualifiers are snaks (property-value pairings) attached to statements
# to provide nuance.
from entity import Snak

qualifier = Snak()
qualifier.set_string_value("P38952", "Qualifier string")
statement.add_qualifier(qualifier)

# Add reference to statement
# An individual reference is an array of snaks. The references section
# of a statement is thus an array of arrays.
from entity import Reference

reference = Reference()
ref_part = Snak()
ref_part.set_url_value("P43659", "https://en.wikipedia.org")
reference.add_part(ref_part)
statement.add_reference(reference)

# Add the complete statement to the entity
entity.add_statement(st)

# Add a sitelink to the entity
from entity import Sitelink

sitelink = Sitelink(
    site_code="enwiki",
    title="Douglas Adams",
    url="https://en.wikipedia.org/wiki/Douglas_Adams")

entity.add_sitelink(sitelink)
```
### Other data types

```python
# Monolingual text: property ID, language code, value
st = Statement()
st.set_monolingual_text_value("P98445", "en", "English-language word")
entity.add_statement(st)

# External identifier: property ID, value
st = Statement()
st.set_external_id_value("P98444", "External identifier value")
entity.add_statement(st)

# URL: property ID, value
st = Statement()
st.set_url_value("P7711", "https://archive.org")
entity.add_statement(st)

# Quantity: property ID, quantity, unit of measurement
st = Statement()
st.set_quantity_value("P543", 155, "http://test.wikidata.org/entity/Q71737")
entity.add_statement(st)

# Commons file: property ID, filename (no prefixes)
st = Statement()
st.set_commons_media_value("P98443", "45313-Sougy-Arron.png")
entity.add_statement(st)

# Time value: property ID, date (with positive sign for CE), precision level
st = Statement()
st.set_time_value("P66", "+2001-01-15", 11)
entity.add_statement(st)
```

### Submitting Changes

After making changes to the entity, you can submit the updated data back to the Wikibase instance.

```python
entity.submit()
```

If no entity ID is specified, a new entity will be created. Otherwise, the existing entity will be updated.

### Important Notes
- Before submitting, the script checks if any changes have been made by comparing the current data with the original data. If no changes are detected, the submission is skipped.
- Only "item" type entities are supported for creation; updates can be made to any entity type (at least in theory; for unknown reasons this does not work for properties at the moment).
