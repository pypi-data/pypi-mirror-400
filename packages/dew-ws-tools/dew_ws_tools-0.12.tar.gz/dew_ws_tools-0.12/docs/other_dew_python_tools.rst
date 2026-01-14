Other DEW Python tools
======================
There are a few different Python packages   which might be useful to you at DEW.

python-sa-gwdata
----------------
Provides a way to download some groundwater data from Python scripts outside the government
intranet.

It is publicly available: see the `complete documentation <https://python-sa-gwdata.readthedocs.io/en/latest/>`__.
I wouldn't recommend it unless you need your code to run in situations where you cannot be on the
intranet, because the access it provides is not as flexible or complete as the packages below.

sageodata_db
------------
Provides bindings and ability to run queries directly on SA Geodata.

This provides a link to the SA Geodata database, and a set of predefined queries to retrieve all kinds of
groundwater data. You must be on the intranet to run it. In general I don't recommend using this directly,
because it is wrapped by other easier-to-use packages such as dew_gwdata (see below).

It is available to install publicly but the documentation and code is only available internally at DEW: 
`http://bunyip:8191/python-docs/sageodata_db/latest_source/index.html <http://bunyip:8191/python-docs/sageodata_db/latest_source/index.html>`__.

dew_gwdata
----------
Provides code to make it easier to access and use groundwater data stored in a variety of internal databases at DEW.

This has links and methods for retrieving a wide variety of groundwater data from various sources:

- SA Geodata (a wide variety of drillhole data) via either predefined or custom queries
- Aquarius Time Series (logger time series data)
- Water Data Entry extended database (well maintenance notes and alerts)
- WILMA (Water Licensing data include usage and allocations)
- Gtslogs (geophysical logging data)

This is a great place to start! Again, you'll need to be on the intranet to use it in most cases.

It is available to install publicly but the documentation and code is only available internally at DEW: 
`http://bunyip:8191/python-docs/dew_gwdata/latest_source/index.html <http://bunyip:8191/python-docs/dew_gwdata/latest_source/index.html>`__.

wrap_technote
-------------
Code to semi-automate aspects of annual groundwater resource reporting.

This package contains code, scripts, and notebooks for automating the groundwater and rainfall data processing
for the annual water resource reporting process at DEW (WRAP). 

It is available to install publicly but the documentation and code is only available internally at DEW: 
`http://bunyip:8191/python-docs/wrap_technote/latest_source/index.html <http://bunyip:8191/python-docs/wrap_technote/latest_source/index.html>`__.
