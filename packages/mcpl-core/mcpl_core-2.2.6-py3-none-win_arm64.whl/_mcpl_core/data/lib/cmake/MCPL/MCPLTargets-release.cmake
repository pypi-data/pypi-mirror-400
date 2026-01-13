#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "MCPL::mcpl" for configuration "Release"
set_property(TARGET MCPL::mcpl APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(MCPL::mcpl PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/_mcpl_core/data/lib/mcpl.lib"
  IMPORTED_LOCATION_RELEASE "C:/Users/RUNNER~1/AppData/Local/Temp/tmpy7py7c2r/wheel/scripts/mcpl.dll"
  )

list(APPEND _cmake_import_check_targets MCPL::mcpl )
list(APPEND _cmake_import_check_files_for_MCPL::mcpl "${_IMPORT_PREFIX}/_mcpl_core/data/lib/mcpl.lib" "C:/Users/RUNNER~1/AppData/Local/Temp/tmpy7py7c2r/wheel/scripts/mcpl.dll" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)

_mcpl_fixup_mcpltargets()
