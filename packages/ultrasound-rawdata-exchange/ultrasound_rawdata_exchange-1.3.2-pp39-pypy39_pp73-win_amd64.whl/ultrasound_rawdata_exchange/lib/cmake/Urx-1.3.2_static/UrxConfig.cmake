
####### Expanded from @PACKAGE_INIT@ by configure_package_config_file() #######
####### Any changes to this file will be overwritten by the next CMake run ####
####### The input file was UrxConfig.cmake.in                            ########

get_filename_component(PACKAGE_PREFIX_DIR "${CMAKE_CURRENT_LIST_DIR}/D:/CI/builds/common/sw/urx/build/lib.win-amd64-pypy39/ultrasound_rawdata_exchange" ABSOLUTE)

macro(set_and_check _var _file)
  set(${_var} "${_file}")
  if(NOT EXISTS "${_file}")
    message(FATAL_ERROR "File or directory ${_file} referenced by variable ${_var} does not exist !")
  endif()
endmacro()

macro(check_required_components _NAME)
  foreach(comp ${${_NAME}_FIND_COMPONENTS})
    if(NOT ${_NAME}_${comp}_FOUND)
      if(${_NAME}_FIND_REQUIRED_${comp})
        set(${_NAME}_FOUND FALSE)
      endif()
    endif()
  endforeach()
endmacro()

####################################################################################

include(CMakeFindDependencyMacro)

if(ON AND NOT (NOT OFF AND OFF))

  if(NOT HDF5_DIR)
    set(HDF5_DIR "D:/CI/builds/common/sw/urx/build/temp.win-amd64-pypy39/Release_ultrasound-rawdata-exchange/vcpkg_installed/x64-wssrep/share/hdf5")
  endif()
  if(NOT "${HDF5_DIR}" STREQUAL "")
    find_dependency(
      HDF5
      NAMES
      hdf5
      COMPONENTS
      CXX
      static
      CONFIG
      NO_DEFAULT_PATH
      REQUIRED)
  endif()

endif()

set(WITH_PYTHON "ON")
if(WITH_PYTHON)
  find_dependency(Python3 COMPONENTS Interpreter Development.Module REQUIRED)
  find_dependency(pybind11 2.11 CONFIG REQUIRED)
endif()

set(URX_PYTHON_TEST_PATH
    "D:/CI/builds/common/sw/urx/build/lib.win-amd64-pypy39/ultrasound_rawdata_exchange/share/Urx-1.3.2_static/python")
set(URX_MATLAB_INSTALL_DATADIR
    "D:/CI/builds/common/sw/urx/build/lib.win-amd64-pypy39/ultrasound_rawdata_exchange/share/Urx-1.3.2_static/matlab")

include("${CMAKE_CURRENT_LIST_DIR}/UrxTargets.cmake")

check_required_components(Urx UrxUtils)
