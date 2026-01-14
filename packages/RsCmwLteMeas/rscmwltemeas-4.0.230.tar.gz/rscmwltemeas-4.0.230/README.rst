==================================
 RsCmwLteMeas
==================================

.. image:: https://img.shields.io/pypi/v/RsCmwLteMeas.svg
   :target: https://pypi.org/project/ RsCmwLteMeas/

.. image:: https://readthedocs.org/projects/sphinx/badge/?version=master
   :target: https://RsCmwLteMeas.readthedocs.io/

.. image:: https://img.shields.io/pypi/l/RsCmwLteMeas.svg
   :target: https://pypi.python.org/pypi/RsCmwLteMeas/

.. image:: https://img.shields.io/pypi/pyversions/pybadges.svg
   :target: https://img.shields.io/pypi/pyversions/pybadges.svg

.. image:: https://img.shields.io/pypi/dm/RsCmwLteMeas.svg
   :target: https://pypi.python.org/pypi/RsCmwLteMeas/

Rohde & Schwarz CMW LTE Measurement RsCmwLteMeas instrument driver.

Basic Hello-World code:

.. code-block:: python

    from RsCmwLteMeas import *

    instr = RsCmwLteMeas('TCPIP::192.168.2.101::hislip0')
    idn = instr.utilities.query('*IDN?')
    print('Hello, I am: ' + idn)

Supported instruments: CMW500,CMW100,CMW270,CMW280,CMP

The package is hosted here: https://pypi.org/project/RsCmwLteMeas/

Documentation: https://RsCmwLteMeas.readthedocs.io/

Examples: https://github.com/Rohde-Schwarz/Examples/


Version history
----------------

Release Notes:

Latest release notes summary: Update for FW 4.0.230

	Version 4.0.230
		- Update for FW 4.0.230
		- Several bugfixes

	Version 4.0.112
		- Added Result query methods without CC{Nr} header
		- Changed minimal Python requirement to 3.8

	Version 4.0.111
		- Added commands for use without CC{Nr} header

	Version 4.0.110
		- Update for FW 4.0.110

	Version 3.8.xx2
		- Fixed several misspelled arguments and command headers

	Version 3.8.xx1
		- Bluetooth and WLAN update for FW versions 3.8.xxx

	Version 3.7.xx8
		- Added documentation on ReadTheDocs

	Version 3.7.xx7
		- Added 3G measurement subsystems RsCmwGsmMeas, RsCmwCdma2kMeas, RsCmwEvdoMeas, RsCmwWcdmaMeas
		- Added new data types for commands accepting numbers or ON/OFF:
		- int or bool
		- float or bool

	Version 3.7.xx6
		- Added new UDF integer number recognition

	Version 3.7.xx5
		- Added RsCmwDau

	Version 3.7.xx4
		- Fixed several interface names
		- New release for CMW Base 3.7.90
		- New release for CMW Bluetooth 3.7.90

	Version 3.7.xx3
		- Second release of the CMW python drivers packet
		- New core component RsInstrument
		- Previously, the groups starting with CATalog: e.g. 'CATalog:SIGNaling:TOPology:PLMN' were reordered to 'SIGNaling:TOPology:PLMN:CATALOG' give more contextual meaning to the method/property name. This is now reverted back, since it was hard to find the desired functionality.
		- Reorganized Utilities interface to sub-groups

	Version 3.7.xx2
		- Fixed some misspeling errors
		- Changed enum and repCap types names
		- All the assemblies are signed with Rohde & Schwarz signature

	Version 1.0.0.0
		- First released version
