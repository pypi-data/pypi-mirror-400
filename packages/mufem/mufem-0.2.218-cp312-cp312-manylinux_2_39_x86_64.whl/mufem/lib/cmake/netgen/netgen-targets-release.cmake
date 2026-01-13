#----------------------------------------------------------------
# Generated CMake target import file for configuration "RELEASE".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "ngcore" for configuration "RELEASE"
set_property(TARGET ngcore APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(ngcore PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libngcore.so"
  IMPORTED_SONAME_RELEASE "libngcore.so"
  )

list(APPEND _cmake_import_check_targets ngcore )
list(APPEND _cmake_import_check_files_for_ngcore "${_IMPORT_PREFIX}/lib/libngcore.so" )

# Import target "nglib" for configuration "RELEASE"
set_property(TARGET nglib APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(nglib PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libnglib.so"
  IMPORTED_SONAME_RELEASE "libnglib.so"
  )

list(APPEND _cmake_import_check_targets nglib )
list(APPEND _cmake_import_check_files_for_nglib "${_IMPORT_PREFIX}/lib/libnglib.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
