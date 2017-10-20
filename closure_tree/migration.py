from django.db.migrations.operations.special import RunSQL


class CreateTreeClosure(RunSQL):

    def __init__(self, model_name):
        self.model_name = model_name

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        # model = from_state.model[app_label, model_name]
        schema_editor.execute('''
CREATE OR REPLACE RECURSIVE VIEW %s_%s_closure(path, ancestor_id, descendant_id, depth) AS

SELECT ARRAY[node_id], node_id, node_id, 0 FROM tree_node

UNION ALL

SELECT parent_id || path, parent_id, descendant_id, depth + 1
FROM tree_node INNER JOIN tree_closure ON (ancestor_id = node_id)
WHERE parent_id IS NOT NULL;
''' % (app_label, self.model_name))

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        # model = from_state.model[app_label, model_name]
        schema_editor.execute('''DROP VIEW %s_%s_closure;''' % (app_label, self.model_name))
