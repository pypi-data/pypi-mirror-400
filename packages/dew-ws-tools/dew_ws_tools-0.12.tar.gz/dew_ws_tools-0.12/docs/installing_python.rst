####################################
Installing Python and Oracle Client
####################################

To use most of the tools here you'll need Python to run code, and Oracle Client, to access SA Geodata.

- Python: I recommend you use an Anaconda distribution of Python (or something equivalent 
  such as Miniforge) as some packages require Python packages like
  geopandas and pillow. The latter are not easily
  installed with pip (the default Python package manager).
- Oracle: the bindings to SA Geodata require the Oracle Instant Client (at least)
  to be installed.

Instructions for installing Python and Oracle follow. You can skip these if you have
them installed already.

There are two methods for installing Python:

1. Method A: use a packaged version from the Software Center. This can only be used
if you are the sole user of the computer i.e. your work laptop. Advantages:
simpler for you. Disadvantages: it is quite an old version of Python (3.6) which
will eventually lead you to needing to employ some workarounds; it uses the conda
package manager, which is slow to install, update, and remove packages.

2. Method B: install Python yourself under c:\devapps. This is the only way to 
install it on a shared machine (i.e. a server). Advantages: more flexible and up-to-date;
can be managed/debugged/fixed without involvement from the Helpdesk; uses the
mamba package manager, which is must faster for installing, updating, and removing
packages. Disadvantages: fiddly to install.

Method A for installing Python: Software Center version
============================================================

If you are the only user of your computer that will need Python, you can 
install Python and Oracle from the Software Center. The package is called
"Miniconda Python":

.. warning:: This distribution has become quite out of date over the last
    few years (as of 2023) - Python 3.6 is very old and not supported.
    Until the package can be updated, I suggest you follow the instructions
    below for method B, as that will get you the
    most up-to-date version of Python to begin with.

1. Visit https://serviceportal.env.sa.gov.au

2. Select "Install Software"

.. figure:: figures/software_center_install.png

3. Search for and select "Miniconda Python distribution"

.. figure:: figures/software_center_select.png

The distribution is a customised distribution arranged by Tristan Ryan
and Kent Inverarity, and includes Oracle Instant Client.


Method B for installing Python: in c:\\devapps 
===============================================

The distribution above (method A) does not work properly on shared machines, where
multiple users will be using the same installation. Currently, the only
solution for this is installing a different sandboxed Python for each
user. Follow the instructions below carefully, and please contact  
`Kent Inverarity <mailto:kent.inverarity@sa.gov.au>`_ with any questions
or problems - you can also call on 0422746056 or on Microsoft Teams.

Install Python 
--------------

Download the "Miniforge" installer 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Download the file named ``Miniforge3-Windows-x86_64.exe`` from 
https://github.com/conda-forge/miniforge#miniforge3 

.. figure:: figures/python_mambaforge.png

Save this file somewhere under ``c:\devapps``, so that you can execute it. 
You should create the ``c:\devapps`` folder if it does not already exist.

Install Miniforge 
^^^^^^^^^^^^^^^^^^

.. note:: The following instructions refer to "Mambaforge". Please ignore
    it. The name effectively changed from "Mambaforge" to "Miniforge" in 2023 
    but there is functionally no difference at all between the two, and you can
    continue to use the instructions below exactly as they are, to the
    letter.

Create your own folder under devapps e.g. 
``c:\devapps\YOURNAME_python\mambaforge``. This is the location where you will
install Python, and it should end in a folder called ``mambaforge``. 
(Obviously replace ``YOURNAME`` with your first name here and in all following
steps below).

Run the installer you downloaded. 

When the warning appears, click on “More Info” and “Run anyway”. 
The warning relates to the fact that the installer is not released and signed
by Microsoft. 

.. figure:: figures/python_smartscreen.png
.. figure:: figures/python_mambaforge_installer_1.png

Install into the path you created above i.e.
``c:\devapps\YOURNAME_python\mambaforge``

.. figure:: figures/python_mambaforge_installer_2.png

Note to follow steps below: 

.. figure:: figures/python_mambaforge_installer_3.png

Create a folder for temporary files 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create an empty folder called “temp” inside where you put Mambaforge (i.e.
``c:\devapps\YOURNAME_python\mambaforge\temp``):

.. figure:: figures/python_temp_path.png

Create a batch file which will be run every time you use Command Prompt 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create a batch file called ``YOURNAME_cmd_init.bat`` alongside your Python
folder, in e.g.: ``C:\devapps\YOURNAME_python``

So the batch file you create would be:

``C:\devapps\YOURNAME_python\YOURNAME_cmd_init.bat``

Remember, replace ``YOURNAME`` with the first name you are using. So for me this
file is: ``c:\devapps\kent_python\kent_cmd_init.bat``

Open your batch file for editing in Notepad++.

And fill it with the contents of this template batch file. See here for a 
version you can copy: 

https://gitlab.com/-/snippets/2209918/raw/main/YOURNAME_cmd_init.bat  

.. figure:: figures/python_kent_cmd_init_1.png

You will need to change the parts containing ``YOURNAME`` to match the directory
name where you have installed Mambaforge. 

Make sure there are no trailing spaces on any of the lines. 

End result should look like this: 

.. figure:: figures/python_kent_cmd_init_2.png

Register the above batch file with Windows by running this command once: 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Copy this line into Notepad++ 

.. code-block:: 
    
    reg add "HKCU\Software\Microsoft\Command Processor" /v AutoRun /t REG_EXPAND_SZ /d "c:\devapps\YOURNAME_python\YOURNAME_cmd_init.bat" /f 

.. figure:: figures/python_regedit_1.png

And update ``YOURNAME``: 

.. figure:: figures/python_regedit_2.png

Copy this text, open Command Prompt and paste this in and run it: 

.. figure:: figures/python_regedit_3.png
.. figure:: figures/python_regedit_4.png

Close Command Prompt 

Installing Oracle
-----------------

Download Oracle Instant Client
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Download the "Basic Light Package" of Oracle Instant Client.

https://download.oracle.com/otn_software/nt/instantclient/213000/instantclient-basiclite-windows.x64-21.3.0.0.0.zip

Install by unzipping
^^^^^^^^^^^^^^^^^^^^

Unzip this file into this folder (create it if necessary): ``c:\devapps\oracle_instant_client_x64``.

.. figure:: figures/oracle_unzip.png

Find where it was installed
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Identify the version which was downloaded and installed by looking in the folder:

.. figure:: figures/oracle_folder.png

In my case, this path is: ``C:\devapps\oracle_instant_client_x64\instantclient_21_3``

.. note:: If you are using a server and this path already exists, you can use it without following the steps above.

Tell Windows where it was installed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Add the path above to your environment variable. In the Windows search box type "environment variable" and select the option
that says "Edit environment variables for your account".

.. figure:: figures/oracle_envvar1.png

Select "PATH" and click the "Edit" button.

.. figure:: figures/oracle_envvar2.png

Click the "New" button.

.. figure:: figures/oracle_envvar3.png

Paste the path from above and click OK twice to close both dialog boxes.

.. figure:: figures/oracle_envvar4.png

How to use Python 
=================

Running Python from the command line
------------------------------------

Run Command Prompt. You should see something like this happen: 

.. figure:: figures/python_cmd_1.png

This places you in your ``base`` conda environment, from here you can run a Python 
interpreter by typing ``python`` or you can run python scripts by using 
``python your_script.py``. 

How to install Jupyter Notebook 
-------------------------------

Jupyter Notebook is used widely across the Python scientific computing 
environment - it's a good idea to set it up early so you can use it. To install
it, follow the instructions below:

Run this command when you are in the base environment (i.e. the command prompt 
looks like ``(base) U:\>``):

.. code-block:: none

    mamba install jupyter nb_conda_kernels ipykernel ipython 

You can launch Jupyter Notebook with: 

.. code-block:: none

    jupyter notebook

How to install Spyder
---------------------

Spyder is a widely used IDE (integrated development environment). You can install
and use it in a very similar way to Jupyter:

Run this command when you are in the base environment (i.e. the command prompt 
looks like ``(base) U:\>``):

.. code-block:: none

    mamba install spyder

You can then launch Spyder from the Command Prompt with:

.. code-block:: none

    spyder

Learn about conda environments 
------------------------------

You can install packages using either the “mamba” package manager (equivalent 
to “conda” but faster) or by using the standard Python tool “pip”. 

Conda environments are a way of "sandboxing" packages from each other,
so that if you run into a problem when installing a Python package, you
don't have to reinstall all of Python on your computer. It's a good idea
to get used to how they work.

I strongly recommend reading up on conda environments: 
https://docs.conda.io/projects/conda/en/4.6.1/user-guide/getting-started.html#managing-envs 

To create a basic environment called, for example, “working”: 

.. code-block:: none

    mamba create -n working pandas scipy matplotlib geopandas pyodbc pillow 

And then using it by typing this each time you load Command Prompt 

.. code-block:: none

    conda activate working 

Alternatively if you only want to use Jupyter Notebooks you can run Jupyter
from the base environment:

.. code-block:: none

    jupyter notebook

And then select the ``working`` environment's kernel in the notebook itself, e.g.: 

.. figure:: figures/python_jupyter_kernel_selection_1.png

Or 

.. figure:: figures/python_jupyter_kernel_selection_2.png
