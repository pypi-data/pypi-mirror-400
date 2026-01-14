![SeaSTAR Logo](seastar-logo-text.png)

SeaSTAR (Sea-faring System for Tagging, Attribution and Redistribution) is a CLI and GUI application for processing biodiversity data collected at sea.

## Use cases
Currently SeaSTAR focuses on processing data collected on the IFCB instrument. It has functionality for interactions with EcoTaxa and CRAB.

## How to install and use
```
$ pip install seastartool
Collecting seastartool
  Downloading seastartool-0.1-py3-none-any.whl.metadata (1.1 kB)
[...]
Successfully installed seastartool-0.1

$ seastar ifcb_v4_features -i testdata/*.hdr -o testout/
```
