Getting Started
===============

This package provides many drivers for different lab hardware. You can find them all in the list here :ref:`hardware-index`.



Starting a device HERO
----------------------

.. important::

   All drivers also run without BOSS, however to use all features we strongly recommend starting them via `BOSS <https://boss-eb4966.gitlab.io/>`_!

The following examples assume the following device configuration in a ``json`` file in the working directory:

.. code-block:: json
   :caption: my_device.json

    {
        "_id": "my-vac-controller",
        "classname": "herosdevices.hardware.gamma_vacuum.EthernetSPC",
        "arguments": {
            "address": "192.0.2.1",
        }
    }

.. tip::

  Check out the `BOSS documentation <https://boss-eb4966.gitlab.io/getting_started.html>`_ to learn more about possible sources.

.. tabs::

   .. tab:: Docker Container

      Install docker and create a ``docker-compose.yml`` file with the following content:

      .. code-block:: yaml

          services:
            vacuum-controller:
              image: registry.gitlab.com/atomiq-project/herosdevices:latest
              restart: always
              network_mode: host
              command: python -m boss.starter -u file:///${PWD}/my_device.json

      Then run it with

      .. code-block:: bash

          docker compose up


   .. tab:: Local Installation

      The device representations can also be installed locally via pip:

      .. hint::

         We recommend using `uv <https://docs.astral.sh/uv/>`_ to maintain an enclosed python environment.

      .. code-block::

         uv pip install heros-boss herosdevices


      Now you are ready to go! You can get an overview over the command line arguments of boss by running

      .. code-block::

         uv run python -m boss.starter -u file:///${PWD}/my_device.json

.. tip::

   Many of the device drivers have an
   `atomiq-compatible interface <https://atomiq-atomiq-project-515d34b8ff1a5c74fcf04862421f6d74a00d9de1b.gitlab.io/heros.html#using-heros-in-the-atomiq-experiment>`_
   so components can be exchanged seamlessly. Look out for inheritance from :py:class:`herosdevices.interfaces.atomiq.AtomiqInterface`.

Adding vendor libraries
-----------------------
Due to the large variety of devices supported by herosdevices, it becomes intractable (and sometimes legally troublesome) to have all dependencies for every device installed in the the base image. It might thus be necessary to extend your installation by required third party libraries in one of the following ways:

.. tabs::

   .. tab:: Docker Container

      While you can extend the docker image by the required packages, BOSS provides an easy way to install dependencies from the compose file during container creation.
      Both processes are described in the `BOSS documentation <https://boss-eb4966.gitlab.io/getting_started.html#additional-dependencies-in-docker>`_.


   .. tab:: Local Installation

      Installing non-python third party drivers locally depends on what OS you are using, please refer to the official documentation of the driver.
      Additional python packages can be installed directly to the ``venv`` you run your ``BOSS`` in. For example:

      .. code:: bash

        uv pip install PyVCAM



