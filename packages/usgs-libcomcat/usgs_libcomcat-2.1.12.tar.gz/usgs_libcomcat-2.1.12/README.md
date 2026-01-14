# Table of Contents
- [Table of Contents](#table-of-contents)
- [Introduction](#introduction)
- [Installation](#installation)
    - [Uninstalling and Updating](#uninstalling-and-updating)
- [Motivation](#motivation)
- [Documentation](#documentation)
- [Getting Help](#getting-help)
- [Citation](#citation)

# Introduction


libcomcat is a project designed to provide a Python equivalent to the ANSS ComCat search
<a href="https://earthquake.usgs.gov/fdsnws/event/1/">API</a>.  This includes a Python library
that provides various classes and functions wrapping around the ComCat API, and a number of command
line programs that use those:

* `findid` Find the ID of an event closest to input parameters (time, latitude, longitude). Also can provide the authoritative ID if an event id is provided.
*  `getcsv` Generate csv or Excel files with basic earthquake information.
*  `geteventhist` Generate csv or Excel files with a history of product submission for an event. Can also create a timeline demonstrating when different product versions were released along with their summaries.
 * `getmags` Download all available magnitudes from all sources.
  * `getpager` Download information that represents the PAGER exposure and loss results.
  * `getphases` Generate csv or Excel files with phase information.
 * `getproduct` Download ComCat product contents (shakemap grids, origin quakeml, etc.)


# Installation
`libcomcat` is now installable via pip:

`pip install usgs-libcomcat`

### Uninstalling and Updating

To uninstall:

`pip uninstall usgs-libcomcat`

To update:

`pip install --upgrade usgs-libcomcat`

# Motivation

libcomcat is a python wrapper for the Comprehensive Catalog (ComCat), which has a [web page interface](https://earthquake.usgs.gov/earthquakes/map/) and [API](https://earthquake.usgs.gov/fdsnws/event/1/). ComCat contains information in **Events** which contain **Products**. Products contain **Contents** in the form of files, maps, etc.

The ComCat interface is very user friendly, but does not support automation. The API supports automation, but limits the number of events that can be returned to 20,000. libcomcat uses the API in a way that allows for:
- Searches returning more than 20,000 eventsource
- Automation of product file downloads
- Extraction of information in product content files

# Documentation

Documentation can be found in the docs folder:
- [API Documentation](https://code.usgs.gov/ghsc/esi/libcomcat-python/-/blob/master/docs/api.md)
- [Command Line Interface Documentation](https://code.usgs.gov/ghsc/esi/libcomcat-python/-/blob/master/docs/cli.md)

Example Jupyter notebooks show how the API can be used to get and manipulate information from ComCat:

*Note: The ShakeMap/DYFI Station Pairs Notebook requires a geodetic distance calculation function*
*, which can be installed via: `pip install geopy`*

- [Classes Notebook](https://code.usgs.gov/ghsc/esi/libcomcat-python/-/blob/master/notebooks/Classes.ipynb)
- [Dataframes Notebook](https://code.usgs.gov/ghsc/esi/libcomcat-python/-/blob/master/notebooks/Dataframes.ipynb)
- [Detailed Event Notebook](https://code.usgs.gov/ghsc/esi/libcomcat-python/-/blob/master/notebooks/DetailEvent.ipynb)
- [Event History Notebook](https://code.usgs.gov/ghsc/esi/libcomcat-python/-/blob/master/notebooks/EventHistory.ipynb)
- [Magnitude Comparison Notebook](https://code.usgs.gov/ghsc/esi/libcomcat-python/-/blob/master/notebooks/ComparingMagnitudes.ipynb)
- [Phase and Magnitude Notebook](https://code.usgs.gov/ghsc/esi/libcomcat-python/-/blob/master/notebooks/PhasesAndMagnitudes.ipynb)
- [Search Notebook](https://code.usgs.gov/ghsc/esi/libcomcat-python/-/blob/master/notebooks/Search.ipynb)
- [Get ShakeMap/DYFI Station Pairs Notebook](https://code.usgs.gov/ghsc/esi/libcomcat-python/-/blob/master/notebooks/GetSMDYFIPairs.ipynb)

# Getting Help

Any questions about libcomcat can be directed to the primary author:

Mike Hearne
mhearne@usgs.gov
# Citation

If you wish to cite this work in your own publication, you may use this DOI:
https://doi.org/10.5066/P91WN1UQ

