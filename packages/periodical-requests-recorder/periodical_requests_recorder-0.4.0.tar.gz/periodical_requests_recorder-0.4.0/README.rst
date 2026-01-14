
periodical_requests_recorder
============================


.. image:: https://img.shields.io/pypi/v/package_name.svg
   :target: https://pypi.python.org/pypi/periodical_requests_recorder
   :alt: Latest PyPI version


Usage
-----

.. code-block::

   periodical_recorder example.yaml

yaml data format example.

.. code-block:: yaml

   gmail_address: example@gmail.com
   gmail_oauth: "~/yagmail_secret.json"
   tasks:
     - 
       name: "some_data"
       url: "https://example.com/somedata.csv"
       record_dir: "~/hist_data/"
       output_file_format: "{name}/{name}_%Y-%m-%d.csv"
       cron_expr: "0 * * * * * *"
       encoding: "ms932"
     - 
       name: "some_data_2"
       url: "https://www.google.com/"
       record_dir: "~/hist_data/"
       output_file_format: "{name}/{name}_%Y-%m-%d.txt"
       cron_expr: "@reboot"
       target_elements: 
         - 
           element: "#gws-output-pages-elements-homepage_additional_languages__als"
           index: 3

Request result will be stored in the ``record_dir`` with your ``output_file_format``.

If you set up ``yagmail``\ , error messages will be sent to your address.

``cron_expr`` format is the same as `Crython <https://github.com/ahawker/crython>`_.

Installation
------------

You can install this with pip.

Requirements
^^^^^^^^^^^^

Compatibility
-------------

Licence
-------

Authors
-------

periodical_requests_recorder was written by `fx-kirin <fx.kirin@gmail.com>`_.
=================================================================================
