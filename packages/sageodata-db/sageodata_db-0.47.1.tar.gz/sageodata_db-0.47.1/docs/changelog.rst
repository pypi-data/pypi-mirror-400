#####################################################################
Changelog
#####################################################################

Version 0.47 (8 January 2026)
=============================
- Add petroleum_wells_summary and mineral_wells_summary for plugin
- Expand docstring for SAGeodataConnection.find_wells
- Return SQL to predefined query method docstrings
- Move changelog to separate file in docs
- Add all predefined query methods to documentation

Version 0.46 (2 January 2026)
=============================
- Add water_wells_summary and non_water_wells_summary as faster alternatives
  to wells_summary. Otherwise identical.

Version 0.45 (23 December 2025)
===============================
- Move from cx_Oracle to oracledb following upgrade to Oracle version in September in PIRSA to DEW migration

Version 0.23 (24/11/2023)
=========================
- Fix #2 - data_available query's salinities field incorrect - was counting only water chem. 
  Now counting salinity samples as well.

Version 0.14
============
- Add pressure fields to water_levels predefined query (#3)
