Getting Started
===============


Possible Configuration Sources
++++++++++++++++++++++++++++++

Device configuration data can be supplied to BOSS from various sources.

.. tabs::

   .. tab:: JSON File

      For testing purposes or isolated BOSS instances, you can directly supply a :ref:`JSON file <json-head>`
      with the device configuration inside. Run BOSS with the *absolute path* to the JSON file:

      .. code-block:: bash

         python -m boss.starter --u file:///absolute/path/to/file.json


   .. tab:: Network based JSON Database

      For a production setup, we recommend using a network based database like CouchDB. This has the advantage, that
      all configurations are at a central point and are easy to maintain.

      .. code-block:: bash

         python -m boss.starter -u http://<user>:<pw>@<couchdb_host>:5984/my-boss/http-test

      See :ref:`CouchDB <couchdb-head>` for more details.


   .. tab:: Environment Variables

      BOSS can also load the configuration from environment variables

      .. code-block:: bash

          export BOSS1={"_id": "docker-env-ftp","classname": "ftplib.FTP","arguments": {"host": "ftp.us.debian.org"}}
          python -m boss.starter -e BOSS1

      This can make sense for example for docker based portable deployments. An example of this can be found in the
      Docker :ref:`compose file below <start-compose>`.


.. hint::

   BOSS uses *urllib* to parse the url specified by the ``-u`` argument, which supports many more `url schemes <https://docs.python.org/3/library/urllib.parse.html>`_ than listed here.
   This means you can use also completely different endpoints to host your configuration for BOSS like `ftp` or `svn`, the only requirement
   is that there is a valid JSON configuration string at the end.

Installing/Deploying BOSS
+++++++++++++++++++++++++

.. tabs::


    .. _start-compose:
    .. tab:: Docker Compose

        A convenient way to deploy BOSS is inside of a docker container. You can find pre-build containers images in
        our docker `registry <https://gitlab.com/atomiq-project/boss/container_registry>`_.


        .. hint::

           You can also build the BOSS docker image yourself from the Dockerfile in the repository:
           ``docker build -t atomiq/boss .``
           By building the docker image yourself, you can `modify the docker image <https://docs.docker.com/build/building/base-images/>`_
           and add for example custom device vendor libraries or similar.


        A BOSS docker service can be started with the following compose file

        .. code-block:: yaml

            services:
              httpclient:
                image: registry.gitlab.com/atomiq-project/boss:latest
                restart: always
                network_mode: host
                environment:
                 - |
                   BOSS1=
                   {
                    "_id": "docker-env-ftp",
                       "classname": "ftplib.FTP",
                       "arguments": {
                            "host": "ftp.us.debian.org"
                       }
                   }
                command: python -m boss.starter -e BOSS1

        Additionally, also specifying a file or URL is possible, such that (mounted) json files in the docker container or web
        URLs can be used as configuration sources. Note that the ``-e`` and ``-u`` options can be specified in the command line
        multiple times to define several objects that should be instantiated by the BOSS.

    .. tab:: Local Installation

        BOSS can also be installed locally via pip:

        .. hint::

           We recommend using `uv <https://docs.astral.sh/uv/>`_ to maintain an enclosed python environment.

        .. tabs::

           .. tab:: uv

              .. code-block::

                 uv pip install heros-boss


           .. tab:: other

              .. code-block::

                 pip install heros-boss


        Now you are ready to go! You can get an overview over the command line arguments of boss by running

        .. tabs::

           .. tab:: uv

              .. code-block::

                 uv run python -m boss.starter --help


           .. tab:: other

              .. code-block::

                 python -m boss.starter --help


Additional Dependencies in Docker
+++++++++++++++++++++++++++++++++

Due to the large variety of devices supported by herosdevices, it becomes intractable (and sometimes legally troublesome) to have all dependencies for
every device installed in the the base image. It might thus be necessary to extend the docker image by required third party libraries in one of the
following ways:

.. tabs::

   .. tab:: BOSS native

     BOSS can install dependencies from various sources during container creation. You can specify these dependencies in the docker-compose file as the following minimal example shows:

     .. code-block:: yaml
        :caption: docker-compose.yaml

        services:
          myboss:
            image: registry.gitlab.com/atomiq-project/boss
            restart: always
            network_mode: host
            environment:
              - BOSS_PIP_PKGS=toptica-lasersdk pyserial
              - BOSS_APT_PKGS=libftdi1
              - PVCAM_SDK_PATH=/opt/pvcam/sdk # For pvcam installed via script below
            command: python -m boss.starter --log debug --expose
            volumes:
              - ./my_pkgs/:/etc/boss/

     * ``BOSS_PIP_PKGS``: Packages specified here are installed into the environment via pip. Every valid pip package syntax is usable (Notably ``git+https://...``). Here `pyserial <https://pypi.org/project/pyserial/>`_ and `toptica-lasersdk <https://pypi.org/project/toptica-lasersdk/>`_ are installed.
     * ``BOSS_APT_PKGS``: Packages specified here are installed via the `apt` package manager. The base image is based on debian so everything debian offers can be added here. Here ``libftdi1``.

       .. note::

          Packages via ``apt`` are installed first so that they are available during the installation of ``pip`` packages.

     * **Local Packages**: The starter looks for files with the extensions ``.boss.sh`` in ``/etc/boss``. In the example the folder, ``./my_pkgs`` residing in the same directory as the compose file is mounted to that location. The following scripts install the `pvcam <https://www.teledynevisionsolutions.com/products/pvcam-sdk-amp-driver>`_ software.

       .. code-block:: bash
         :caption: pvcam.boss.sh

         # Install prerequisites
         apt-get update && apt-get install -y sudo git

         # Install the vendor library itself
         # We have to agree to some licenses here so we use the "yes" command.
         # The EUID=1 is a little hack to trick the installer into thinking we're not root.
         /bin/sh -c 'yes | EUID=1 /bin/bash ./pvcam/pvcam__install_helper-Ubuntu.sh'

         # Remove build files after installation to make image a bit smaller
         rm -rf /pvcam

         # We need to point the python api to the correct library path
         export PVCAM_SDK_PATH="/opt/pvcam/sdk"
         # Install python API
         pip install --break-system-packages PyVCAM


   .. tab:: Extend Docker Image

     If you want to generate a permanent image with your drivers, you have to extent the ``BOSS`` base image.

     .. note::

        Note that you have to repeat this process for every update of the base image. We therefore recommend the **BOSS native** method for most use cases.

     The following example shows this process at the example of :py:class:`herosdevices.hardware.teledyne.pvcam.PvcamCamera`:

     - Create a new a directory and download and unzip the `binary drivers <https://www.teledynevisionsolutions.com/products/pvcam-sdk-amp-driver/?model=PVCAM-SDK&vertical=tvs-princeton-instruments&segment=tvs>`_.
       There should now be two folders ``pvcam`` and ``pvcam-sdk`` among others.
     - Create ``Dockerfile`` with the following content:

       .. literalinclude :: ../../examples/expand_docker/Dockerfile
          :language: docker


       .. tip::

          The docker container runs a debian system. Vendor libraries for ubuntu are therefore mostly compatible.

     - Run ``sudo docker buildx build --tag herosdevices:pvcam .``

       .. tip::

         The ``:pvcam`` is the tag name of the image. You should choose something to make it descriptive of what you put in the image.

     - In your docker compose files, replace the ``registry.gitlab.com/atomiq-project/herosdevices:latest`` by ``herosdevices:pvcam``.

Accessing Devices inside a Container
++++++++++++++++++++++++++++++++++++

If the objects started by BOSS need access on device connected directly to the host machine (e.g. living in ``/dev``, like ``/dev/ttyUSB0``) you need to pass the device to the container.

.. tabs::

   .. tab:: Individual Devices

     Using the ``device`` flag, you can mount individual devices into your container.

     .. code-block:: yaml
        :caption: docker-compose.yaml

        services:
          myboss:
            image: registry.gitlab.com/atomiq-project/boss
            restart: always
            network_mode: host
            command: python -m boss.starter -u <url> --expose
            devices:
              - /dev/ttyUSB0
              - /dev/ttyUSB1

     .. important::

       The device must be present during container startup.
       If you unplug and re-plug a device, the running container does not know about this and needs to be restarted to be able to use it.


   .. tab:: All Devices

     Using the ``privileged`` flag mounts a mirror of ``/dev`` into your container.

     .. warning::

       ``privileged`` gives your container root access to your host machine. Typically this is not an issue for this use case, but you should be aware of this.
       `Learn more... <https://docs.docker.com/reference/cli/docker/container/run/#privileged>`_

     .. important::

       If you add devices during container runtime (e.g. plugging in new devices or re-plugging devices) the running container does not know about this and needs to be restarted to be able to use it.
       You can avoid this behavior by directly mounting the ``/dev`` folder (see compose example below).

       Note that this is also necessary if you are using custom ``udev`` symlinks like ``/dev/MY_USB_DEVICE -> /dev/ttyUSB0``, as symlinks are not added by the ``privileged`` flag.

     .. code-block:: yaml
        :caption: docker-compose.yaml

        services:
          myboss:
            image: registry.gitlab.com/atomiq-project/boss
            restart: always
            network_mode: host
            command: python -m boss.starter -u <url> --expose
            privileged: true
            volumes:
              - /dev:/dev # optional to sync changes


