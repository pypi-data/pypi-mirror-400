#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "duvc::core-static" for configuration "Release"
set_property(TARGET duvc::core-static APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(duvc::core-static PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/duvc-core.lib"
  )

list(APPEND _cmake_import_check_targets duvc::core-static )
list(APPEND _cmake_import_check_files_for_duvc::core-static "${_IMPORT_PREFIX}/lib/duvc-core.lib" )

# Import target "duvc::core-shared" for configuration "Release"
set_property(TARGET duvc::core-shared APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(duvc::core-shared PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/lib/duvc-core.lib"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/duvc-core.dll"
  )

list(APPEND _cmake_import_check_targets duvc::core-shared )
list(APPEND _cmake_import_check_files_for_duvc::core-shared "${_IMPORT_PREFIX}/lib/duvc-core.lib" "${_IMPORT_PREFIX}/bin/duvc-core.dll" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
