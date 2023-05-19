# wikibase-patcher

A minimum viable implementation of the Wikibase REST API in Python.

See `example.py` for a demo script that updates Wikibase statements.

## Known issues
This is very much under development, and nothing is guaranteed to work.

* `WikibaseEntity.update_statement` and other PATCH-based methods have not been fully implemented