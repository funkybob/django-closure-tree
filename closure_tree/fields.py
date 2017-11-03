from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.fields.related import resolve_relation
from django.db.models.utils import make_model_tuple
from django.utils.translation import gettext_lazy as _


class ClosureManyToManyField(models.ManyToManyField):
    '''
    Pre-configured M2M that defines a 'through' model automatically for the closure table.
    '''

    def contribute_to_class(self, cls, name, **kwargs):
        if not cls._meta.abstract:
            # Define through table
            meta = type('Meta', (), {
                'db_table': '%s_closure' % cls._meta.db_table,
                'app_label': cls._meta.app_label,
                'db_tablespace': cls._meta.db_tablespace,
                'unique_together': ('ancestor', 'descendant'),
                'verbose_name': _('ancestor-descendant relationship'),
                'verbose_name_plural': _('ancestor-descendant relationships'),
                'apps': cls._meta.apps,
                'managed': False,
            })
            # Construct and set the new class.
            name_ = '%s_Closure' % cls._meta.model_name
            self.remote_field.through = type(name_, (models.Model,), {
                'Meta': meta,
                '__module__': cls.__module__,
                'path': ArrayField(base_field=models.IntegerField(), primary_key=True),
                'ancestor': models.ForeignKey(
                    cls,
                    related_name='%s+' % name_,
                    db_tablespace=self.db_tablespace,
                    db_constraint=self.remote_field.db_constraint,
                    on_delete=models.CASCADE,
                ),
                'descendant': models.ForeignKey(
                    cls,
                    related_name='%s+' % name_,
                    db_tablespace=self.db_tablespace,
                    db_constraint=self.remote_field.db_constraint,
                    on_delete=models.CASCADE,
                ),
                'depth': models.IntegerField(),
            })

        super().contribute_to_class(cls, name, **kwargs)
