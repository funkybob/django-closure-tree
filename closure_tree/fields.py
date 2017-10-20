from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.utils import make_model_tuple
from django.utils.translation import gettext_lazy as _


class ClosureManyToManyField(models.ManyToManyField):
    '''
    Pre-configured M2M that defines a 'through' model automatically for the closure table.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__('self', related_name='children', symmetrical=False, **kwargs)

    def contribute_to_class(self, cls, name, **kwargs):
        if cls._meta.abstract:
            return
        # Define through table
        to_model = cls
        name = '%s_Closure' % cls._meta.object_name

        to = make_model_tuple(to_model)[1]
        from_ = cls._meta.model_name

        to = 'to_%s' % to
        from_ = 'from_%s' % from_

        meta = type('Meta', (), {
            'db_table': self._get_m2m_db_table(cls._meta),
            'auto_created': cls,
            'app_label': cls._meta.app_label,
            'db_tablespace': cls._meta.db_tablespace,
            'unique_together': (from_, to),
            'verbose_name': _('%(from)s-%(to)s relationship') % {'from': from_, 'to': to},
            'verbose_name_plural': _('%(from)s-%(to)s relationships') % {'from': from_, 'to': to},
            'apps': self.model._meta.apps,
            'managed': False,
        })
        # Construct and set the new class.
        self.remote_field.through = type(name, (models.Model,), {
            'Meta': meta,
            '__module__': cls.__module__,
            'path': ArrayField(base_field=models.IntegerField(), primary_key=True),
            'ancestor': models.ForeignKey(cls, related_name='+'),
            'descendant': models.ForeignKey(cls, related_name='+'),
            'depth': models.IntegerField(),
        })

        return super(cls, name, **kwargs)
