#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "Urx::UrxBindingsPython" for configuration "Release"
set_property(TARGET Urx::UrxBindingsPython APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(Urx::UrxBindingsPython PROPERTIES
  IMPORTED_COMMON_LANGUAGE_RUNTIME_RELEASE ""
  IMPORTED_LOCATION_RELEASE "/builds/common/sw/urx/build/lib.linux-x86_64-pypy311/ultrasound_rawdata_exchange/bindings.pypy311-pp73-x86_64-linux-gnu.so"
  IMPORTED_NO_SONAME_RELEASE "TRUE"
  )

list(APPEND _cmake_import_check_targets Urx::UrxBindingsPython )
list(APPEND _cmake_import_check_files_for_Urx::UrxBindingsPython "/builds/common/sw/urx/build/lib.linux-x86_64-pypy311/ultrasound_rawdata_exchange/bindings.pypy311-pp73-x86_64-linux-gnu.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
