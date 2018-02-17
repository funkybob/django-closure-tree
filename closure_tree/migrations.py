from django.db.migrations.operations.special import RunSQL


class CreateTreeClosure(RunSQL):
    reversible = True

    def __init__(self, model_name):
        self.model_name = model_name.lower()
        super().__init__('')

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        model = from_state.apps.get_model(app_label, self.model_name)
        view_name = model._meta.db_table + '_closure'

        self.sql = '''
CREATE OR REPLACE RECURSIVE VIEW {view}(path, ancestor_id, descendant_id, depth) AS

SELECT ARRAY[node_id], node_id, node_id, 0
FROM {table}

UNION ALL

SELECT parent_id || path, parent_id, descendant_id, depth + 1
FROM {table}
INNER JOIN {view} ON (ancestor_id = node_id)
WHERE parent_id IS NOT NULL;
'''.format(
    table=schema_editor.connection.ops.quote_name(model._meta.db_table),
    view=schema_editor.connection.ops.quote_name(view_name),
)
        super().database_forwards(app_label, schema_editor, from_state, to_state)


    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        model = from_state.apps.get_model(app_label, self.model_name)
        view_name = model._meta.db_table + '_closure'
        self.reverse_sql = '''DROP VIEW IF EXISTS {view};'''.format(
            view=schema_editor.connection.ops.quote_name(view_name)
        )
        super().database_backwards(app_label, schema_editor, from_state, to_state)
