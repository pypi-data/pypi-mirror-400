.. _json-head:

JSON Configuration Format
=========================

This page describes the JSON configuration format for HERO devices.
The JSON configuration can be provided as a single HERO config object or as a collection of HERO configs under the ``rows`` key.

Single HERO Config
~~~~~~~~~~~~~~~~~~

A single HERO config is a dictionary with the following keys:

.. code-block:: json

   {
       "_id": "hero_name",
       "classname": "module.class",
       "arguments": {},
       "extra_decorators": {},
       "datasource": {}
   }

.. list-table::
   :widths: 15 10 30
   :header-rows: 1

   * - Key
     - Type
     - Description
   * - ``_id``
     - string
     - Name of the HERO.
   * - ``classname``
     - string
     - Path to the device driver class in the form ``module.class``.
   * - ``arguments``
     - dict
     - Dictionary of keyword-value pairs passed to the ``__init__`` function of the class specified in ``classname``.
   * - ``extra_decorators``
     - dict
     - Dictionary of keyword-value pairs of method name and list of decorator paths.
   * - ``datasource`` (optional)
     - dict
     - Keyword-value pairs that describe a datasource (classes with the ``observable_data`` function).
   * - ``tags`` (optional)
     - list
     - List of tags that are added to the HERO. The tag ``BOSS: {name_of_boss}`` is always added to the tag list independent of this configuration.

Special Arguments
~~~~~~~~~~~~~~~~~

.. code-block:: json

    {
        "_id": "hero_name_1",
        "classname": "module.class",
        "arguments": {
            "loop": "@_boss_loop",
            "some_object": "$remotehero_name"
        }
    }

Event Loop
^^^^^^^^^^
Using ``@_boss_loop`` as the value of the key/value pair in the ``arguments`` part of the configuration passes the ``asyncio.EventLoop`` which is running inside ``BOSS``.
Note, ``asyncio`` support in Zenoh is still in development and using the event loop might not behave as expected.


.. _json-remote-hero:

RemoteHEROs
^^^^^^^^^^^
Sometimes a HERO needs to act on another HERO in the network. BOSS allows to specify a reference to another hero by giving the
name of the HERO with the magic prefix ``$``. When a string with this magic prefix is found, BOSS tries to build a RemoteHERO
object from the given HERO name and passes the RemoteHERO into the constructor of the object to be built. To account for situations
where the HERO is not yet available, BOSS tries several times (default 10 times) to create the RemoteHERO with the given name.

Extra Decorators
~~~~~~~~~~~~~~~~

The ``extra_decorators`` can be used to add decorators to methods during the creation of the HERO.

.. code-block:: json

    {
        "_id": "hero_name_1",
        "classname": "module.Class",
        "extra_decorators": [
            ["some_data", "heros.event"],
            ["_hidden method", "heros.inspect.force_remote"],
            ["foo_bar", "some.module.decorator"],
            ["method", "some.other_module.decorator2"]
        ]
    }

In this example, the method ``module.Class.some_data`` will become an event in the HEROS network.
The method ``module.Class.foo_bar`` is decorated twice according to the order in the list.

.. attention::

    Decorating with ``heros.event`` leads to a fundamental change in the method since it will be transferred into a ``heros.events.LocalEventDescriptor``.
    This, in turn, implies that no further decorator should be applied after the event.
    In fact, using any other decorator in combination with the event decorator may lead to unexpected, undocumented behavior.


Datasource Keys
~~~~~~~~~~~~~~~

The ``datasource`` dictionary supports the following keys:

.. list-table::
   :widths: 15 10 30
   :header-rows: 1

   * - Key
     - Type
     - Description
   * - ``async``
     - bool
     - If ``true``, the device class handles the ``observable_data`` event by itself. If ``false``, the ``observable_data`` function is polled periodically.
   * - ``interval``
     - number
     - Polling interval in seconds.
   * - ``observable``
     - list
     - List of class attributes that are polled and emitted with the ``observable_data`` event.

Multiple HERO Configs
~~~~~~~~~~~~~~~~~~~~~

To define multiple HERO configs, use the ``rows`` key:

.. code-block:: json

   {
       "rows": [
           {
               "_id": "hero_name_1",
               "classname": "module.class",
               "arguments": {},
               "datasource": {}
           },
           {
               "_id": "hero_name_2",
               "classname": "module.class",
               "arguments": {},
               "datasource": {}
           }
       ]
   }


.. warning::

  The ``couchdb`` API may enclose the HERO config dictionary in a ``doc`` keyword. This is handled automatically, so **do not** use ``doc`` as a top-level key in your configuration.


.. tip::

  You may use additional keys for specific use cases, such as CouchDB views. For more information, see :ref:`couchdb-view`.


