====================================================================================
``mod2pip`` - Enhanced requirements.txt generator with dynamic import detection
====================================================================================

.. image:: https://github.com/kactlabs/mod2pip/actions/workflows/tests.yml/badge.svg
        :target: https://github.com/kactlabs/mod2pip/actions/workflows/tests.yml


.. image:: https://img.shields.io/pypi/v/mod2pip.svg
        :target: https://pypi.python.org/pypi/mod2pip


.. image:: https://codecov.io/gh/kactlabs/mod2pip/branch/master/graph/badge.svg?token=0rfPfUZEAX
        :target: https://codecov.io/gh/kactlabs/mod2pip

.. image:: https://img.shields.io/pypi/l/mod2pip.svg
        :target: https://pypi.python.org/pypi/mod2pip

**mod2pip** is an enhanced version of pipreqs that generates pip requirements.txt files based on imports in your project. It addresses the main limitations of the original pipreqs by providing:

✅ **Enhanced Import Detection** - Catches dynamic imports, conditional imports, and late imports that standard tools miss

✅ **Conda Environment Support** - Properly detects packages in conda environments and custom virtual environments  

✅ **Transitive Dependencies** - Experimental support for resolving indirect dependencies

✅ **Better Local Package Detection** - Supports editable packages, namespace packages, and non-standard installations

Installation
------------

.. code-block:: sh

    pip install mod2pip

For minimal installation without Jupyter notebook support:

.. code-block:: sh

    pip install --no-deps mod2pip
    pip install yarg==0.1.9 docopt==0.6.2

Usage
-----

::

    Usage:
        mod2pip [options] [<path>]

    Arguments:
        <path>                The path to the directory containing the application files for which a requirements file
                              should be generated (defaults to the current working directory)

    Options:
        --use-local           Use ONLY local package info instead of querying PyPI
        --pypi-server <url>   Use custom PyPi server
        --proxy <url>         Use Proxy, parameter will be passed to requests library
        --debug               Print debug information
        --ignore <dirs>...    Ignore extra directories, each separated by a comma
        --no-follow-links     Do not follow symbolic links in the project
        --encoding <charset>  Use encoding parameter for file open
        --savepath <file>     Save the list of requirements in the given file
        --print               Output the list of requirements in the standard output
        --force               Overwrite existing requirements.txt
        --diff <file>         Compare modules in requirements.txt to project imports
        --clean <file>        Clean up requirements.txt by removing modules that are not imported in project
        --mode <scheme>       Enables dynamic versioning with <compat>, <gt> or <no-pin> schemes
                              <compat> | e.g. Flask~=1.1.2
                              <gt>     | e.g. Flask>=1.1.2
                              <no-pin> | e.g. Flask
        --scan-notebooks      Look for imports in jupyter notebook files
        --enhanced-detection  Enable enhanced import detection (dynamic imports, conda packages)
        --include-transitive  Include transitive dependencies (experimental)
        --transitive-depth <n> Maximum depth for transitive dependency resolution (default: 2)

Enhanced Features
-----------------

**Dynamic Import Detection**

mod2pip can detect imports that traditional tools miss:

.. code-block:: python

    # Dynamic imports
    module_name = "pandas"
    pd = importlib.import_module(module_name)
    
    # Conditional imports  
    try:
        import tensorflow as tf
    except ImportError:
        tf = None
    
    # Late imports in functions
    def process_data():
        import scipy.stats as stats
        return stats.norm()

**Conda Environment Support**

Works seamlessly with conda environments and detects conda-installed packages that pip-based tools often miss.

**Enhanced Usage Examples**

.. code-block:: sh

    # Basic usage with enhanced detection
    mod2pip --enhanced-detection
    
    # Include transitive dependencies
    mod2pip --enhanced-detection --include-transitive
    
    # Use only local packages (faster, no PyPI queries)
    mod2pip --enhanced-detection --use-local
    
    # Print to stdout instead of file
    mod2pip --enhanced-detection --print

Example Output
--------------

::

    $ mod2pip --enhanced-detection /home/project/location
    INFO: Using enhanced detection for conda packages and dynamic imports
    Successfully saved requirements file in /home/project/location/requirements.txt

Contents of requirements.txt

::

    beautifulsoup4==4.14.3
    numpy==2.4.0
    pandas==2.3.3
    requests==2.32.5
    tensorflow==2.20.0

Why mod2pip over pip freeze?
----------------------------

- ``pip freeze`` only saves packages installed with ``pip install`` in your environment
- ``pip freeze`` saves ALL packages in the environment, including unused ones (without virtualenv)
- ``pip freeze`` misses packages installed via conda or other package managers
- ``pip freeze`` cannot detect dynamically imported packages
- ``mod2pip`` analyzes your actual code imports and generates minimal, accurate requirements

Why mod2pip over pipreqs?
-------------------------

- **Better Import Detection**: Catches dynamic imports, conditional imports, and late imports
- **Conda Support**: Works properly with conda environments and conda-installed packages  
- **Transitive Dependencies**: Optional resolution of indirect dependencies
- **Enhanced Local Detection**: Supports editable packages, namespace packages, and custom installations
- **More Accurate**: Reduces "missing packages" issues common with pipreqs
