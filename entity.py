class WikibaseEntity:
    def __init__(self, api, entity_id):
        self.api = api
        self.entity_id = entity_id
        self.entity_data = self.api.get_item(self.entity_id)

    def add_label(self, language, label):
        self.entity_data['labels'][language] = {'language': language, 'value': label}
        self.api._put(f"/entities/items/{self.entity_id}/labels/{language}", self.entity_data['labels'][language])

    def add_description(self, language, description):
        self.entity_data['descriptions'][language] = {'language': language, 'value': description}
        self.api._put(f"/entities/items/{self.entity_id}/descriptions/{language}", self.entity_data['descriptions'][language])

    def add_alias(self, language, alias):
        if language in self.entity_data['aliases']:
            self.entity_data['aliases'][language].append({'language': language, 'value': alias})
        else:
            self.entity_data['aliases'][language] = [{'language': language, 'value': alias}]
        self.api._put(f"/entities/items/{self.entity_id}/aliases/{language}", self.entity_data['aliases'][language])

    def add_claim(self, property_id, data_value, data_type):
        claim = {
            'mainsnak': {
                'snaktype': 'value',
                'property': property_id,
                'datavalue': {
                    'value': data_value,
                    'type': data_type
                }
            },
            'type': 'statement'
        }
        self.api.add_statement(self.entity_id, claim)

    def delete_statement(self, statement_id):
        self.api.delete_statement(statement_id)

    def update_statement(self, statement_id, data):
        self.api.update_statement(statement_id, data)
