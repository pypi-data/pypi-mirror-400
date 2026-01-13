#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "spw_rmap::spw_rmap" for configuration "Release"
set_property(TARGET spw_rmap::spw_rmap APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(spw_rmap::spw_rmap PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libspw_rmap.a"
  )

list(APPEND _cmake_import_check_targets spw_rmap::spw_rmap )
list(APPEND _cmake_import_check_files_for_spw_rmap::spw_rmap "${_IMPORT_PREFIX}/lib/libspw_rmap.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
