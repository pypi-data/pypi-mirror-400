#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "Urx::UrxBindingsPython" for configuration "Release"
set_property(TARGET Urx::UrxBindingsPython APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(Urx::UrxBindingsPython PROPERTIES
  IMPORTED_COMMON_LANGUAGE_RUNTIME_RELEASE ""
  IMPORTED_LOCATION_RELEASE "D:/CI/builds/common/sw/urx/build/lib.win-amd64-cpython-39/ultrasound_rawdata_exchange/bindings.cp39-win_amd64.pyd"
  )

list(APPEND _cmake_import_check_targets Urx::UrxBindingsPython )
list(APPEND _cmake_import_check_files_for_Urx::UrxBindingsPython "D:/CI/builds/common/sw/urx/build/lib.win-amd64-cpython-39/ultrasound_rawdata_exchange/bindings.cp39-win_amd64.pyd" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
