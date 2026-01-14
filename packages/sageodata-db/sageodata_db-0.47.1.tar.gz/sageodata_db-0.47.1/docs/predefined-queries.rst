.. _predefined-queries-label:

####################################
Predefined queries
####################################

.. py:currentmodule:: sageodata_db

.. autofunction:: connect
    :no-index:
.. autoclass:: SAGeodataConnection
    :members: test_alive, find_wells, find_wells_from_df, query, find_edits_by, find_additions_by, find_replacements, find_replacement_history, _predefined_query, _create_well_instances
    :exclude-members: SQL

Well summary queries
======================
.. automethod:: sageodata_db.SAGeodataConnection::wells_summary
.. automethod:: sageodata_db.SAGeodataConnection::water_wells_summary
.. automethod:: sageodata_db.SAGeodataConnection::petroleum_wells_summary
.. automethod:: sageodata_db.SAGeodataConnection::mineral_wells_summary
.. automethod:: sageodata_db.SAGeodataConnection::non_water_wells_summary

Well construction activity queries
==========================================
.. automethod:: sageodata_db.SAGeodataConnection::construction_events
.. automethod:: sageodata_db.SAGeodataConnection::drilled_intervals
.. automethod:: sageodata_db.SAGeodataConnection::casing_strings
.. automethod:: sageodata_db.SAGeodataConnection::casing_seals
.. automethod:: sageodata_db.SAGeodataConnection::production_zones
.. automethod:: sageodata_db.SAGeodataConnection::other_construction_items
.. automethod:: sageodata_db.SAGeodataConnection::gravel_packing
.. automethod:: sageodata_db.SAGeodataConnection::water_cuts
.. automethod:: sageodata_db.SAGeodataConnection::water_cuts_by_completion
.. automethod:: sageodata_db.SAGeodataConnection::well_development
.. automethod:: sageodata_db.SAGeodataConnection::well_yields
.. automethod:: sageodata_db.SAGeodataConnection::permit_details
.. automethod:: sageodata_db.SAGeodataConnection::permit_details_between_dates
.. automethod:: sageodata_db.SAGeodataConnection::permit_details_for_permit_no_range
.. automethod:: sageodata_db.SAGeodataConnection::permit_conditions_and_notes
.. automethod:: sageodata_db.SAGeodataConnection::permits_by_completed_drillholes_all
.. automethod:: sageodata_db.SAGeodataConnection::permits_by_completed_drillholes_only
.. automethod:: sageodata_db.SAGeodataConnection::drillhole_construction_by_permit_nos
.. automethod:: sageodata_db.SAGeodataConnection::licensed_driller
.. automethod:: sageodata_db.SAGeodataConnection::well_completion_reports
.. automethod:: sageodata_db.SAGeodataConnection::well_completion_reports_all
.. automethod:: sageodata_db.SAGeodataConnection::well_completion_reports_since_date

Lithological, stratigraphic, hydrostratigraphic data queries 
==========================================================================

.. automethod:: sageodata_db.SAGeodataConnection::drillhole_logs
.. automethod:: sageodata_db.SAGeodataConnection::drillers_logs
.. automethod:: sageodata_db.SAGeodataConnection::lith_logs
.. automethod:: sageodata_db.SAGeodataConnection::strat_logs
.. automethod:: sageodata_db.SAGeodataConnection::strat_logs_by_strat_unit
.. automethod:: sageodata_db.SAGeodataConnection::strat_log_teeny
.. automethod:: sageodata_db.SAGeodataConnection::hydrostrat_logs
.. automethod:: sageodata_db.SAGeodataConnection::hydrostrat_logs_by_strat_unit
.. automethod:: sageodata_db.SAGeodataConnection::hydrostrat_log_teeny
.. automethod:: sageodata_db.SAGeodataConnection::strat_unit_details
.. automethod:: sageodata_db.SAGeodataConnection::strat_unit_notes
.. automethod:: sageodata_db.SAGeodataConnection::strat_unit_by_map_symbol
.. automethod:: sageodata_db.SAGeodataConnection::strat_unit_to_aquifer_unit
.. automethod:: sageodata_db.SAGeodataConnection::all_strat_units
.. automethod:: sageodata_db.SAGeodataConnection::erroneous_hydro_subunit_descs

Aquifer queries
=================
.. automethod:: sageodata_db.SAGeodataConnection::all_aquifer_units
.. automethod:: sageodata_db.SAGeodataConnection::aquifer_units
.. automethod:: sageodata_db.SAGeodataConnection::aquifers_monitored
.. automethod:: sageodata_db.SAGeodataConnection::erroneous_aquifer_units
.. automethod:: sageodata_db.SAGeodataConnection::hydro_units

Drillhole groups (monitoring networks) queries
================================================
.. automethod:: sageodata_db.SAGeodataConnection::monitoring_networks
.. automethod:: sageodata_db.SAGeodataConnection::project_groups
.. automethod:: sageodata_db.SAGeodataConnection::group_types
.. automethod:: sageodata_db.SAGeodataConnection::group_details
.. automethod:: sageodata_db.SAGeodataConnection::wells_in_groups
.. automethod:: sageodata_db.SAGeodataConnection::drillhole_groups
.. automethod:: sageodata_db.SAGeodataConnection::wells_in_group_type
.. automethod:: sageodata_db.SAGeodataConnection::drillhole_current_monitoring_networks
.. automethod:: sageodata_db.SAGeodataConnection::drillhole_current_wl_monitoring_networks
.. automethod:: sageodata_db.SAGeodataConnection::drillhole_current_sal_monitoring_networks

Other drillhole-related queries
=================================
.. automethod:: sageodata_db.SAGeodataConnection::data_available
.. automethod:: sageodata_db.SAGeodataConnection::drillhole_notes
.. automethod:: sageodata_db.SAGeodataConnection::drillhole_status
.. automethod:: sageodata_db.SAGeodataConnection::drillhole_purpose
.. automethod:: sageodata_db.SAGeodataConnection::drillhole_document_image_list
.. automethod:: sageodata_db.SAGeodataConnection::drillhole_document_references
.. automethod:: sageodata_db.SAGeodataConnection::drillhole_image_list
.. automethod:: sageodata_db.SAGeodataConnection::drillhole_image_list_with_image_contents
.. automethod:: sageodata_db.SAGeodataConnection::drillhole_file_list
.. automethod:: sageodata_db.SAGeodataConnection::file_list_by_aquifer
.. automethod:: sageodata_db.SAGeodataConnection::elevation_surveys
.. automethod:: sageodata_db.SAGeodataConnection::site_details
.. automethod:: sageodata_db.SAGeodataConnection::rock_sample_analyses_by_drillholes

Water monitoring data queries
===============================
.. automethod:: sageodata_db.SAGeodataConnection::water_levels
.. automethod:: sageodata_db.SAGeodataConnection::water_levels_between_dates
.. automethod:: sageodata_db.SAGeodataConnection::water_levels_latest
.. automethod:: sageodata_db.SAGeodataConnection::water_levels_latest_monitoring
.. automethod:: sageodata_db.SAGeodataConnection::salinities

Water chemistry queries
========================
.. automethod:: sageodata_db.SAGeodataConnection::chem_codes
.. automethod:: sageodata_db.SAGeodataConnection::sample_analyses_by_chem_code
.. automethod:: sageodata_db.SAGeodataConnection::sample_analyses_by_drillholes
.. automethod:: sageodata_db.SAGeodataConnection::water_sample_analyses_by_drillholes
    

(NO LONGER AUTHORITATIVE) logger data queries
=============================================

.. warning:: The authoritative location for all logger data is Aquarius TS, not SA Geodata.

.. automethod:: sageodata_db.SAGeodataConnection::logger_data
.. automethod:: sageodata_db.SAGeodataConnection::logger_data_by_dh
.. automethod:: sageodata_db.SAGeodataConnection::logger_data_summary
.. automethod:: sageodata_db.SAGeodataConnection::logger_wl_data
.. automethod:: sageodata_db.SAGeodataConnection::logger_wl_data_by_dh

Geophysical log queries
=======================
.. automethod:: sageodata_db.SAGeodataConnection::geophys_log_metadata
.. automethod:: sageodata_db.SAGeodataConnection::geophys_log_metadata_by_job_no
.. automethod:: sageodata_db.SAGeodataConnection::geophys_log_metadata_by_log_hdr_no
.. automethod:: sageodata_db.SAGeodataConnection::geophys_log_metadata_by_job_no_range
.. automethod:: sageodata_db.SAGeodataConnection::geophys_log_metadata_by_location
.. automethod:: sageodata_db.SAGeodataConnection::geophys_log_metadata_by_logged_date_range
.. automethod:: sageodata_db.SAGeodataConnection::geophys_log_files
.. automethod:: sageodata_db.SAGeodataConnection::geophys_log_files_all
.. automethod:: sageodata_db.SAGeodataConnection::geophys_log_files_by_job_no
.. automethod:: sageodata_db.SAGeodataConnection::geophys_log_files_by_log_hdr_no

GAB Spring vent queries 
========================
.. automethod:: sageodata_db.SAGeodataConnection::all_mound_springs
.. automethod:: sageodata_db.SAGeodataConnection::all_mound_spring_conditions

Drillhole lists and search queries
====================================
.. automethod:: sageodata_db.SAGeodataConnection::all_drillholes
.. automethod:: sageodata_db.SAGeodataConnection::all_replacement_drillholes
.. automethod:: sageodata_db.SAGeodataConnection::drillhole_details
.. automethod:: sageodata_db.SAGeodataConnection::drillhole_details_all
.. automethod:: sageodata_db.SAGeodataConnection::drillhole_details_by_latest_permit
.. automethod:: sageodata_db.SAGeodataConnection::drillhole_details_by_lon_lat_rect
.. automethod:: sageodata_db.SAGeodataConnection::drillhole_details_by_name_search
.. automethod:: sageodata_db.SAGeodataConnection::drillhole_details_by_pwa
.. automethod:: sageodata_db.SAGeodataConnection::drillhole_details_by_pwra
.. automethod:: sageodata_db.SAGeodataConnection::drillhole_details_by_utm_rect
.. automethod:: sageodata_db.SAGeodataConnection::drillholes_all
.. automethod:: sageodata_db.SAGeodataConnection::drillholes_by_aquifer_all
.. automethod:: sageodata_db.SAGeodataConnection::drillholes_by_full_current_aquifer
.. automethod:: sageodata_db.SAGeodataConnection::drillholes_by_purpose
.. automethod:: sageodata_db.SAGeodataConnection::drillholes_by_status
.. automethod:: sageodata_db.SAGeodataConnection::drillhole_no_by_obs_no
.. automethod:: sageodata_db.SAGeodataConnection::drillhole_no_by_unit_long
.. automethod:: sageodata_db.SAGeodataConnection::drillhole_by_dh_seq_no
.. automethod:: sageodata_db.SAGeodataConnection::drillhole_by_obs_seq_no
.. automethod:: sageodata_db.SAGeodataConnection::drillhole_within_distance
.. automethod:: sageodata_db.SAGeodataConnection::replacement_drillholes_by_dh_no


Tracking changes etc to the database
=======================================
.. automethod:: sageodata_db.SAGeodataConnection::water_level_data_entry_from_year
.. automethod:: sageodata_db.SAGeodataConnection::salinity_data_entry_from_year
.. automethod:: sageodata_db.SAGeodataConnection::water_level_additions
.. automethod:: sageodata_db.SAGeodataConnection::water_level_edits
.. automethod:: sageodata_db.SAGeodataConnection::salinity_additions
.. automethod:: sageodata_db.SAGeodataConnection::salinity_edits
.. automethod:: sageodata_db.SAGeodataConnection::elevation_additions
.. automethod:: sageodata_db.SAGeodataConnection::elevation_edits
.. automethod:: sageodata_db.SAGeodataConnection::data_edits_aquifer_mon