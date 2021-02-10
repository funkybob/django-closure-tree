from django.db.migrations.operations.special import RunSQL


VIEW_TEMPLATE = '''
CREATE OR REPLACE RECURSIVE VIEW {view}(path, ancestor_id, descendant_id, depth) AS

SELECT ARRAY[{node_id}], {node_id}, {node_id}, 0
FROM {table}

UNION ALL

SELECT {table}.{parent_id} || {view}.path, {table}.{parent_id}, {view}.descendant_id, {view}.depth + 1
FROM {table}
INNER JOIN {view} ON ({view}.ancestor_id = {table}.{node_id})
WHERE {table}.{parent_id} IS NOT NULL;
'''


def get_self_reference(model):
    parent_id = [field.column for field in model._meta.fields if field.rel and field.rel.to is model]
    if not parent_id:
        raise Exception('No self-referential field detected.')
    if len(parent_id) > 1:
        raise Exception(
            'Multiple self-referential fields detected. '
            'You can pass the desired parent_field to the CreateTreeClosure migration'
        )
    return parent_id[0]


class CreateTreeClosure(RunSQL):
    reversible = True

    def __init__(self, model_name, parent_field=None):
        self.model_name = model_name.lower()
        self.parent_field = parent_field
        super().__init__('')

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        quote_name = schema_editor.connection.ops.quote_name
        model = from_state.apps.get_model(app_label, self.model_name)
        parent_id = self.parent_field or self.get_self_reference(model)

        self.sql = VIEW_TEMPLATE.format(
            table=quote_name(model._meta.db_table),
            view=quote_name(model._meta.db_table + '_closure'),
            node_id=quote_name(model._meta.pk.column),
            parent_id=quote_name(parent_id)
        )
        super().database_forwards(app_label, schema_editor, from_state, to_state)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        model = from_state.apps.get_model(app_label, self.model_name)
        view_name = model._meta.db_table + '_closure'
        self.reverse_sql = '''DROP VIEW IF EXISTS {view};'''.format(
            view=schema_editor.connection.ops.quote_name(view_name)
        )
        super().database_backwards(app_label, schema_editor, from_state, to_state)
