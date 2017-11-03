from django.db.migrations.operations.special import RunSQL


class CreateTreeClosure(RunSQL):
    reversible = True

    def __init__(self, model_name):
        self.model_name = model_name.lower()

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        model = from_state.apps.get_model(app_label, self.model_name)
        view_name = model._meta.db_table + '_closure'

        schema_editor.execute('''
CREATE OR REPLACE RECURSIVE VIEW %(view)s(path, ancestor_id, descendant_id, depth) AS

SELECT ARRAY[node_id], node_id, node_id, 0
FROM %(table)s

UNION ALL

SELECT parent_id || path, parent_id, descendant_id, depth + 1
FROM %(table)s
INNER JOIN %(view)s ON (ancestor_id = node_id)
WHERE parent_id IS NOT NULL;
''' % {
    'table': schema_editor.connection.ops.quote_name(model._meta.db_table),
    'view': schema_editor.connection.ops.quote_name(view_name),
})


    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        model = from_state.apps.get_model(app_label, self.model_name)
        view_name = model._meta.db_table + '_closure'
        schema_editor.execute('''DROP VIEW IF EXISTS %s;''' % (
            schema_editor.connection.ops.quote_name(view_name)
        ))
