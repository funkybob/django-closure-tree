Django closure tree model.
==========================


Abstract base model for creating a Closure Tree using a recursive Postgres view.

http://schinckel.net/2016/01/27/django-trees-via-closure-view/

Usage
=====

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

   $ ./manage.py makenigrations --empty myapp


.. code-block:: python

   from closure_tree.migrations import CreateTreeClosure

   class Migration(migrations.Migration):

       dependencies = [
           ('dummy', '0001_initial'),
       ]

       operations = [
           CreateTreeClosure('MyNode'),
       ]

