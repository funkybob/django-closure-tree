Django closure tree model.
==========================


Abstract base model for creating a Closure Tree using a recursive Postgres view.

https://schinckel.net/2016/01/27/django-trees-via-closure-view/

Usage
-----

Inherit from the Node model:

.. code-block:: python

   from closure_tree.models import Node


   class MyNode(Node):
       name = models.CharField(max_length=30)


Create migrations:

.. code-block:: sh

   $ ./manage.py makemigrations


Add the CreateTreeClosure migration step:

.. code-block:: sh

   $ ./manage.py makemigrations --empty myapp


.. code-block:: python

   from closure_tree.migrations import CreateTreeClosure

   class Migration(migrations.Migration):

       dependencies = [
           ('dummy', '0001_initial'),
       ]

       operations = [
           CreateTreeClosure('MyNode'),
       ]


Usage in an existing app
------------------------

Add a field for the closure table reference to your model that already has a self-referencing
foreign key.

.. code-block:: python

    from closure_tree.fields import ClosureManyToManyField

    class MyModel(models.Model):
        parent = models.ForeignKey('self', related_name='children', null=True, blank=True, on_delete=models.CASCADE)

        ...

        descendants = ClosureManyToManyField('self', symmetrical=False, related_name='ancestors')


And create a migration (as above).
