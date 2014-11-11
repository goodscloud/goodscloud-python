GoodsCloud API client in Python
===============================

.. image:: https://travis-ci.org/goodscloud/goodscloud-python.svg?branch=master
    :target: https://travis-ci.org/goodscloud/goodscloud-python
    :alt: Travis

Installation
------------

.. code-block:: bash

    $ python setup.py install


Interactive Usage
-----------------

.. code-block:: bash

    $ goodscloud_api_client

A Python REPL starts up:

.. code-block:: python

    # Instantiate with API host, username, and password:
    >>> gc = GoodsCloudAPIClient(host="http://app.goodscloud.com", user="test@example.com", pwd="testpass")

    # Then, do requests as follows:
    >>> orders = gc.get(
    >>>     "/api/internal/order",
    >>>     q=dict(filters=[dict(name="channel_id", op="eq", val=16)]), results_per_page=20, page=1)
    200 OK
    >>> first_id = orders.json()['objects'][0]['id']
    >>> gc.patch(url="/api/internal/order/{}".format(first_id),
    >>>     dict(pay_later=True)
    200 OK
    >>> gc.delete(url="/api/internal/order/{}".format(first_id))
    204 NO CONTENT

Writing and running scripts
---------------------------

The files in the ``examples/`` folder and the `GoodsCloud API docs <http://docs.goodscloud.net/>` provide all required information to start writing scripts.

To run a script:

.. code-block:: bash

    $ python <path/to/your/script.py> # your command line arguments go here

Viewing logger output
---------------------

To view logger output on ``STDOUT``, do this:

.. code-block:: python

    >>> import logging
    >>> logging.getLogger('goodscloud_api_client').addHandler(logging.StreamHandler())


Debugging authentication issues
-------------------------------
Instantiating a GoodsCloudAPIClient with ``debug=True`` provides detailed output of the request signing and authentication process.
