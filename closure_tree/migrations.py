from django.db.migrations.operations.special import RunSQL


class RunStuff(RunSQL):
    reversible = True

    def __init__(self, model_name):
        self.model_name = model_name.lower()

    def state_forwards(self, app_label, state):
        pass

    def get_model(self, from_state, app_label):
        return from_state.apps.get_model(app_label, self.model_name)

    def get_table_name(self, model):
        return model._meta_db_table

    def get_view_name(self, model):
        return model._meta.db_table + '_closure'

    def get_params(self, model):
        return {
            'table': schema_editor.connection.ops.quote_name(self.get_view_name(model)),
            'view': schema_editor.connection.ops.quote_name(self.get_table_name(model)),
        }

class CreateTreeClosure(RunStuff):
    reversible = True

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        model = self.get_model(from_state, app_label)
        params = self.get_params(model)

        schema_editor.execute('''
CREATE OR REPLACE RECURSIVE VIEW %(view)s(path, ancestor_id, descendant_id, depth) AS

SELECT ARRAY[node_id], node_id, node_id, 0
FROM %(table)s

UNION ALL

SELECT parent_id || path, parent_id, descendant_id, depth + 1
FROM %(table)s
INNER JOIN %(view)s ON (ancestor_id = node_id)
WHERE parent_id IS NOT NULL;
''' % params)
})

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        model = self.get_model(from_state, app_label)
        params = self.get_params(model)

        schema_editor.execute('''DROP VIEW IF EXISTS %(view)s;''' % params)


class CreateCycleDetect(RunStuff):

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        model = self.get_model(from_state, app_label)
        params = self.get_params(model)

        schema_editor.execute('''
CREATE OR REPLACE FUNCTION prevent_%(table)s_cycles()
RETURNS TRIGGER AS $$

BEGIN
  IF (NEW.parent_id IS NOT NULL)
  THEN
    IF EXISTS (
      SELECT node_id
      FROM %(view)s
      WHERE NEW.group_id = ANY(ancestors)
      AND node_id = NEW.parent_id
    )
    THEN
      RAISE EXCEPTION 'Cyclic data detected';
    END IF;
  END IF ;

  RETURN NEW;
END;

$$ LANGUAGE plpgsql;

CREATE TRIGGER prevent_%(table)s_cycles
BEFORE UPDATE ON %(table)s
FOR EACH ROW
EXECUTE PROCEDURE prevent_%(view)s_cycles()
''' % params)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        model = self.get_model(from_state, app_label)
        params = self.get_params(model)

        schema_editor.execute('''
DROP TRIGGER prevent_%(table)s_cycles;
DROP FUNCTION prevent_%(table)s_cycles;
''' % params)
