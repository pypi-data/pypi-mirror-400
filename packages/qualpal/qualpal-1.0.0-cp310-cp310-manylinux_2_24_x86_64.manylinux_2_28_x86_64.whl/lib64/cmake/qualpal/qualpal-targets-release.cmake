#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "qualpal::qualpal" for configuration "Release"
set_property(TARGET qualpal::qualpal APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(qualpal::qualpal PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib64/libqualpal.a"
  )

list(APPEND _cmake_import_check_targets qualpal::qualpal )
list(APPEND _cmake_import_check_files_for_qualpal::qualpal "${_IMPORT_PREFIX}/lib64/libqualpal.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
