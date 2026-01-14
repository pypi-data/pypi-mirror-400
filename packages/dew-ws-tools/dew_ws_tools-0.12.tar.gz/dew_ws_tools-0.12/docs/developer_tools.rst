Tools for developers
====================

Publishing Python packages internally
-------------------------------------

dew_ws_tools installs a command-line utility called publish_locally. You can
use this to publish a new version of a python package to a central network
drive location.

An example is below for when I've made a new version of, say, sageodata_db,
and am ready to build and release it as ``v0.5``:

.. code-block::

    $ git tag v0.5
    $ python -m build

This creates the wheel file in the ``dist\`` folder as usual.

To use the publish_locally script I would then run:

.. code-block::

   $ publish_locally v0.5

The publish_locally script will:

1. Copies wheel file to package repositories: the Groundwater Toolbox folder. 
   This step will be skipped if tag is
   'latest_source', because by definition that doesn't have a wheel file.
2. Builds the Sphinx docs in the repository - this means you most definitely
   need the tag checked out, as per the code above.
3. Copies the built Sphinx docs to the documentation location, which is
   also under the Groundwater Toolbox
4. re-creates the "base" Sphinx docs page, to link between all the different
   packages and versions.

.. note:: I suggest the additional step of publicly releasing your Python
   packages on PyPI e.g. ``twine upload dist\-0.5*`` - this makes life 
   much easier for your internal users.

Publishing internal documentation for Python packages
-----------------------------------------------------------------

You can also run the above command with the tag omitted to follow
steps 2 through 4 above i.e. build documentation for the current state of
the checked-out branch. It will use a fake documentation release of 
"latest_source", similar to readthedocs.org's "latest":

.. figure:: figures/sphinx_latest_source.png

.. figure:: figures/sphinx_postrelease.png

API documentation for dew_ws_tools
----------------------------------

.. autofunction:: dew_ws_tools.publish_locally.publish_locally