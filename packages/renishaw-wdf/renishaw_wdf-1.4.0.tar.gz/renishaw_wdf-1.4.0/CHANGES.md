# ChangeLog

## 1.4.0

  * Update WdfBlockId values to match upcoming software release
  * Return the data type and units enums with the xlist/ylist values
  * Added examples for extracting whitelight images from file for both
    the primary whitelight image and per-spectrum images.
  * Added get_spectrum_properties method to retrieve any per-spectrum data.

## 1.3.1

  * Include the Masked flag in WdfSpectrumFlags
  * Converted WdfBlockId values to an enum
  * Provide collection indexing for nested psets and array members
    eg: `item['child']['grandchild']`
  * BUGFIX: corrected error handling step > 1 in data origin slices.

## 1.2.0

  * Include tests in the source distribution
  * Added bounds checks for the spectum function
  * Make use of enum for Pset types and flags fields.
  * Added support for python 3.12
