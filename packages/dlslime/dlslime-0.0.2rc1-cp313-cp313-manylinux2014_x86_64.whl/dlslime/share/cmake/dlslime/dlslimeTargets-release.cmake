#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "dlslime::_slime_device" for configuration "Release"
set_property(TARGET dlslime::_slime_device APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(dlslime::_slime_device PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/dlslime/lib_slime_device.so"
  IMPORTED_SONAME_RELEASE "lib_slime_device.so"
  )

list(APPEND _cmake_import_check_targets dlslime::_slime_device )
list(APPEND _cmake_import_check_files_for_dlslime::_slime_device "${_IMPORT_PREFIX}/dlslime/lib_slime_device.so" )

# Import target "dlslime::_slime_engine" for configuration "Release"
set_property(TARGET dlslime::_slime_engine APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(dlslime::_slime_engine PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/dlslime/lib_slime_engine.so"
  IMPORTED_SONAME_RELEASE "lib_slime_engine.so"
  )

list(APPEND _cmake_import_check_targets dlslime::_slime_engine )
list(APPEND _cmake_import_check_files_for_dlslime::_slime_engine "${_IMPORT_PREFIX}/dlslime/lib_slime_engine.so" )

# Import target "dlslime::_slime_rdma" for configuration "Release"
set_property(TARGET dlslime::_slime_rdma APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(dlslime::_slime_rdma PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/dlslime/lib_slime_rdma.so"
  IMPORTED_SONAME_RELEASE "lib_slime_rdma.so"
  )

list(APPEND _cmake_import_check_targets dlslime::_slime_rdma )
list(APPEND _cmake_import_check_files_for_dlslime::_slime_rdma "${_IMPORT_PREFIX}/dlslime/lib_slime_rdma.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
