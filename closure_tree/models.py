from django.db import models

from .fields import ClosureManyToManyField


class Node(models.Model):
    node_id = models.AutoField(primary_key=True)
    parent = models.ForeignKey('self', related_name='children', null=True, blank=True, on_delete=models.CASCADE)

    descendants = ClosureManyToManyField('self', symmetrical=False, related_name='ancestors')

    class Meta:
        abstract = True
