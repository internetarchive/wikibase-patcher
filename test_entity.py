from entity import *
import unittest

connection = Connection()

class TestSnak(unittest.TestCase):
    def test_set_and_get_property(self):
        snak = Snak()
        snak.set_property("P123", "string")
        self.assertEqual(snak.get_property_id(), "P123")
        self.assertEqual(snak.get_property_type(), "string")

    def test_set_value(self):
        snak = Snak()
        snak.set_value("some_value")
        self.assertEqual(snak.get_value(), {"type": "value", "content": "some_value"})

    def test_set_no_value(self):
        snak = Snak()
        snak.set_no_value()
        self.assertEqual(snak.get_value(), {"type": "novalue"})

    def test_set_unknown_value(self):
        snak = Snak()
        snak.set_unknown_value()
        self.assertEqual(snak.get_value(), {"type": "somevalue"})

    def test_set_wikibase_item_value(self):
        snak = Snak()
        snak.set_wikibase_item_value("P456", "Q789")
        self.assertEqual(snak.get_property_id(), "P456")
        self.assertEqual(snak.get_property_type(), "wikibase-item")
        self.assertEqual(snak.get_value(), {"type": "value", "content": "Q789"})

class TestSitelink(unittest.TestCase):
    def test_set_and_get_title(self):
        sitelink = Sitelink()
        sitelink.set_title("Example Title")
        self.assertEqual(sitelink.get_title(), "Example Title")

    def test_set_and_get_url(self):
        sitelink = Sitelink()
        sitelink.set_url("https://example.com")
        self.assertEqual(sitelink.get_url(), "https://example.com")

    def test_add_and_remove_badge(self):
        sitelink = Sitelink()
        sitelink.add_badge("Q123")
        self.assertIn("Q123", sitelink.get_badges())
        sitelink.remove_badge("Q123")
        self.assertNotIn("Q123", sitelink.get_badges())

class TestReference(unittest.TestCase):
    def test_set_and_get_hash(self):
        reference = Reference()
        reference.set_hash("abc123")
        self.assertEqual(reference.get_hash(), "abc123")

    def test_add_and_remove_part(self):
        reference = Reference()
        snak = Snak(property_id="P123", data_type="string", value_type="value", value_content="some_value")
        reference.add_part(snak)
        self.assertIn(snak.data, reference.data["parts"])
        reference.remove_part(snak)
        self.assertNotIn(snak.data, reference.data["parts"])

class TestStatement(unittest.TestCase):
    def test_set_and_get_id(self):
        statement = Statement(statement_id="S123")
        self.assertEqual(statement.get_id(), "S123")

    def test_set_and_get_rank(self):
        statement = Statement()
        statement.set_rank("preferred")
        self.assertEqual(statement.get_rank(), "preferred")

    def test_add_and_remove_qualifier(self):
        statement = Statement()
        snak = Snak(property_id="P123", data_type="string", value_type="value", value_content="some_value")
        statement.add_qualifier(snak)
        self.assertIn(snak.data, statement.get_qualifiers())
        statement.remove_qualifier(snak)
        self.assertNotIn(snak.data, statement.get_qualifiers())

    def test_add_and_remove_reference(self):
        statement = Statement()
        reference = Reference(ref_hash="abc123")
        statement.add_reference(reference)
        self.assertIn(reference.data, statement.get_references())
        statement.remove_reference(reference)
        self.assertNotIn(reference.data, statement.get_references())

class TestEntity(unittest.TestCase):
    def test_set_and_get_id(self):
        entity = Entity(connection=connection, entity_id="Q123")
        self.assertEqual(entity.get_id(), "Q123")

    def test_set_and_get_label(self):
        entity = Entity(connection=connection)
        entity.set_label("en", "Example Label")
        self.assertEqual(entity.get_label("en"), "Example Label")

    def test_set_and_get_description(self):
        entity = Entity(connection=connection)
        entity.set_description("en", "Example Description")
        self.assertEqual(entity.get_description("en"), "Example Description")

    def test_add_and_remove_alias(self):
        entity = Entity(connection=connection)
        entity.data["aliases"]["en"] = []
        entity.add_alias("en", "Alias 1")
        self.assertIn("Alias 1", entity.get_aliases("en"))
        entity.remove_alias("en", "Alias 1")
        self.assertNotIn("Alias 1", entity.get_aliases("en"))

    def test_get_statements(self):
        entity = Entity(connection=connection)
        self.assertEqual(entity.get_statements(), {})

    def test_get_sitelinks(self):
        entity = Entity(connection=connection)
        self.assertEqual(entity.get_sitelinks(), {})

if __name__ == '__main__':
    unittest.main()
